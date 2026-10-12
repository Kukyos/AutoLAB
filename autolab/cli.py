"""`autolab` command line: every subcommand prints one JSON object on stdout.

Built for AI coding agents (Claude Code, Codex, ...) as much as for people.
Exit codes: 0 ok, 1 the program/SQL ran but failed, 2 usage or missing tool.
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import sys
from importlib import resources
from pathlib import Path

from . import __version__

EXT_LANG = {".py": "python", ".c": "c", ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".java": "java"}
DEFAULT_CWD = r"C:\Users\{urk}\Desktop\Lab"


class UsageError(Exception):
    pass


def _emit(obj: dict, code: int = 0) -> int:
    sys.stdout.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
    return code


def _read(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        raise UsageError(f"no such file: {path}")
    return p.read_text(encoding="utf-8")


def _lang(path: str, given: str | None) -> str:
    if given:
        return given
    lang = EXT_LANG.get(Path(path).suffix.lower())
    if not lang:
        raise UsageError(f"can't tell the language of {path}; pass --lang")
    return lang


def _write(path: str, data: bytes) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return str(p)


def _guide() -> str:
    return resources.files("autolab").joinpath("agent/GUIDE.md").read_text(encoding="utf-8")


# ---- commands ------------------------------------------------------------

def cmd_doctor(a) -> int:
    from .runner import tool_status
    from .sql import find_psql
    return _emit({
        "version": __version__,
        "languages": tool_status(),
        "sql": {"psql": bool(find_psql()), "sqlite": bool(shutil.which("sqlite3"))},
        "python_for_notebooks": sys.executable,
    })


def _terminal_shot(output: str, command: str, a) -> bytes:
    from .labshot import render_terminal_shot
    return render_terminal_shot(output, command=command, cwd=a.cwd, style=a.style,
                                urk=a.urk or "", urk_mode=a.urk_mode if a.urk else "none")


def cmd_run(a) -> int:
    from .runner import run_single
    code = _read(a.file)
    lang = _lang(a.file, a.lang)
    stdin = _read(a.stdin) if a.stdin else ""
    res = run_single(code, language=lang, stdin_text=stdin, timeout=a.timeout,
                     filename=Path(a.file).name)
    out = {"ok": res.ok, "stage": res.stage, "exit_code": res.exit_code,
           "timed_out": res.timed_out, "command": res.command, "output": res.output}
    if a.shot and res.ok:  # never render a failed run into a screenshot
        out["shot"] = _write(a.shot, _terminal_shot(res.output, a.command or res.command, a))
    if a.code_shot:
        from .labshot import render_code_shot
        out["code_shot"] = _write(a.code_shot, render_code_shot(code, language=lang,
                                                                filename=Path(a.file).name))
    return _emit(out, 0 if res.ok else 1)


def cmd_run_pair(a) -> int:
    from .runner import run_pair
    lang = _lang(a.server, a.lang)
    stdin = _read(a.stdin) if a.stdin else ""
    srv, cli = run_pair(_read(a.server), _read(a.client), language=lang, client_stdin=stdin,
                        client_timeout=a.timeout, server_filename=Path(a.server).name,
                        client_filename=Path(a.client).name)
    out = {"ok": srv.stage != "compile" and cli.ok,
           "server": {"output": srv.output, "command": srv.command, "stage": srv.stage},
           "client": {"output": cli.output, "command": cli.command, "stage": cli.stage,
                      "exit_code": cli.exit_code, "timed_out": cli.timed_out}}
    if out["ok"]:
        if a.shot_server:
            out["shot_server"] = _write(a.shot_server, _terminal_shot(srv.output, srv.command, a))
        if a.shot_client:
            out["shot_client"] = _write(a.shot_client, _terminal_shot(cli.output, cli.command, a))
    return _emit(out, 0 if out["ok"] else 1)


def cmd_shot(a) -> int:
    from . import labshot
    if a.kind == "code":
        png = labshot.render_code_shot(_read(a.file), language=_lang(a.file, a.lang),
                                       filename=Path(a.file).name)
    else:
        text = _read(a.text_file) if a.text_file else sys.stdin.read()
        if a.kind == "console":
            png = labshot.render_console_text(text, title=a.title or "Command Prompt")
        else:
            png = _terminal_shot(text.rstrip("\n"), a.command, a)
    return _emit({"ok": True, "out": _write(a.out, png)})


def cmd_notebook(a) -> int:
    from .notebook import run_notebook
    src = Path(a.file)
    if not src.is_file():
        raise UsageError(f"no such file: {a.file}")
    res = run_notebook(src, Path(a.out), prefix=a.prefix or "",
                       shots_dir=Path(a.shots) if a.shots else None,
                       shot_command=a.command or "")
    return _emit(res, 0 if res["ok"] else 1)


def cmd_sql(a) -> int:
    from .sql import run_sql_file
    src = Path(a.file)
    if not src.is_file():
        raise UsageError(f"no such file: {a.file}")
    try:
        res = run_sql_file(src, engine=a.engine, db=a.db, user=a.user, host=a.host,
                           shots_dir=Path(a.shots) if a.shots else None, title=a.title)
    except FileNotFoundError as e:
        raise UsageError(str(e)) from e
    if a.transcript:
        Path(a.transcript).write_text(res["transcript"] + "\n", encoding="utf-8")
        res["transcript_file"] = a.transcript
    return _emit(res, 0 if res["ok"] else 1)


def cmd_record_new(a) -> int:
    from .record import build_record
    spec_path = Path(a.spec)
    spec = json.loads(_read(a.spec))
    for k in ("title", "questions"):
        if k not in spec:
            raise UsageError(f"spec is missing '{k}'")
    try:
        return _emit({"ok": True, **build_record(spec, Path(a.out), spec_path.parent)})
    except FileNotFoundError as e:
        raise UsageError(f"spec refers to a missing file: {e.filename}") from e


def cmd_record_add(a) -> int:
    from docx import Document
    from .assemble import add_solved_question
    doc = Document(a.docx)
    images = [Path(p).read_bytes() for p in a.image]
    add_solved_question(doc, number=a.number, title=a.title, description=a.description,
                        code=_read(a.code_file) if a.code_file else "", images=images,
                        image_width_in=a.image_width)
    out = a.out or a.docx
    doc.save(out)
    return _emit({"ok": True, "out": out, "images": len(images)})


def cmd_replace(a) -> int:
    from .docxedit import replace_in_docx
    out = a.out or a.docx
    n = replace_in_docx(a.docx, out, a.find, a.replace)
    return _emit({"ok": True, "out": out, "replacements": n})


def cmd_blocks(a) -> int:
    from docx import Document
    from .docxedit import extract_blocks
    blocks = extract_blocks(Document(a.docx))
    return _emit({"blocks": [{k: b[k] for k in ("id", "kind", "style", "text") if k in b}
                             for b in blocks]})


def cmd_edit(a) -> int:
    from .docxedit import apply_block_edits_bytes
    edits = json.loads(_read(a.edits))
    data, n = apply_block_edits_bytes(Path(a.docx).read_bytes(), edits)
    out = a.out or a.docx
    Path(out).write_bytes(data)
    return _emit({"ok": n == len(edits), "out": out, "applied": n, "requested": len(edits)})


def cmd_pdf_spans(a) -> int:
    import pymupdf
    from .pdfedit import read_spans
    return _emit({"spans": [s.as_dict() for s in read_spans(pymupdf.open(a.pdf))]})


def cmd_pdf_edit(a) -> int:
    import pymupdf
    from .pdfedit import apply_edits
    doc = pymupdf.open(a.pdf)
    report = apply_edits(doc, json.loads(_read(a.edits)))
    doc.save(a.out, garbage=3, deflate=True)
    return _emit({"ok": True, "out": a.out, "report": report})


def cmd_init(a) -> int:
    root = Path(a.dir)
    root.mkdir(parents=True, exist_ok=True)
    made = []
    cfg = root / "autolab.json"
    if not cfg.exists():
        cfg.write_text(json.dumps({
            "register_number": a.register_number or "", "name": a.name or "",
            "courses": {s: "" for s in a.subject},
        }, indent=2) + "\n", encoding="utf-8")
        made.append(str(cfg))
    for subj in a.subject:
        for d in ("materials", "output", "records", "scripts"):
            (root / subj / d).mkdir(parents=True, exist_ok=True)
        notes = root / subj / "NOTES.md"
        if not notes.exists():
            notes.write_text(f"# {subj}\n\nConventions for this subject: template quirks, "
                             "what the teacher asked for, anything learned the hard way.\n",
                             encoding="utf-8")
            made.append(str(notes))
    agents = root / "AGENTS.md"
    if not agents.exists() or a.force:
        agents.write_text(_guide(), encoding="utf-8")
        made.append(str(agents))
    claude = root / "CLAUDE.md"
    if not claude.exists():
        claude.write_text("@AGENTS.md\n", encoding="utf-8")  # Claude Code imports it
        made.append(str(claude))
    return _emit({"ok": True, "dir": str(root), "created": made})


def cmd_skill(a) -> int:
    body = ("---\nname: autolab\ndescription: Make college lab records with the autolab CLI. "
            "Run code/notebooks/SQL for real, render terminal and VS Code screenshots from the "
            "real output, and assemble or edit the record .docx/.pdf. Use for lab records, "
            "lab exercises, experiment write-ups and output screenshots.\n---\n\n" + _guide())
    if a.print:
        sys.stdout.write(body)
        return 0
    dest = Path(a.dir).expanduser() / "autolab" / "SKILL.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(body, encoding="utf-8")
    return _emit({"ok": True, "installed": str(dest),
                  "undo": f"rm -r {dest.parent}"})


def cmd_guide(a) -> int:
    sys.stdout.write(_guide())
    return 0


def cmd_app(a) -> int:
    try:
        import webview  # noqa: F401
    except ImportError:
        raise UsageError("the desktop window needs pywebview: install with  autolab[desktop]  "
                         "or use  autolab serve  and open the browser")
    from .desktop import main as desktop_main
    return desktop_main()


def cmd_serve(a) -> int:
    import uvicorn
    from .server import app
    uvicorn.run(app, host=a.host, port=a.port, log_level="warning")
    return 0


# ---- parser --------------------------------------------------------------

def _shot_opts(p) -> None:
    p.add_argument("--urk", help="register number to show in the screenshot")
    p.add_argument("--urk-mode", default="line", choices=["line", "title", "prompt", "none"])
    p.add_argument("--style", default="cmd", choices=["cmd", "powershell"])
    p.add_argument("--cwd", default=DEFAULT_CWD, help="prompt path shown in the terminal")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="autolab", description=__doc__.splitlines()[0])
    ap.add_argument("--version", action="version", version=f"autolab {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True, metavar="command")

    p = sub.add_parser("doctor", help="which languages and tools are installed")
    p.set_defaults(fn=cmd_doctor)

    p = sub.add_parser("run", help="compile + run one program, optionally screenshot it")
    p.add_argument("file"); p.add_argument("--lang", choices=list(dict.fromkeys(EXT_LANG.values())))
    p.add_argument("--stdin", help="file whose contents are typed into the program")
    p.add_argument("--timeout", type=float, default=15.0)
    p.add_argument("--shot", help="write a terminal screenshot of the output here")
    p.add_argument("--code-shot", help="write a VS Code screenshot of the source here")
    p.add_argument("--command", help="command line shown in the screenshot")
    _shot_opts(p); p.set_defaults(fn=cmd_run)

    p = sub.add_parser("run-pair", help="server + client programs (socket labs)")
    p.add_argument("server"); p.add_argument("client")
    p.add_argument("--lang", choices=list(dict.fromkeys(EXT_LANG.values())))
    p.add_argument("--stdin", help="typed into the client")
    p.add_argument("--timeout", type=float, default=15.0)
    p.add_argument("--shot-server"); p.add_argument("--shot-client")
    _shot_opts(p); p.set_defaults(fn=cmd_run_pair)

    p = sub.add_parser("shot", help="render a screenshot from text or source")
    p.add_argument("kind", choices=["terminal", "console", "code"])
    p.add_argument("file", nargs="?", help="source file (code)")
    p.add_argument("--text-file", help="text to show (terminal/console); default stdin")
    p.add_argument("--command", default="python main.py", help="terminal: command shown")
    p.add_argument("--title", help="console: window title")
    p.add_argument("--lang"); p.add_argument("--out", required=True)
    _shot_opts(p); p.set_defaults(fn=cmd_shot)

    p = sub.add_parser("notebook", help="run a '# %%' script into an .ipynb with outputs")
    p.add_argument("file"); p.add_argument("--out", required=True)
    p.add_argument("--shots", help="folder for per-cell output/figure PNGs")
    p.add_argument("--prefix", help="line prepended to every code cell")
    p.add_argument("--command", help="command shown in the cell screenshots")
    p.set_defaults(fn=cmd_notebook)

    p = sub.add_parser("sql", help="run a .sql file through psql/sqlite3, screenshot each question")
    p.add_argument("file"); p.add_argument("--engine", required=True, choices=["psql", "sqlite"])
    p.add_argument("--db", required=True, help="database name (psql) or file (sqlite)")
    p.add_argument("--user", default="postgres"); p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--shots"); p.add_argument("--transcript"); p.add_argument("--title")
    p.set_defaults(fn=cmd_sql)

    rec = sub.add_parser("record", help="build or extend a record .docx")
    rsub = rec.add_subparsers(dest="rcmd", required=True, metavar="action")
    p = rsub.add_parser("new", help="build from a JSON spec"); p.add_argument("spec")
    p.add_argument("--out", required=True); p.set_defaults(fn=cmd_record_new)
    p = rsub.add_parser("add", help="append a solved question to an existing docx")
    p.add_argument("docx"); p.add_argument("--out", help="default: edit in place")
    p.add_argument("--title", required=True); p.add_argument("--number", default="")
    p.add_argument("--description", default=""); p.add_argument("--code-file")
    p.add_argument("--image", action="append", default=[])
    p.add_argument("--image-width", type=float, default=6.0, help="inches")
    p.set_defaults(fn=cmd_record_add)

    p = sub.add_parser("replace", help="find & replace across a docx (body, tables, headers)")
    p.add_argument("docx"); p.add_argument("--find", required=True)
    p.add_argument("--replace", required=True); p.add_argument("--out")
    p.set_defaults(fn=cmd_replace)

    p = sub.add_parser("blocks", help="list a docx's editable text blocks")
    p.add_argument("docx"); p.set_defaults(fn=cmd_blocks)
    p = sub.add_parser("edit", help="apply {block id: text} edits to a docx")
    p.add_argument("docx"); p.add_argument("--edits", required=True); p.add_argument("--out")
    p.set_defaults(fn=cmd_edit)

    pdf = sub.add_parser("pdf", help="edit PDF text in place")
    psub = pdf.add_subparsers(dest="pcmd", required=True, metavar="action")
    p = psub.add_parser("spans"); p.add_argument("pdf"); p.set_defaults(fn=cmd_pdf_spans)
    p = psub.add_parser("edit"); p.add_argument("pdf"); p.add_argument("--edits", required=True)
    p.add_argument("--out", required=True); p.set_defaults(fn=cmd_pdf_edit)

    p = sub.add_parser("init", help="set up a lab folder (layout + AGENTS.md for agents)")
    p.add_argument("dir", nargs="?", default=".")
    p.add_argument("--subject", action="append", default=[], help="repeatable, e.g. DBMS")
    p.add_argument("--register-number"); p.add_argument("--name")
    p.add_argument("--force", action="store_true", help="overwrite AGENTS.md with the latest guide")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("skill", help="install the Claude Code skill (~/.claude/skills/autolab)")
    p.add_argument("--dir", default="~/.claude/skills")
    p.add_argument("--print", action="store_true", help="print SKILL.md instead of installing")
    p.set_defaults(fn=cmd_skill)

    p = sub.add_parser("guide", help="print the agent guide"); p.set_defaults(fn=cmd_guide)
    p = sub.add_parser("app", help="open the desktop app"); p.set_defaults(fn=cmd_app)
    p = sub.add_parser("serve", help="run the web UI")
    p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8000)
    p.set_defaults(fn=cmd_serve)
    return ap


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    a = build_parser().parse_args(argv)
    try:
        return a.fn(a)
    except UsageError as e:
        return _emit({"ok": False, "error": str(e)}, 2)
    except Exception as e:  # MissingTool and friends: say what, don't dump a traceback
        from .runner import MissingTool
        code = 2 if isinstance(e, (MissingTool, FileNotFoundError)) else 1
        return _emit({"ok": False, "error": f"{type(e).__name__}: {e}"}, code)
