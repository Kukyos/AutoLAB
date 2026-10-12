"""Execute a percent-format Python script into a real .ipynb, outputs included.

Input is a plain .py split into cells the way VS Code and Jupytext read it:

    # %% [markdown]
    # ## Load the data
    # %%
    import pandas as pd
    df = pd.read_csv("rental.csv")
    df.head()

Code cells run in order in one shared namespace (like a kernel), with the
script's folder as the working directory. Each code cell records its stdout,
the value of a trailing expression (DataFrames keep their HTML table) and any
matplotlib figure it drew. Optionally each cell's stdout is also rendered as a
terminal screenshot and each figure saved as a PNG, ready for the record.

Execution stops at the first exception: the traceback goes into that cell's
outputs, and the result reports the error so the caller can fix the code
rather than ship a notebook that crashed.
"""

from __future__ import annotations

import ast
import base64
import contextlib
import io
import json
import os
import re
import sys
import traceback
from pathlib import Path

_MARK = re.compile(r"^# %%(.*)$")


def parse_cells(text: str) -> list[tuple[str, str]]:
    """Split percent-format source into [(kind, source)], kind = code|md."""
    cells: list[tuple[str, list[str]]] = []
    kind, buf = "code", []
    for line in text.splitlines():
        m = _MARK.match(line)
        if m:
            if any(s.strip() for s in buf):
                cells.append((kind, buf))
            kind = "md" if "markdown" in m.group(1) or "[md]" in m.group(1) else "code"
            buf = []
            continue
        buf.append(line)
    if any(s.strip() for s in buf):
        cells.append((kind, buf))
    out = []
    for kind, lines in cells:
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if kind == "md":
            lines = [l[2:] if l.startswith("# ") else l.lstrip("#") for l in lines]
        out.append((kind, "\n".join(lines)))
    return out


def _srclist(text: str) -> list[str]:
    return text.splitlines(keepends=True) or [""]


def _grab_figure() -> bytes | None:
    """Save and close whatever matplotlib figure the cell drew, if any."""
    plt = sys.modules.get("matplotlib.pyplot")
    if plt is None or not plt.get_fignums():
        return None
    buf = io.BytesIO()
    plt.gcf().savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close("all")
    return buf.getvalue()


def _run_cell(src: str, ns: dict, count: int) -> tuple[list[dict], str, bytes | None, str | None]:
    """Returns (nb outputs, stdout text, figure png, error text)."""
    buf, result, error = io.StringIO(), None, None
    try:
        tree = ast.parse(src)
        last = tree.body[-1] if tree.body else None
        with contextlib.redirect_stdout(buf):
            if isinstance(last, ast.Expr):
                exec(compile(ast.Module(tree.body[:-1], []), "<cell>", "exec"), ns)
                result = eval(compile(ast.Expression(last.value), "<cell>", "eval"), ns)
            else:
                exec(compile(tree, "<cell>", "exec"), ns)
    except Exception:
        error = traceback.format_exc()
    outs: list[dict] = []
    if buf.getvalue():
        outs.append({"output_type": "stream", "name": "stdout", "text": _srclist(buf.getvalue())})
    fig = _grab_figure()
    if fig:
        outs.append({"output_type": "display_data", "metadata": {},
                     "data": {"image/png": base64.b64encode(fig).decode()}})
    if result is not None:
        data = {"text/plain": _srclist(repr(result))}
        if hasattr(result, "_repr_html_"):
            try:
                data["text/html"] = _srclist(result._repr_html_())
            except Exception:
                pass
        outs.append({"output_type": "execute_result", "execution_count": count,
                     "metadata": {}, "data": data})
    if error:
        etype = error.strip().splitlines()[-1]
        outs.append({"output_type": "error", "ename": etype.split(":")[0],
                     "evalue": etype.partition(":")[2].strip(),
                     "traceback": error.splitlines()})
    return outs, buf.getvalue(), fig, error


def run_notebook(src_path: Path, out_path: Path, *, prefix: str = "",
                 shots_dir: Path | None = None, shot_command: str = "",
                 shot_cwd: str = r"C:\Users\Student\Desktop\Lab") -> dict:
    """Execute `src_path` (percent format) and write `out_path` (.ipynb).

    prefix: a line prepended to every code cell (e.g. `print("URK24CS1021")`,
            when the teacher wants the register number in every output).
    shots_dir: also write cellNN_out.png (terminal shot of stdout) and
               cellNN_fig.png (figure) per code cell.
    """
    os.environ.setdefault("MPLBACKEND", "Agg")  # never pop a GUI window
    cells = parse_cells(src_path.read_text(encoding="utf-8"))
    if shots_dir:
        shots_dir.mkdir(parents=True, exist_ok=True)
        from .labshot import render_terminal_shot
    nb_cells, ns, count = [], {"__name__": "__main__"}, 0
    summary: list[dict] = []
    error = None
    prev = os.getcwd()
    os.chdir(src_path.parent.resolve())
    try:
        for kind, src in cells:
            if kind == "md":
                nb_cells.append({"cell_type": "markdown", "metadata": {}, "source": _srclist(src)})
                continue
            count += 1
            if prefix:
                src = prefix + "\n\n" + src
            if error:  # after a failure, keep the cell but don't run it
                nb_cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                                 "outputs": [], "source": _srclist(src)})
                continue
            outs, stdout, fig, err = _run_cell(src, ns, count)
            nb_cells.append({"cell_type": "code", "execution_count": count, "metadata": {},
                             "outputs": outs, "source": _srclist(src)})
            entry: dict = {"cell": count, "stdout": stdout, "figure": bool(fig)}
            if shots_dir:
                if stdout.strip():
                    p = shots_dir / f"cell{count:02d}_out.png"
                    p.write_bytes(render_terminal_shot(
                        stdout.rstrip("\n"), command=shot_command or f"python {src_path.name}",
                        cwd=shot_cwd, urk_mode="none", show_banner=False, width=1500))
                    entry["shot"] = str(p)
                if fig:
                    p = shots_dir / f"cell{count:02d}_fig.png"
                    p.write_bytes(fig)
                    entry["figure_png"] = str(p)
            if err:
                entry["error"] = err
                error = err
            summary.append(entry)
    finally:
        os.chdir(prev)
    nb = {"cells": nb_cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python",
                                         "version": ".".join(map(str, sys.version_info[:3]))}},
          "nbformat": 4, "nbformat_minor": 5}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    return {"ok": error is None, "out": str(out_path), "cells": summary, "error": error}
