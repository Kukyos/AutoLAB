"""Run SQL for real through psql or sqlite3 and render the console transcript.

Input is a .sql file. Lines like `-- @q 3` start question 3; everything up to
the next marker belongs to it (no markers = one question). Each statement ends
with `;` at the end of a line; psql backslash commands and sqlite dot commands
are one line each. Other `--` comment lines are dropped.

Every statement is run as its own client invocation (`psql -c` /
`sqlite3 db stmt`), exactly as captured in real submissions. The database
persists between statements; session state (an open BEGIN, `\\set`) does not.

psql connection: --db/--user/--host, password from the PGPASSWORD env var.
"""

from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
from pathlib import Path

from .labshot import render_console_text

_Q = re.compile(r"^--\s*@q\s*(\S+)\s*$")
ENGINES = ("psql", "sqlite")


def split_questions(text: str) -> list[tuple[str, list[str]]]:
    """[(question id, [statement, ...])]."""
    questions: list[tuple[str, list[str]]] = []
    qid, stmts, cur = "1", [], []

    def flush_q():
        nonlocal stmts
        if stmts:
            questions.append((qid, stmts))
        stmts = []

    for line in text.splitlines():
        m = _Q.match(line.strip())
        if m:
            if cur:
                stmts.append("\n".join(cur)); cur = []
            flush_q()
            qid = m.group(1)
            continue
        s = line.strip()
        if not cur and (not s or s.startswith("--")):
            continue
        if not cur and s[:1] in ("\\", "."):
            stmts.append(s)
            continue
        cur.append(line.rstrip())
        if s.endswith(";"):
            stmts.append("\n".join(cur)); cur = []
    if cur:
        stmts.append("\n".join(cur))
    flush_q()
    return questions


def find_psql() -> str | None:
    p = shutil.which("psql")
    if p:
        return p
    hits = sorted(glob.glob(r"C:\Program Files\PostgreSQL\*\bin\psql.exe"))
    return hits[-1] if hits else None


class SqlRunner:
    def __init__(self, engine: str, db: str, user: str = "postgres", host: str = "127.0.0.1"):
        if engine not in ENGINES:
            raise ValueError(f"engine must be one of {ENGINES}")
        self.engine, self.db, self.user, self.host = engine, db, user, host
        if engine == "psql":
            self.exe = find_psql()
            if not self.exe:
                raise FileNotFoundError("psql not found. Install PostgreSQL and add its bin folder to PATH.")
            self.prompt = f"{db}=#"
        else:
            self.exe = shutil.which("sqlite3")
            if not self.exe:
                raise FileNotFoundError("sqlite3 not found. Install the SQLite command-line shell (sqlite.org/download.html).")
            self.prompt = "sqlite>"

    def run(self, stmt: str) -> str:
        if self.engine == "psql":
            argv = [self.exe, "-U", self.user, "-h", self.host, "-d", self.db, "-c", stmt]
        else:
            argv = [self.exe, "-header", "-table", self.db, stmt]  # ASCII: safe in any font
        r = subprocess.run(argv, capture_output=True, text=True, env=os.environ.copy(), timeout=60)
        return (r.stdout + r.stderr).rstrip()

    def echo(self, stmt: str) -> list[str]:
        """The statement as it looks typed at the interactive prompt."""
        lines = stmt.strip("\n").split("\n")
        out = [f"{self.prompt} {lines[0]}"]
        depth = lines[0].count("(") - lines[0].count(")")
        for l in lines[1:]:
            if self.engine == "psql":
                out.append(f"{self.db}{'(' if depth > 0 else '-'}# {l}")
            else:
                out.append(f"   ...> {l}")
            depth += l.count("(") - l.count(")")
        return out


def code_text(stmts: list[str]) -> str:
    """The statements as they belong in the record (not a transcript)."""
    return "\n".join(stmts)


def run_sql_file(path: Path, *, engine: str, db: str, user: str = "postgres",
                 host: str = "127.0.0.1", shots_dir: Path | None = None,
                 title: str | None = None) -> dict:
    runner = SqlRunner(engine, db, user, host)
    questions = split_questions(path.read_text(encoding="utf-8"))
    if shots_dir:
        shots_dir.mkdir(parents=True, exist_ok=True)
    win_title = title or (f"psql — {db}" if engine == "psql" else f"sqlite3 — {Path(db).name}")
    results, full = [], []
    for qid, stmts in questions:
        transcript, outputs, errors = [], [], []
        for s in stmts:
            out = runner.run(s)
            outputs.append(out)
            if re.search(r"^(ERROR|Error|Parse error|Runtime error)", out, re.M):
                errors.append({"statement": s, "output": out})
            transcript += runner.echo(s)
            if out:
                transcript += out.split("\n")
            transcript.append("")
        transcript.append(runner.prompt)
        text = "\n".join(transcript)
        full.append(text)
        entry = {"question": qid, "code": code_text(stmts), "output": "\n".join(outputs),
                 "errors": errors}
        if shots_dir:
            shot = shots_dir / f"q{qid}.png"
            shot.write_bytes(render_console_text(text, title=win_title))
            entry["shot"] = str(shot)
        results.append(entry)
    return {"ok": not any(r["errors"] for r in results), "engine": engine,
            "questions": results, "transcript": "\n\n".join(full)}
