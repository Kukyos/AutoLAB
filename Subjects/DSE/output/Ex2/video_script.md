# Ex 2 — Code explanation (teaching cues)
*Pandas on fanspeed.csv · URK24CS1021*

> Mam wants this to sound like **you teaching a junior**, not you reading the code.
> So the order is always: **the question first, why this tool and not another, then the code.**
> Glance at these cues, look at the cell on screen, say it in your own words. ~5-6 min.

**Open with** — who you are, reg no URK24CS1021, Experiment 2.
Then the hook, in your own words: *"I've got a csv of fan readings — temperature on one
side, the fan speed observed at that temperature on the other. Before I can say anything
about it I have to answer boring questions first: did it load properly, is anything
missing, what's actually in here. That's what pandas is for. A DataFrame is basically a
spreadsheet you can talk to in code — and unlike a spreadsheet, every step is written
down, so anyone can re-run exactly what I did."*

---

**1. Load it — `read_csv`**
- Question: *is the file even what I think it is?*
- Why pandas and not opening the csv by hand: 100 rows you could eyeball, a million you
  couldn't, and `read_csv` figures out the columns and the types for you.
- Then the code. Point at it: two columns, the index down the left that pandas added.

**2–3. First look — `head(10)` / `tail(8)`**
- Question: *what does a row look like, and did the whole file come in?*
- Why not just print `df`: on a big file that's a wall of text. `head` and `tail` are the
  cheap first move — and `tail` specifically catches the classic bug where a file ends
  in a blank line or a junk footer row.
- Teach the habit: **always look at the data before you compute on it.**

**4. Structure — `shape`, `columns`, `dtypes`**
- Question: *how big is it, and does pandas agree with me about the types?*
- The one that matters is `dtypes`. If a number column came in as `object`, that means
  something non-numeric snuck in and every calculation after this would be wrong or
  would crash. Checking here saves you an hour later.
- Point at it: both columns are numeric, so we're clear.

**5. Summary — `describe()`**
- Question: *what's the typical reading, and how spread out are they?*
- Why `describe` and not five separate calls: it gives count, mean, std, min, max and the
  quartiles in one line. **Count is the sneaky useful one** — if it's lower than the row
  count, that column has missing values.
- Point at it: min and max tell you the range the fan actually operated over.

**6–7. Missing values — `isnull().sum()`, then `fillna`**
- Question: *are there gaps, and what do I do about them?*
- Be honest on camera: **this dataset has no missing values**, so I plant a few on
  purpose — and I do it on `df.copy()`, not the real one. That's the actual lesson here:
  never demo a destructive operation on your live data. If I'd done it to `df`, every
  group and pivot after this would quietly be based on numbers I invented.
- `isnull()` gives True/False per cell, `.sum()` counts the Trues per column — True is 1,
  False is 0, so summing booleans *is* counting them. That trick comes up everywhere.
- Why fill with the mean and not delete the rows: deleting throws away the other column's
  good value too. Mean is the simplest defensible fill. Say the caveat — it flattens the
  spread, and for a genuinely large gap you'd want something smarter.

**8–9. Slicing — `loc` / `iloc`, and a boolean condition**
- Question: *how do I get at just the part I care about?*
- The distinction worth teaching: **`loc` is by label, `iloc` is by position.** They look
  identical on this dataset because the index happens to be 0,1,2… Say that out loud —
  the moment you sort or filter, the labels stay with their rows and the positions don't,
  and that's when people get bitten.
- Then conditional slicing: `df[df["Temperature"] > 25]`. The inside is a column of
  True/False, and the outside keeps only the True rows. Same boolean idea as cell 6.

**10. New columns — arithmetic, then `apply`**
- Question: *the column I want isn't in the file — can I make it?*
- Arithmetic first (`speed / temperature`) because it's the easy case: pandas does it to
  the whole column at once, no loop. Point out that there's no `for` anywhere.
- Then `apply` with a lambda for the case arithmetic can't do — turning a number into a
  "High"/"Low" label. Why this over a loop: it's one line, and it reads as *what* you
  want rather than *how* to walk the rows.

**11. Sorting — `sort_values(ascending=False)`**
- Question: *which readings are the extreme ones?*
- Why it's not just cosmetic: sorting is how you spot the outliers and sanity-check that
  your derived column behaved. Tie it back — notice the index is now out of order, which
  is exactly why `loc` and `iloc` stop agreeing.

**12. Grouping — `groupby(...).mean()`**
- Question: *do the High and Low groups actually differ, or did I make up that label?*
- This is the concept to slow down on: **split the rows by a category, compute one number
  per group, put it back together.** Once they get split-apply-combine, pivot tables are
  just the same idea with two categories instead of one.
- Point at it: the two group means are far apart, so the label is meaningful.

**13. Ranking — `rank(method="dense")`**
- Question: *where does each reading stand relative to the others?*
- Why the method matters: the methods only differ **on ties**. `min` gives tied rows the
  best rank, `max` the worst, `average` splits it, `dense` doesn't skip numbers after a
  tie. Say which one you'd pick and why — that's the whole question.
- Sort by the rank afterwards to show it lines up with the actual values. **Always
  sanity-check a derived column against the thing it came from.**

---

**Close with** — the workflow, not the function names:
*load it → look at it → check the types → summarise → deal with the gaps → slice to what
you care about → derive what's missing → sort, group, rank to find the pattern.*
Then: that order is the same for any dataset you'll ever open — only the column names change.
