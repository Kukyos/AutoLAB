# AutoLAB

Auto-fills college lab record `.docx` files. AI writes the code, AutoLAB
**actually runs it** on your machine, draws terminal / VS Code "screenshots"
from the real output, and inserts everything (heading, code, images) into the
record.

It also does find & replace across a whole record (including inside the
screenshots), template filling, and in-place PDF text editing.

Free and open source (MIT). No account needed.

## Get started (Windows)

1. **Download** `AutoLAB.exe` from the
   [latest release](https://github.com/Kukyos/AutoLAB/releases/latest) and run
   it. Nothing is installed. Windows SmartScreen may warn because the exe
   isn't signed: click *More info → Run anyway*.
2. **Add a free Gemini API key.** Get one at
   [aistudio.google.com](https://aistudio.google.com) (Google account, no
   card), then in AutoLAB go to **Profile → Gemini API key → Save**. The key
   stays on your PC, in `%APPDATA%\AutoLAB\profile.json`.
3. **Save your register number** in Profile, so it gets filled in for you.

### Running code needs the language installed

AutoLAB runs the program for real, so the compiler has to be on your PC.
Languages that aren't installed are greyed out in the solve form.

| Language | Install | Check it works (in a new terminal) |
|----------|---------|-------------------------------------|
| Python | [python.org](https://www.python.org/downloads/), tick **"Add python.exe to PATH"** | `python --version` |
| C / C++ | MinGW-w64 from [winlibs.com](https://winlibs.com) or [MSYS2](https://www.msys2.org), add its `bin` folder to PATH | `gcc --version` |
| Java | A JDK, e.g. [Temurin](https://adoptium.net) | `javac -version` |

Restart AutoLAB after installing so it picks up the new PATH.

## Features

- **Solve a question:** paste the question → Gemini writes the code → AutoLAB
  compiles and runs it (with timeouts, and server + client pairs for networking
  labs) → renders a Windows terminal and optional VS Code screenshot → appends
  it to the record. A failed run never gets pasted in.
- **Find & replace:** swap a register number everywhere in the text, and
  optionally **inside the screenshots** too (Gemini finds it in the image and
  rewrites it in place).
- **Templates:** generate a blank record with your course, register number,
  experiment number and date filled in.
- **Document editor:** open a `.docx`, edit blocks, add questions.
- **PDF editor:** click any line of a PDF and retype it. The text goes back at
  the same baseline in the same font (reused, re-embedded, or the closest
  match, and it tells you when it had to substitute). Scanned PDFs have no text
  layer and can't be edited.

## Run from source (any OS)

```
python -m venv .venv
.venv/bin/pip install -r requirements.txt     # Windows: .venv\Scripts\pip

.venv/bin/python desktop.py                   # desktop app
.venv/bin/python -m uvicorn server:app --port 8000   # web mode, open localhost:8000
```

Tests: `python tests/run_all.py` (smoke tests for the solve pipeline, the HTTP
API, templates, Gemini helpers, billing and the PDF editor).

Building the exe: `pyinstaller AutoLAB.spec --clean --noconfirm` on Windows,
which gives you `dist/AutoLAB.exe`. CI does this on every push and attaches it
to the release when a `v*` tag is pushed (`.github/workflows/build.yml`).

## What's inside

| File | Does |
|------|------|
| `desktop.py` | desktop launcher: in-process server + native window (pywebview) |
| `server.py` | FastAPI backend, all `/api/*` endpoints |
| `runner.py` | runs code (python/c/cpp/java) with timeouts; `run_pair` for server+client labs; checks the compilers are installed |
| `labshot.py` | draws the screenshots: Windows terminal and VS Code windows |
| `assemble.py` | writes a solved question (heading, code, images) into a docx |
| `autolab.py` | docx find/replace and block extraction/editing |
| `pdfedit.py` | PDF in-place text editing with automatic font finding |
| `gemini.py` | Gemini API client and in-place screenshot patching |
| `make_template.py` | builds the neutral record template |
| `static/` | frontend (vanilla JS, no build step) |
| `tests/` | smoke tests, `run_all.py` runs them all |

## Self-hosting extras (optional)

**Vercel:** the repo deploys as-is (`vercel.json` + `api/index.py`). The
hosted version does everything except actually running code, because there are
no compilers there. Gemini writes the output instead, and the solve form hides
itself.

**Prepaid credits:** `billing.py` contains an optional Supabase + Razorpay
credit wallet for a hosted instance. It is **off unless you set these env
vars**, so the app stays bring-your-own-key and free:

| Env var | From |
|---------|------|
| `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY` | Supabase → Settings → API |
| `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET` | Razorpay dashboard |
| `GEMINI_API_KEY` | the server-side key paid operations use |

Schema: paste `supabase_setup.sql` into the Supabase SQL editor. Prices are in
`billing.py` (`PRICES`).

## License

MIT, see [LICENSE](LICENSE).
