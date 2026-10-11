"""Build Cleo's DSE Ex-3 record (Data Visualization / university admissions)
from scratch, same approach as build_dse_ex1/ex2.py: run the real Python,
capture real output + real plots, assemble the .docx.

    python Subjects/DSE/build_dse_ex3.py
"""
from __future__ import annotations

import ast, base64, contextlib, io, json, os, sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless: this runs from a build script, never a GUI
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt
from assemble import add_code_block
import labshot

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "output" / "Ex3"
URK = "URK24CS1021"
DATE = "06/08/2026"
COURSE = "23CS2025 DATA SCIENCE ECOSYSTEM LAB"
TITLE = "DATA VISUALIZATION"
FONT = "Times New Roman"

AIM = ("To develop and implement Python programs that visualise real-world datasets "
       "from various industries such as HR, logistics, retail, finance, education and "
       "security using Matplotlib and Seaborn.")
DESC = ("Matplotlib is Python's core plotting library and Seaborn is built on top of it "
        "with a shorter, dataset-aware interface. Together they turn a Pandas DataFrame "
        "into charts: scatter plots for the relationship between two numeric columns, "
        "box and violin plots for how a distribution differs between groups, bar plots "
        "for a summary value per category, and histograms for the shape of a single "
        "column. They show the patterns, spread and outliers that a table of numbers "
        "hides.")

# ---- the assigned dataset -------------------------------------------------
# NOTE: transcribed exactly from the 15-row table in URK23CS1021_EXP3.docx.
# If the assigned dataset ever changes, edit this constant and re-run.
CSV = """Student_ID,GPA,SAT_Score,ACT_Score,Extracurriculars,Recommendation_Strength,Admitted
U001,3.8,1420,32,3,Strong,Yes
U002,3.2,1200,26,1,Weak,No
U003,4.0,1560,35,5,Strong,Yes
U004,3.5,1310,29,2,Moderate,Yes
U005,3.9,1480,33,4,Strong,Yes
U006,3.1,1150,24,1,Weak,No
U007,3.7,1380,30,3,Moderate,Yes
U008,3.0,1100,22,0,Weak,No
U009,4.0,1520,34,5,Strong,Yes
U010,3.6,1350,28,2,Moderate,Yes
U011,3.3,1250,27,1,Weak,No
U012,3.8,1450,31,4,Strong,Yes
U013,3.4,1280,27,2,Moderate,No
U014,3.9,1500,33,5,Strong,Yes
U015,3.2,1180,25,1,Weak,No
"""

QUESTION = (
    "Dataset: University Admissions Dataset (admissions.csv)\n"
    "Columns: Student_ID, GPA, SAT_Score, ACT_Score, Extracurriculars, "
    "Recommendation_Strength, Admitted\n"
    "\u2022 Scatter Plot: SAT_Score vs. GPA (color by Admitted)\n"
    "\u2022 Box Plot: ACT_Score distribution by Admitted status\n"
    "\u2022 Bar Plot: Admission rate by Recommendation_Strength\n"
    "\u2022 Histogram: Distribution of Extracurriculars\n"
    "\u2022 Violin Plot: GPA distribution by Admitted status")
RESULT = "The exercise shown above has been successfully executed and the output has been verified."

PREAMBLE = (
    "import pandas as pd\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n\n"
    'sns.set_theme(style="whitegrid")\n'
    'plt.rcParams["figure.figsize"] = (7, 4.5)\n\n'
)

# (heading for the docx label, source code for that question)
SECTIONS: list[tuple[str, str]] = [
    ("Loading the dataset",
     'df = pd.read_csv("admissions.csv")\n'
     'print(df)\n'
     'print("\\nShape:", df.shape)\n'
     'print("\\nData types:")\nprint(df.dtypes)'),

    ("1. Scatter Plot: SAT_Score vs. GPA (colour by Admitted)",
     'sns.scatterplot(data=df, x="GPA", y="SAT_Score", hue="Admitted",\n'
     '                style="Admitted", s=120)\n'
     'plt.title("SAT Score vs GPA, coloured by admission status")\n'
     'plt.xlabel("GPA")\n'
     'plt.ylabel("SAT Score")\n'
     'plt.tight_layout()\n'
     'plt.show()'),

    ("2. Box Plot: ACT_Score distribution by Admitted status",
     'sns.boxplot(data=df, x="Admitted", y="ACT_Score",\n'
     '            hue="Admitted", palette="Set2", legend=False)\n'
     'plt.title("ACT Score distribution by admission status")\n'
     'plt.xlabel("Admitted")\n'
     'plt.ylabel("ACT Score")\n'
     'plt.tight_layout()\n'
     'plt.show()'),

    ("3. Bar Plot: Admission rate by Recommendation_Strength",
     '# Admitted is Yes/No, so the admission rate is the mean of (Admitted == "Yes")\n'
     'rate = (df.groupby("Recommendation_Strength")["Admitted"]\n'
     '          .apply(lambda s: (s == "Yes").mean())\n'
     '          .reindex(["Weak", "Moderate", "Strong"]))\n'
     'print("Admission rate:")\nprint(rate)\n\n'
     'sns.barplot(x=rate.index, y=rate.values, hue=rate.index,\n'
     '            palette="Blues_d", legend=False)\n'
     'plt.title("Admission rate by recommendation strength")\n'
     'plt.xlabel("Recommendation Strength")\n'
     'plt.ylabel("Admission rate")\n'
     'plt.ylim(0, 1)\n'
     'plt.tight_layout()\n'
     'plt.show()'),

    ("4. Histogram: Distribution of Extracurriculars",
     '# whole numbers 0-5, so give it explicit bins instead of the automatic ones\n'
     'plt.hist(df["Extracurriculars"], bins=range(0, 7), edgecolor="black",\n'
     '         align="left", color="#4C72B0")\n'
     'plt.xticks(range(0, 6))\n'
     'plt.yticks(range(0, 6))  # counts are whole students, not 2.5 of one\n'
     'plt.title("Distribution of extracurricular activities")\n'
     'plt.xlabel("Number of extracurriculars")\n'
     'plt.ylabel("Number of students")\n'
     'plt.tight_layout()\n'
     'plt.show()'),

    ("5. Violin Plot: GPA distribution by Admitted status",
     'sns.violinplot(data=df, x="Admitted", y="GPA", hue="Admitted",\n'
     '               palette="Set3", legend=False)\n'
     'plt.title("GPA distribution by admission status")\n'
     'plt.xlabel("Admitted")\n'
     'plt.ylabel("GPA")\n'
     'plt.tight_layout()\n'
     'plt.show()'),
]


def shot(output: str) -> bytes:
    return labshot.render_terminal_shot(
        output, command="python admissions_viz.py", cwd=r"C:\DSE\Ex3", style="cmd",
        urk_mode="none", show_banner=False, trailing_prompt=True, width=1500)


def _grab_figure() -> bytes | None:
    """Save whatever figure the section just drew, then close it."""
    if not plt.get_fignums():
        return None
    buf = io.BytesIO()
    plt.gcf().savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close("all")
    return buf.getvalue()


def run_sections() -> list[list[bytes]]:
    """Exec each section cumulatively in one shared namespace. Each section
    gives back its images: a terminal shot if it printed anything, plus the
    plot it drew."""
    ns: dict = {}
    prev_cwd = os.getcwd()
    os.chdir(OUT)  # admissions_viz.py reads "admissions.csv" next to itself
    try:
        exec(compile(PREAMBLE, "<preamble>", "exec"), ns)
        shots = []
        for _heading, code in SECTIONS:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exec(compile(code, "<section>", "exec"), ns)
            imgs = []
            if buf.getvalue().strip():
                imgs.append(shot(buf.getvalue().rstrip("\n")))
            fig = _grab_figure()
            if fig:
                imgs.append(fig)
            assert imgs, f"section produced no output: {_heading}"
            shots.append(imgs)
    finally:
        os.chdir(prev_cwd)
    return shots


# ---- notebook + video script ---------------------------------------------
NB_CELLS = [
    ("md", "# Ex 3 \u2014 Data Visualization\n\n"
           "**Dataset:** University Admissions (admissions.csv)  \n"
           "**Reg No:** URK24CS1021", None),
    ("code",
     "import pandas as pd\n"
     "import matplotlib.pyplot as plt\n"
     "import seaborn as sns\n\n"
     'sns.set_theme(style="whitegrid")\n'
     'plt.rcParams["figure.figsize"] = (7, 4.5)\n\n'
     'df = pd.read_csv("admissions.csv")\n'
     "df", None),
    ("code", "df.dtypes", None),
    ("md", "### 1. Scatter plot \u2014 does a higher GPA come with a higher SAT score?", None),
    ("code",
     'sns.scatterplot(data=df, x="GPA", y="SAT_Score", hue="Admitted", style="Admitted", s=120)\n'
     'plt.title("SAT Score vs GPA")\n'
     "plt.show()", None),
    ("md", "### 2. Box plot \u2014 how do ACT scores differ between admitted and rejected?", None),
    ("code",
     'sns.boxplot(data=df, x="Admitted", y="ACT_Score", hue="Admitted", palette="Set2", legend=False)\n'
     'plt.title("ACT Score by admission status")\n'
     "plt.show()", None),
    ("md", "### 3. Bar plot \u2014 does a stronger recommendation mean a better chance?", None),
    ("code",
     'rate = (df.groupby("Recommendation_Strength")["Admitted"]\n'
     '          .apply(lambda s: (s == "Yes").mean())\n'
     '          .reindex(["Weak", "Moderate", "Strong"]))\n'
     "rate", None),
    ("code",
     'sns.barplot(x=rate.index, y=rate.values, hue=rate.index, palette="Blues_d", legend=False)\n'
     'plt.ylabel("Admission rate")\nplt.ylim(0, 1)\n'
     'plt.title("Admission rate by recommendation strength")\n'
     "plt.show()", None),
    ("md", "### 4. Histogram \u2014 how many activities does a typical applicant have?", None),
    ("code",
     'plt.hist(df["Extracurriculars"], bins=range(0, 7), edgecolor="black", align="left")\n'
     "plt.xticks(range(0, 6))\nplt.yticks(range(0, 6))\n"
     'plt.xlabel("Number of extracurriculars")\nplt.ylabel("Number of students")\n'
     "plt.show()", None),
    ("md", "### 5. Violin plot \u2014 the box plot, plus the shape of the distribution", None),
    ("code",
     'sns.violinplot(data=df, x="Admitted", y="GPA", hue="Admitted", palette="Set3", legend=False)\n'
     'plt.title("GPA distribution by admission status")\n'
     "plt.show()", None),
]


def _srclist(text: str) -> list[str]:
    return text.splitlines(keepends=True) or [""]


def _run_cell(src: str, ns: dict, count: int) -> list[dict]:
    tree = ast.parse(src)
    last = tree.body[-1] if tree.body else None
    buf, result = io.StringIO(), None
    with contextlib.redirect_stdout(buf):
        if isinstance(last, ast.Expr):
            exec(compile(ast.Module(tree.body[:-1], []), "<cell>", "exec"), ns)
            result = eval(compile(ast.Expression(last.value), "<cell>", "eval"), ns)
        else:
            exec(compile(tree, "<cell>", "exec"), ns)
    outs = []
    if buf.getvalue():
        outs.append({"output_type": "stream", "name": "stdout",
                     "text": _srclist(buf.getvalue())})
    fig = _grab_figure()  # plot cells return None from plt.show(), so catch the figure
    if fig:
        outs.append({"output_type": "display_data", "metadata": {},
                     "data": {"image/png": base64.b64encode(fig).decode()}})
    if result is not None:
        data = {"text/plain": _srclist(repr(result))}
        if hasattr(result, "_repr_html_"):
            data["text/html"] = _srclist(result._repr_html_())
        outs.append({"output_type": "execute_result", "execution_count": count,
                     "metadata": {}, "data": data})
    return outs


def build_notebook(path: Path) -> None:
    ns: dict = {}
    cells, count = [], 0
    for kind, src, _note in NB_CELLS:
        if kind == "md":
            cells.append({"cell_type": "markdown", "metadata": {}, "source": _srclist(src)})
        else:
            count += 1
            # teacher's rule from Ex-2 onward: reg no printed first, every cell
            src = f'print("{URK}")\n\n' + src
            cells.append({"cell_type": "code", "execution_count": count,
                          "metadata": {}, "outputs": _run_cell(src, ns, count),
                          "source": _srclist(src)})
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                      "name": "python3"},
                       "language_info": {"name": "python", "version": "3.14"}},
          "nbformat": 4, "nbformat_minor": 5}
    path.write_text(json.dumps(nb, indent=1), encoding="utf8")


VIDEO = """# Ex 3 — Code explanation (teaching cues)
*Data Visualization · University Admissions dataset · URK24CS1021*

> Mam wants this to sound like **you teaching a junior**, not you reading the code.
> So the order is always: **the question first, the chart choice second, the code last.**
> Glance at these cues, look at the plot on screen, and say it in your own words.
> ~5-6 min. Pause after each plot and actually point at what it shows.

**Open with** — who you are, reg no URK24CS1021, Experiment 3.
Then the hook, in your own words: *"We have a table of 15 applicants — GPA, SAT, ACT,
activities, recommendation, admitted or not. I could just call `describe()` and read out
the averages. But an average won't tell me whether the two groups actually separate, or
where the odd student out is. That's what plotting is for. Five charts, five different
questions."*

---

**1. Scatter plot — SAT vs GPA, coloured by Admitted**
- Question first: *do the two scores move together, and do admits sit somewhere separate?*
- Why a scatter: two numeric columns, one dot per student, nothing summarised away.
- Why `hue="Admitted"`: it adds a third, categorical variable without a second chart.
- Then the code: `sns.scatterplot(data=..., x=..., y=..., hue=...)`.
- Point at it: the dots climb left-to-right (GPA and SAT agree), and the Yes/No colours
  form two fairly separate clusters — say where the boundary roughly sits.

**2. Box plot — ACT by Admitted**
- Question: *how does the ACT distribution differ between the two groups?*
- Why a box and not a bar: a bar would show only the two means and hide the spread.
  A box gives median, the middle 50% (the box), the range (the whiskers), and outliers.
- Teach the anatomy once, here — line = median, box = quartiles, whiskers = the rest.
  Every later box plot they ever see reads the same way.
- Then the code, and read the answer off it: admitted students sit clearly higher, and
  the two boxes barely overlap.

**3. Bar plot — admission rate by Recommendation_Strength**
- Question: *does a stronger recommendation actually mean a better chance?*
- The teaching bit here is that **the column I want doesn't exist**. `Admitted` is
  Yes/No text. A rate is a number. So `groupby` the recommendation, then take the mean
  of `(s == "Yes")` — True counts as 1, False as 0, so the mean *is* the rate.
- Why a bar: one summary number per category — exactly what bars are for.
- Point at it: Weak ≈ 0, Moderate in the middle, Strong = 1. Then the honest caveat —
  15 rows, so "Strong is 100%" means five students, not a law.

**4. Histogram — Extracurriculars**
- Question: *what does a typical applicant's activity count look like?*
- Why a histogram and not a bar chart: this is **one** column being bucketed by value,
  not a value per named category. Bars = categories, histogram = distribution.
- The gotcha worth teaching: these are whole numbers 0–5, and automatic bins split
  them at odd places, so I pass `bins=range(0, 7), align="left"` — one bin per value.
- Point at it: the tallest bar is 1 activity, nobody is far out on their own, and the
  counts are spread fairly evenly across 1–5 — with 15 students there is no dramatic
  peak to read into. Saying that out loud is better than inventing a pattern.

**5. Violin plot — GPA by Admitted**
- Question: same as the box plot, but *what shape is the distribution?*
- Why a violin: it's a box plot with a density curve mirrored on both sides — wide
  means many students at that GPA, narrow means few. Use it when the shape matters,
  use a box when you just want the summary.
- Honest note: with 15 rows the curve is lumpy. Say so — a violin wants more data,
  and knowing when a chart is oversold is part of the point.

---

**Close with** — one line per chart type as a takeaway, not a recap of the code:
*scatter = relationship between two numbers · box = compare a distribution across
groups · bar = one summary value per category · histogram = the shape of one column ·
violin = box plot plus shape.* Then: pick the chart from the question you're asking,
not from what looks nice.
"""


# ---- docx helpers (same as build_dse_ex1/ex2.py) --------------------------
def rfonts(el, name=FONT):
    rpr = el.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs"):
        rf.set(qn(a), name)


def cell_border(cell):
    pr = cell._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for s in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{s}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "6")
        e.set(qn("w:space"), "0"); e.set(qn("w:color"), "000000")
        b.append(e)
    pr.append(b)


def label(doc, text, size=12, space_before=8):
    p = doc.add_paragraph()
    r = p.add_run(text); r.bold = True; r.font.name = FONT; r.font.size = Pt(size)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(3)
    return p


def body(doc, text, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text); r.font.name = FONT; r.font.size = Pt(12); r.italic = italic
    p.paragraph_format.space_after = Pt(4)
    return p


def _img(doc, png, width_in=6.2):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    p.add_run().add_picture(io.BytesIO(png), width=Inches(width_in))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "screenshots").mkdir(exist_ok=True)
    (OUT / "admissions.csv").write_text(CSV, encoding="utf8")

    full_code = PREAMBLE + "\n\n".join(
        f"# {heading}\n{code}" for heading, code in SECTIONS)
    (OUT / "admissions_viz.py").write_text(
        "# Ex 3 - Data Visualization (University Admissions dataset)\n"
        "# URK24CS1021\n\n" + full_code, encoding="utf8")

    shots = run_sections()
    for i, imgs in enumerate(shots, 1):
        for j, png in enumerate(imgs):
            suffix = "" if len(imgs) == 1 else f"{chr(ord('a') + j)}"
            (OUT / "screenshots" / f"q{i:02d}{suffix}_output.png").write_bytes(png)

    doc = Document()
    normal = doc.styles["Normal"]; normal.font.name = FONT; normal.font.size = Pt(12)
    rfonts(normal.element)
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(sec, m, Inches(1.0))

    h = sec.header.paragraphs[0]
    h.paragraph_format.tab_stops.add_tab_stop(Cm(15.9), WD_TAB_ALIGNMENT.RIGHT)
    r = h.add_run(COURSE); r.bold = True
    h.add_run("\t"); r2 = h.add_run(URK); r2.bold = True
    pbdr = h._p.get_or_add_pPr()
    bd = OxmlElement("w:pBdr"); bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single"); bot.set(qn("w:sz"), "12")
    bot.set(qn("w:space"), "1"); bot.set(qn("w:color"), "000000")
    bd.append(bot); pbdr.append(bd)
    f = sec.footer.paragraphs[0]; f.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = f.add_run(f"EX-3: {TITLE}"); fr.bold = True

    t = doc.add_table(rows=2, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    rows = [("Ex. No. 3", TITLE), ("Date of Exercise", DATE)]
    widths = (Inches(1.9), Inches(4.35))
    for ri, (a, b) in enumerate(rows):
        for ci, txt in enumerate((a, b)):
            c = t.rows[ri].cells[ci]; c.width = widths[ci]
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = c.paragraphs[0]
            if ri == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cr = p.add_run(txt); cr.font.name = FONT; cr.font.size = Pt(12)
            cr.bold = (ci == 0 or ri == 0)
            cell_border(c)
    doc.add_paragraph()

    label(doc, "Aim"); body(doc, AIM)
    label(doc, "Description (About Matplotlib & Seaborn)"); body(doc, DESC)
    label(doc, "Question:"); body(doc, QUESTION)

    for (heading, code), imgs in zip(SECTIONS, shots):
        label(doc, f"Sample Code: {heading}")
        add_code_block(doc, code)
        label(doc, "Sample Output:")
        for png in imgs:
            _img(doc, png)

    label(doc, "CODE EXPLANATION LINK:")
    body(doc, "(Youtube / Drive Link)", italic=True)
    label(doc, "Preparation course certificate")
    doc.add_paragraph()
    label(doc, "RESULT"); body(doc, RESULT)

    out_docx = HERE / "records" / "Ex3" / f"Ex3_{URK}.docx"; out_docx.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_docx))

    prev_cwd = os.getcwd()
    os.chdir(OUT)
    try:
        build_notebook(OUT / "Ex3_Admissions.ipynb")
    finally:
        os.chdir(prev_cwd)
    (OUT / "video_script.md").write_text(VIDEO, encoding="utf8")
    print("wrote", OUT)
    print("  sections:", len(shots), "| images:", sum(len(i) for i in shots),
          "| docx:", out_docx.name, "| notebook + video_script.md")


if __name__ == "__main__":
    build()
