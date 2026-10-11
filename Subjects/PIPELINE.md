# Subjects — overall pipeline notes to self (Claude)

Maintained across sessions, same as each subject's own `PIPELINE.md`. This file
holds only what's genuinely shared across subjects — reconcile stale lines
when the pattern changes, don't let subject-specific detail creep in here
(that belongs in `<Subject>/PIPELINE.md`).

## What `Subjects/` is
Cleo's own lab records, generated **directly** for her — not the general
AutoLAB product (the `autolab.py`/`server.py`/web-app stack at the repo root,
built for ~500 other students to self-serve). Different audience, different
code path: `Subjects/` is a personal pipeline, skip the site user flow
entirely when working here.

Reg no is always **URK24CS1021**. Every subject folder has the same shape, so
"what do I show the teacher" and "what does Claude use" are always the same answer:
```
Subjects/
  PIPELINE.md              — this file
  client_secret*.json, token.json   — Google OAuth for classroom_sync (gitignored; never commit)
  <Subject>/               — DSE, DBMS, WebTech
    PIPELINE.md            — per-subject notes
    records/ExN/           — SHOW THE TEACHER: the finished record docx (+pdf for DBMS)
    output/ExN/            — working files: code as run, data, screenshots, notebook, video cue-cards
    scripts/               — Claude's builders (build_*.py, dse_record.py, dbms_lab.py, classroom_sync.py)
    materials/             — teacher uploads: templates, question banks, datasets, slides
                             (DSE: materials/classroom/ = full mirror of the Classroom course)
    assignments/           — standalone non-numbered deliverables (DSE, WebTech)
    archive/, others/      — superseded builds; work done for other students (DBMS)
```

## The shared philosophy: run for real, capture real output
Every subject's builder actually executes the code/SQL and captures genuine
stdout — never hand-writes or guesses what output "should" look like. This is
a hard rule from the teachers, not a style preference: content must not sound
AI-written and must contain no hallucinated output. Concretely:
- Code/SQL actually runs (subprocess or in-process `exec`), stdout is
  captured, and a terminal/editor-style PNG is rendered from that real text
  via `labshot.py` (repo root). No pixel-patching, no fabricated screenshots.
- Student-style code: lowercase, light comments, no over-engineering, no
  AI-tell phrasing. Mam/sir are aware Claude is involved — the ask is that
  the *artifact* still reads like something a student organically typed, not
  that it hide its origin.
- Where a question needs data that doesn't naturally exist (e.g. nulls to
  demonstrate imputation on a clean dataset), it's fine to construct it —
  but do it visibly in the code/SQL shown, and keep the fabrication scoped
  to that one demonstration, never as a substitute for a real run.

## Shared building blocks (repo root, used by every subject)
- `labshot.py` — renders real captured text as PNGs: `render_terminal_shot`
  (Windows cmd/PowerShell console look), `render_console_text` (pre-composed
  transcript, auto-fit width — used for psql), `render_code_shot` (VS Code
  editor look).
- `assemble.py` — `add_code_block()` writes code into a docx as one shaded
  monospace paragraph (soft line breaks, so it survives edits/reflow as a
  single block).
- Each subject's builder does its own docx assembly on top of these two —
  either filling a teacher-provided template, or (when none exists) building
  the record from scratch with matching layout conventions: header
  (course + reg no, bottom border), footer (`EX-N: TITLE`), Ex.No/Date table,
  Aim/Description/Question, then one Sample Code + Sample Output pair per
  question, RESULT. See `DSE/scripts/build_dse_ex1.py` or
  `DBMS/scripts/dbms_lab.py:build_docx_scratch` for the concrete pattern to copy.

## Classroom mirror (`DSE/scripts/classroom_sync.py`)
`python Subjects/DSE/scripts/classroom_sync.py [courseId]` pulls a whole Google
Classroom course into `<Subject>/materials/classroom/<topic>/<post>/` and writes
`index.md` (every post: due date, description, links, YouTube). Uses the Classroom
+ Drive read-only APIs via OAuth: `Subjects/client_secret*.json` (Desktop-app
client from Cleo's college Cloud project) and `Subjects/token.json` (created on
first run, browser consent). Re-runnable, skips files it already has. Default
course id is the DSE lab (`855460957674` = base64-decoded id in the Classroom
URL); pass another id for DBMS/WebTech. `.mp4`s in the mirror are gitignored.
Needs `pip install google-api-python-client google-auth-oauthlib`. Google
reshuffles the granted scope list, so the script sets
`OAUTHLIB_RELAX_TOKEN_SCOPE=1` (otherwise oauthlib raises "Scope has changed").

## Output layout convention
Builders write working files to `<Subject>/output/Ex<N>/` — the real
script/SQL as run, `screenshots/` (real PNGs), data, and for DSE a Jupyter
notebook + video cue-card script — and the **finished record docx to
`<Subject>/records/Ex<N>/`**. Builders locate themselves with
`HERE = Path(__file__).resolve().parents[1]` and the repo root with
`parents[3]` (they live in `<Subject>/scripts/`).

`labshot.py` renders terminal/editor-style PNGs for subjects whose "real
output" is stdout (DSE, DBMS). WebTech's real output is a browser render, so
its screenshots come from actually loading the page via `claude-in-chrome`
and capturing it — same "real capture, not synthesized" principle, different
tool for the job. Don't reach for `labshot` there.

## Folder hygiene
Subject root = `PIPELINE.md` + the folders in the tree above, nothing loose.
Teacher-provided originals go in `materials/` (never duplicate a file that is
already in `materials/classroom/` — dedupe by hash); superseded stuff in
`archive/`. Delete `~$*` Word lock files, `.ipynb_checkpoints`, `__pycache__`.
After moving any script, re-check its `HERE`/`REPO` constants (import every
script and assert `HERE/"materials"` and `REPO/"labshot.py"` exist) — do NOT
rebuild to test, a rebuild overwrites hand-edited records.

## Per-subject specifics
Don't duplicate these here — read the subject's own file:
- `DSE/PIPELINE.md` — Data Science Ecosystem Lab (23CS2025), Python
  NumPy/Pandas, per-student question bank, notebook + video-script
  deliverables, the "reg no printed first in every notebook cell" rule
  (from Ex-2 onward).
- `DBMS/PIPELINE.md` — Database Systems Lab (23CS2014), PostgreSQL (chosen
  over Oracle/MySQL), `dbms_lab.py` single builder for all experiments,
  table-naming/schema-mutation history, the from-scratch record path for
  experiments with no teacher template.
- `WebTech/PIPELINE.md` — Web Technologies lab, HTML5/CSS(/JS later),
  "run for real" means actually rendering in a browser via the
  `claude-in-chrome` tools (`file://` is blocked, serve over
  `http://127.0.0.1`) and screenshotting that; fills mam's real
  `Lab Record Format.docx` template rather than building from scratch. Site
  theme: online gaming community ("Respawn Point"), orange+green palette.
