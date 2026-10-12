"""Smoke test the `autolab` CLI the way an agent drives it: init a lab folder,
run code, notebook and SQL for real, build and edit records. Every command must
print one JSON object; exit codes must mean what the guide says.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import json
import shutil
import subprocess
import tempfile

from docx import Document

from autolab.docxedit import iter_all_paragraphs


def autolab(*args, cwd, expect=0):
    proc = subprocess.run([sys.executable, "-m", "autolab", *map(str, args)], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8")
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise SystemExit(f"FAIL: not JSON from {args}:\n{proc.stdout}\n{proc.stderr}")
    if proc.returncode != expect:
        raise SystemExit(f"FAIL: {args} exited {proc.returncode}, wanted {expect}:\n{proc.stdout}")
    return out


def check(label, cond, detail=""):
    print(f"  {'ok ' if cond else 'FAIL'} {label}")
    if not cond:
        raise SystemExit(f"FAIL: {label} {detail}")


def text_of(path) -> str:
    return "\n".join(p.text for p in iter_all_paragraphs(Document(str(path))))


def main() -> None:
    w = Path(tempfile.mkdtemp(prefix="autolab_cli_"))
    try:
        r = autolab("init", ".", "--subject", "CN", "--register-number", "URK00XX0000", cwd=w)
        check("init", (w / "AGENTS.md").exists() and (w / "CN" / "output").is_dir()
              and json.loads((w / "autolab.json").read_text())["register_number"] == "URK00XX0000")
        check("CLAUDE.md imports AGENTS.md", (w / "CLAUDE.md").read_text().strip() == "@AGENTS.md")

        ex = w / "CN" / "output" / "Ex1"; ex.mkdir(parents=True)
        (ex / "q1.py").write_text("n = int(input())\nprint('square', n * n)\n")
        (ex / "in.txt").write_text("7\n")
        r = autolab("run", ex / "q1.py", "--stdin", ex / "in.txt", "--shot", ex / "q1.png",
                    "--code-shot", ex / "q1_code.png", "--urk", "URK00XX0000", cwd=w)
        check("run ok + real output", r["ok"] and "square 49" in r["output"], r)
        check("run shots written", Path(r["shot"]).stat().st_size > 1000 and Path(r["code_shot"]).exists())

        (ex / "bad.py").write_text("print(1/0)\n")
        r = autolab("run", ex / "bad.py", "--shot", ex / "bad.png", cwd=w, expect=1)
        check("failing run -> exit 1, no shot", not r["ok"] and "ZeroDivisionError" in r["output"]
              and "shot" not in r and not (ex / "bad.png").exists())

        (ex / "q2.c").write_text('#include <stdio.h>\nint main(){printf("hi from c\\n");return 0;}\n')
        r = autolab("run", ex / "q2.c", "--shot", ex / "q2.png", cwd=w)
        check("C compiles and runs", r["ok"] and "hi from c" in r["output"], r)

        (ex / "server.py").write_text(
            "import socket\ns=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)\n"
            "s.bind(('127.0.0.1',50917));s.listen(1);print('listening',flush=True)\n"
            "c,_=s.accept();d=c.recv(64);print('got',d.decode(),flush=True);c.send(d.upper());c.close()\n")
        (ex / "client.py").write_text(
            "import socket\nc=socket.socket();c.connect(('127.0.0.1',50917));c.send(b'ping')\n"
            "print('reply',c.recv(64).decode());c.close()\n")
        r = autolab("run-pair", ex / "server.py", ex / "client.py", "--shot-server", ex / "s.png",
                    "--shot-client", ex / "c.png", cwd=w)
        check("run-pair", r["ok"] and "reply PING" in r["client"]["output"]
              and "got ping" in r["server"]["output"], r)

        (ex / "nb.py").write_text("# %% [markdown]\n# ## Squares\n# %%\nxs = [i * i for i in range(5)]\n"
                                  "print(xs)\n# %%\nsum(xs)\n")
        r = autolab("notebook", ex / "nb.py", "--out", ex / "nb.ipynb", "--shots", ex / "nbshots",
                    "--prefix", 'print("URK00XX0000")', cwd=w)
        nb = json.loads((ex / "nb.ipynb").read_text())
        check("notebook runs cells", r["ok"] and len(nb["cells"]) == 3
              and nb["cells"][2]["outputs"][-1]["data"]["text/plain"] == ["30"], r)
        check("notebook shots", (ex / "nbshots" / "cell01_out.png").exists())
        (ex / "nbbad.py").write_text("# %%\nx = 1\n# %%\nraise ValueError('boom')\n# %%\nprint('never')\n")
        r = autolab("notebook", ex / "nbbad.py", "--out", ex / "nbbad.ipynb", cwd=w, expect=1)
        check("notebook stops at error", not r["ok"] and "boom" in r["error"] and len(r["cells"]) == 2)

        if shutil.which("sqlite3"):
            (ex / "q.sql").write_text("-- @q 1\nCREATE TABLE t (id INT,\n  name TEXT);\n"
                                      "INSERT INTO t VALUES (1, 'a'), (2, 'b');\n"
                                      "-- @q 2\nSELECT * FROM t;\n")
            r = autolab("sql", ex / "q.sql", "--engine", "sqlite", "--db", ex / "lab.db",
                        "--shots", ex / "sqlshots", "--transcript", ex / "t.txt", cwd=w)
            check("sql (sqlite)", r["ok"] and len(r["questions"]) == 2
                  and "b" in r["questions"][1]["output"] and Path(r["questions"][1]["shot"]).exists(), r)
            (ex / "badq.sql").write_text("SELECT * FROM nope;\n")
            r = autolab("sql", ex / "badq.sql", "--engine", "sqlite", "--db", ex / "lab.db", cwd=w, expect=1)
            check("sql error -> exit 1", not r["ok"] and r["questions"][0]["errors"])
        else:
            print("  skip sql (no sqlite3)")

        spec = {"course": "CN Lab", "register_number": "URK00XX0000", "ex_no": "1",
                "title": "Sockets", "date": "12/10/2026", "aim": "To do sockets.",
                "description": "About sockets.",
                "questions": [{"number": "1", "text": "Square a number", "code_file": "q1.py",
                               "images": ["q1.png"]},
                              {"number": "2", "text": "Echo", "code": "print('x')", "images": ["c.png"]}],
                "result": "Done."}
        (ex / "spec.json").write_text(json.dumps(spec))
        rec = w / "CN" / "records" / "Ex1" / "Ex1.docx"
        r = autolab("record", "new", ex / "spec.json", "--out", rec, cwd=w)
        t = text_of(rec)
        check("record new", r["ok"] and r["images"] == 2 and "Square a number" in t
              and "URK00XX0000" in t and "n * n" in t, r)

        r = autolab("record", "add", rec, "--title", "Extra", "--number", "3",
                    "--code-file", ex / "q2.c", "--image", ex / "q2.png", cwd=w)
        check("record add", r["ok"] and "Extra" in text_of(rec) and "hi from c" in text_of(rec))

        r = autolab("replace", rec, "--find", "URK00XX0000", "--replace", "URK11YY1111", cwd=w)
        check("replace", r["replacements"] >= 1 and "URK11YY1111" in text_of(rec))

        r = autolab("blocks", rec, cwd=w)
        target = next(b for b in r["blocks"] if b["text"] == "To do sockets.")
        (ex / "edits.json").write_text(json.dumps({target["id"]: "To learn sockets."}))
        r = autolab("edit", rec, "--edits", ex / "edits.json", cwd=w)
        check("blocks + edit", r["ok"] and "To learn sockets." in text_of(rec), r)

        r = autolab("run", ex / "missing.py", cwd=w, expect=2)
        check("missing file -> exit 2", not r["ok"] and "no such file" in r["error"])

        r = autolab("skill", "--dir", w / "skills", cwd=w)
        skill = Path(r["installed"]).read_text()
        check("skill installs with frontmatter", skill.startswith("---\nname: autolab\n"))
        print("PASS")
    finally:
        shutil.rmtree(w, ignore_errors=True)


if __name__ == "__main__":
    main()
