# AutoLAB: making lab records

You (the agent) write the code. The `autolab` command does what you can't do
reliably by hand: **run it for real**, draw the terminal/editor screenshots
from the real output, run notebooks and SQL, and write the `.docx`. Every
`autolab` command prints one JSON object on stdout. Exit code 0 = ok, 1 = it
ran but the program/SQL failed (read the JSON, fix, rerun), 2 = bad usage or
a missing tool.

## Hard rules

1. **Never invent output.** Every output in a record comes from actually
   running the code through `autolab`. If a run fails, fix the code and rerun.
   Don't hand-write what the output "should" be, and never paste a failed run
   into a record.
2. **Construct data only visibly.** If a question needs data that doesn't
   exist (nulls to demonstrate imputation, say), create it in the code shown,
   scoped to that one demonstration.
3. **Write code at the course's level.** Keep it simple and idiomatic, the way
   the lab manual does it. Use the libraries the question names, use short
   comments, and don't over-engineer.
4. **Follow the teacher's materials.** If they gave a template `.docx`, fill
   that (`autolab record add`, `autolab replace`). Only build from scratch
   (`autolab record new`) when there's no template.
5. Before the first run, check `autolab doctor` for which languages, database
   clients and tools are installed. If one is missing, tell the user what to
   install instead of working around it.

## Workspace

`autolab init` creates this layout in a lab folder. Keep to it:

```
autolab.json          register number, name, courses -- read this first
<Subject>/
  materials/          teacher uploads: templates, question banks, datasets
  output/ExN/         working files: code as run, data, screenshots, notebooks
  records/ExN/        the finished record to submit
  scripts/            any builder scripts you write
  NOTES.md            per-subject conventions you learn (template quirks,
                      what the teacher asked for). Read it, and keep it current
```

## Commands

```
autolab doctor
autolab run q1.py --shot output/Ex3/q1.png [--code-shot output/Ex3/q1_code.png]
        [--stdin input.txt] [--timeout 15] [--urk URK.. --urk-mode line|title|prompt|none]
        [--style cmd|powershell]
autolab run-pair server.py client.py --shot-server s.png --shot-client c.png
autolab notebook ex5.py --out output/Ex5/Ex5.ipynb --shots output/Ex5/screenshots
        [--prefix 'print("URK..")']        # percent-format cells: "# %%"
autolab sql ex2.sql --engine psql --db labdb [--user postgres] --shots output/Ex2/screenshots
autolab sql ex2.sql --engine sqlite --db lab.db --shots ...    # "-- @q N" splits questions
autolab shot terminal --text-file out.txt --command "python q1.py" --out x.png
autolab shot console  --text-file transcript.txt --title "psql" --out x.png
autolab shot code q1.py --out x.png
autolab record new spec.json --out records/Ex2/Ex2_URK...docx
autolab record add template.docx --out rec.docx --title "..." [--number 3]
        [--description "..."] [--code-file q3.py] --image q3.png [--image ...]
autolab replace rec.docx --find URK00 --replace URK24CS1021 [--out new.docx]
autolab blocks rec.docx                      # list editable blocks (id, text)
autolab edit rec.docx --edits edits.json     # {"block id": "new text"}
autolab pdf spans file.pdf                   # list text spans (id, text, font)
autolab pdf edit file.pdf --edits edits.json --out fixed.pdf
```

`record new` takes a JSON spec:

```json
{
  "course": "23CS2014 Database Systems Lab", "register_number": "URK24CS1021",
  "ex_no": "2", "title": "Basic SQL", "date": "29/07/2026",
  "aim": "...", "description": "...",
  "questions": [
    {"number": "1", "text": "Create the table ...",
     "code_file": "output/Ex2/q1.sql", "images": ["output/Ex2/screenshots/q1.png"]}
  ],
  "result": "The queries were executed and the output was verified."
}
```

Paths in the spec are relative to the spec file. Optional keys: `font`,
`code_label`, `output_label`, `image_dpi` (default 150, which keeps console
text the same size across shots), `image_max_width_in`.

## Typical flow

1. Read `autolab.json`, the subject's `NOTES.md` and the question in `materials/`.
2. Write the code into `output/ExN/`.
3. Run it with `autolab run` / `notebook` / `sql`, with shots going to
   `output/ExN/screenshots/`. Fix and rerun until `ok` is true.
4. Assemble: `record add` onto the teacher's template, or `record new`.
5. Open the record yourself to check it (`autolab blocks`), then tell the
   user where it is and anything they should check by eye.
