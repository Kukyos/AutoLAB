"""Build Cleo's WebTech Ex3 record -- same pattern as build_webtech_ex1/2.py:
fills mam's Lab Record Format.docx template with the real responsive HTML5+CSS3
page, the real code, and real screenshots at three breakpoints.

    python Subjects/WebTech/build_webtech_ex3.py

index.html + banner.png + the output_*.png screenshots must already exist in
output/Ex3/ (written by hand + captured via the browser, not by this script)
-- this script only assembles the docx around them.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from assemble import add_code_block

HERE = Path(__file__).resolve().parents[1]
MATERIALS = HERE / "materials"
OUT = HERE / "output" / "Ex3"
URK = "URK24CS1021"
COURSE = "23CS2049 - Web Technology Lab"
TITLE = "Responsive Website using HTML5 and CSS3"
DATE = "17/08/2026"
GITHUB_LINK = "https://kukyos.github.io/WebTechLab/Ex3/index.html"
IMG_W = 5.0

AIM = ("To design and implement a responsive website using HTML5 and CSS3, "
       "so that the same page adapts its layout across desktop, tablet and "
       "mobile screen sizes, applied to the online gaming community theme.")

DESC = ("Responsiveness here comes from CSS3 Flexbox and media queries, not "
        "separate pages for each device. The nav bar and the card grid both "
        "use display:flex so they can reflow instead of overflowing. The "
        "sidebar-plus-content section uses a flex container with each side "
        "sized in percentages, and every image uses max-width:100% so it "
        "never grows past its container. Three @media screen and (max-width: "
        "...) blocks then override those percentage widths and flex "
        "directions at three breakpoints: 992px (tablet, sidebar and content "
        "stack full-width), 768px (mobile, the nav links and the game cards "
        "switch to a single column) and 480px (small mobile, heading font "
        "sizes shrink and buttons go full-width). A "
        "<meta name=\"viewport\" content=\"width=device-width, "
        "initial-scale=1.0\"> tag is required for any of this to take effect "
        "on an actual phone, since without it mobile browsers render at a "
        "fake desktop-sized viewport and zoom out instead of reflowing.")

PROCEDURE = (
    "1. Reused the Ex1/Ex2 Respawn Point site and its orange-and-green color "
    "variables, this time moving every color and layout rule out of inline "
    "style attributes and into a single internal <style> block so media "
    "queries would actually have something to override.\n"
    "2. Added the viewport meta tag, without which the responsive rules "
    "would be ignored on a real phone.\n"
    "3. Restructured the page into <header>, <nav>, a <section class=\"hero\">, "
    "and a .container holding a .sidebar (community roles) and .content "
    "(about, games, roles detail, join, rules, contact), followed by "
    "<footer> -- the same section content as Ex1, laid out with Flexbox "
    "instead of stacked <div>s.\n"
    "4. Turned the featured-games table into a flex .cards grid, one card "
    "per game with a name, a short stat line and a button, so there would be "
    "a grid that visibly reflows at each breakpoint.\n"
    "5. Wrote the tablet breakpoint (max-width: 992px): the sidebar+content "
    "flex row switches to flex-direction:column and both go to 100% width.\n"
    "6. Wrote the mobile breakpoint (max-width: 768px): the nav list and the "
    "card grid switch to flex-direction:column so links and cards stack.\n"
    "7. Wrote the small-mobile breakpoint (max-width: 480px): heading font "
    "sizes shrink and buttons stretch to full width for easier tapping.\n"
    "8. Tested the page at three widths using the browser (desktop, tablet, "
    "mobile) and confirmed the nav, sidebar/content and card grid actually "
    "reflow at each one before taking the output screenshots."
)

RESULT = ("The responsive website was successfully designed and implemented "
          "using HTML5 and CSS3 Flexbox with media queries. The layout "
          "adapted correctly across desktop, tablet and mobile screen "
          "widths, matching the expected output.")


def set_placeholder(doc: Document, marker: str, text: str) -> None:
    paras = doc.paragraphs
    for i, p in enumerate(paras):
        if p.text.strip() == marker:
            ph = paras[i + 1]
            for r in list(ph.runs):
                r.text = ""
            if ph.runs:
                ph.runs[0].text = text
            else:
                ph.add_run(text)
            return
    raise ValueError(f"placeholder for {marker!r} not found")


def clear_placeholder(doc: Document, marker: str) -> "docx.text.paragraph.Paragraph":
    paras = doc.paragraphs
    for i, p in enumerate(paras):
        if p.text.strip() == marker:
            ph = paras[i + 1]
            for r in list(ph.runs):
                r.text = ""
            return ph
    raise ValueError(f"placeholder for {marker!r} not found")


def fill_header_regno(doc: Document, urk: str) -> None:
    """See build_webtech_ex1.py's copy of this function for why."""
    from docx.oxml.ns import qn
    header = doc.sections[0].header._element
    for t in header.iter(qn("w:t")):
        if t.text == "[regno]":
            t.text = urk
            return
    raise ValueError("[regno] placeholder not found in header")


def fill_footer_title(doc: Document, ex_label: str, title: str) -> None:
    """See build_webtech_ex1.py's copy."""
    from docx.oxml.ns import qn
    footer = doc.sections[0].footer._element
    found_ex, found_title = False, False
    for t in footer.iter(qn("w:t")):
        if t.text == "Ex. 1":
            t.text = ex_label
            found_ex = True
        elif t.text and t.text.strip() == "| Title of exercise":
            t.text = f" | {title}"
            found_title = True
    if not (found_ex and found_title):
        raise ValueError(f"footer placeholders not found (ex={found_ex}, title={found_title})")


def set_ex_number(docx_path: Path, label: str) -> None:
    """See build_webtech_ex1.py's copy: patches docProps/app.xml directly."""
    import re, zipfile
    tmp = docx_path.with_suffix(".tmp.docx")
    with zipfile.ZipFile(docx_path, "r") as zin, \
         zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/app.xml":
                text = data.decode("utf8")
                text = re.sub(r"<Company>.*?</Company>", f"<Company>{label}</Company>", text)
                data = text.encode("utf8")
            zout.writestr(item, data)
    tmp.replace(docx_path)


def build() -> Path:
    tmpl = next(MATERIALS.glob("Lab Record Format.docx"))
    doc = Document(str(tmpl))

    doc.core_properties.title = COURSE
    doc.core_properties.author = URK
    doc.core_properties.last_modified_by = URK
    fill_header_regno(doc, URK)
    fill_footer_title(doc, "Ex. 3", TITLE)

    t = doc.tables[0]
    t.rows[0].cells[0].paragraphs[0].runs[-1].text = "3"
    t.rows[0].cells[1].paragraphs[0].runs[0].text = TITLE
    for r in t.rows[0].cells[1].paragraphs[0].runs[1:]:
        r.text = ""
    dcell = t.rows[1].cells[1]
    if not dcell.paragraphs[0].runs:
        dcell.paragraphs[0].add_run(DATE)
    else:
        dcell.paragraphs[0].runs[0].text = DATE
    gcell = t.rows[2].cells[1]
    if not gcell.paragraphs[0].runs:
        gcell.paragraphs[0].add_run(GITHUB_LINK)
    else:
        gcell.paragraphs[0].runs[0].text = GITHUB_LINK

    set_placeholder(doc, "Aim", AIM)
    set_placeholder(doc, "Description", DESC)
    set_placeholder(doc, "Procedure:", PROCEDURE)

    program_anchor = clear_placeholder(doc, "Program")
    add_code_block(doc, (OUT / "index.html").read_text(encoding="utf8"))
    new_block = doc.paragraphs[-1]
    program_anchor._p.addnext(new_block._p)

    output_anchor = clear_placeholder(doc, "Output")
    insert_after = output_anchor
    for fname, caption in [
        ("output_1_desktop.png", "Desktop width (1200px): sidebar and content side by side, four-card row"),
        ("output_2_tablet.png", "Tablet breakpoint (900px, <=992px): sidebar stacks full-width above content"),
        ("output_3_mobile_nav.png", "Mobile breakpoint (400px, <=768px): nav links stack into a single column"),
        ("output_4_mobile_cards.png", "Mobile breakpoint (400px): game cards stack full-width, one per row"),
    ]:
        cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cr = cap.add_run(caption); cr.italic = True; cr.font.size = Pt(10)
        img = doc.add_paragraph(); img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img.paragraph_format.space_after = Pt(10)
        img.add_run().add_picture(str(OUT / fname), width=Inches(IMG_W))
        insert_after._p.addnext(cap._p)
        cap._p.addnext(img._p)
        insert_after = img

    set_placeholder(doc, "Result", RESULT)

    for p in list(doc.paragraphs):
        if p.text.strip().startswith("[Kindly Note"):
            p._p.getparent().remove(p._p)

    out_path = HERE / "records" / "Ex3" / f"Ex3_{URK}.docx"; out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    set_ex_number(out_path, "Ex. 3")
    print("wrote", out_path)
    return out_path


if __name__ == "__main__":
    build()
