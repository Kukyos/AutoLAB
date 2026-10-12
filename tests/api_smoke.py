"""Smoke test the HTTP API end to end, in desktop mode, against a real server.

Starts uvicorn in-process on a free port with a throwaway profile directory
(APPDATA is pointed at a temp dir so your real profile is never touched), then
drives the endpoints the UI uses with the bundled template_empty.docx.
"""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import io
import json
import os
import socket
import threading
import time
import urllib.error
import urllib.request
import uuid

os.environ["APPDATA"] = tempfile.mkdtemp(prefix="autolab_test_")
os.environ["AUTOLAB_DESKTOP"] = "1"
os.environ.pop("GEMINI_API_KEY", None)

import uvicorn
from docx import Document

from autolab import runner
from autolab import server

DOCX = (ROOT / "template_empty.docx").read_bytes()


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = _free_port()
BASE = f"http://127.0.0.1:{PORT}"


def call(method, path, *, json_body=None, fields=None, file=None):
    """Return (status, body bytes, headers). Never raises on HTTP errors."""
    headers = {}
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers["content-type"] = "application/json"
    elif fields is not None or file is not None:
        b = "----autolab" + uuid.uuid4().hex
        parts = [f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
                 for k, v in (fields or {}).items()]
        if file is not None:
            parts += [f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{file[0]}\"\r\n"
                      f"Content-Type: application/octet-stream\r\n\r\n".encode(), file[1], b"\r\n"]
        parts.append(f"--{b}--\r\n".encode())
        data = b"".join(parts)
        headers["content-type"] = f"multipart/form-data; boundary={b}"
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read(), {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, e.read(), {k.lower(): v for k, v in e.headers.items()}


def doc_text(blob: bytes) -> str:
    from autolab.docxedit import iter_all_paragraphs  # body + tables + headers/footers
    return "\n".join(p.text for p in iter_all_paragraphs(Document(io.BytesIO(blob))))


def check(label, cond, detail=""):
    print(f"  {'ok ' if cond else 'FAIL'} {label}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        raise SystemExit(f"FAIL: {label}")


def main() -> None:
    srv = uvicorn.Server(uvicorn.Config(server.app, host="127.0.0.1", port=PORT, log_level="warning"))
    threading.Thread(target=srv.run, daemon=True).start()
    for _ in range(100):
        if srv.started:
            break
        time.sleep(0.05)

    st, body, _ = call("GET", "/api/capabilities")
    caps = json.loads(body)
    check("capabilities", st == 200 and caps["desktop"] is True and "tools" in caps, body[:200])
    check("python runnable", caps["tools"].get("python") is True, caps["tools"])

    st, body, _ = call("GET", "/api/profile")
    check("fresh profile has no key", st == 200 and json.loads(body)["ai_key_set"] is False, body[:200])

    st, body, _ = call("POST", "/api/document/parse", file=("t.docx", DOCX))
    parsed = json.loads(body)
    check("parse docx", st == 200 and parsed["block_count"] > 0, body[:200])
    target = next(b for b in parsed["blocks"] if b["text"].strip())["id"]

    st, body, _ = call("POST", "/api/document/save", fields={"edits": json.dumps({target: "SMOKE EDIT"})},
                       file=("t.docx", DOCX))
    check("save edit", st == 200 and "SMOKE EDIT" in doc_text(body))

    st, body, _ = call("POST", "/api/replace", fields={"find": "{{TITLE}}", "replace": "Replaced Title"},
                       file=("t.docx", DOCX))
    check("find & replace", st == 200 and "Replaced Title" in doc_text(body))

    st, body, _ = call("POST", "/api/template/fill", json_body={
        "template": "neutral", "course_title": "Smoke Lab", "register_number": "URK00XX0000",
        "ex_no": "1", "title": "End-to-end smoke", "date": "2026-10-12"})
    check("template fill", st == 200 and len(body) > 1000, body[:200])

    st, body, h = call("POST", "/api/document/add-question",
                       fields={"number": "2", "title": "Smoke question", "description": "desc"},
                       file=("t.docx", DOCX))
    check("add question", st == 200 and "Smoke question" in doc_text(body))

    st, body, h = call("POST", "/api/document/add-solved-question", fields={
        "number": "3", "title": "Hello", "language": "python", "code": "print('hello from smoke')",
        "urk": "URK00XX0000"}, file=("t.docx", DOCX))
    check("solve python", st == 200 and h.get("x-run-ok") == "1" and int(h.get("x-images-added", 0)) >= 1,
          f"{st} {body[:200]!r}")

    st, body, _ = call("POST", "/api/ai/rewrite", json_body={"text": "hello", "instruction": ""})
    check("AI without key -> 400", st == 400, body[:200])

    # Pretend gcc isn't installed: must be a clear 400, not a 500 traceback.
    real_which = runner.shutil.which
    runner.shutil.which = lambda name, *a, **k: None if name == "gcc" else real_which(name, *a, **k)
    try:
        st, body, _ = call("POST", "/api/document/add-solved-question", fields={
            "number": "4", "title": "C", "language": "c", "code": "int main(){return 0;}"},
            file=("t.docx", DOCX))
        detail = json.loads(body).get("detail", "")
        check("missing gcc -> 400 with hint", st == 400 and "gcc" in detail and "install" in detail.lower(), body[:200])
        st, body, _ = call("GET", "/api/capabilities")
        check("capabilities reports c missing", json.loads(body)["tools"]["c"] is False)
    finally:
        runner.shutil.which = real_which

    srv.should_exit = True
    print("PASS")


if __name__ == "__main__":
    main()
