# Ex 4 — Code explanation (teaching cues)
*Descriptive statistics & correlation · fanspeed.csv · URK24CS1021*

> Mam wants this to sound like **you teaching a junior**, not you reading the code.
> So the order is always: **the question first, why this measure and not another, then the code.**
> Glance at these cues, look at the output on screen, say it in your own words. ~6-7 min.

**Open with** — who you are, reg no URK24CS1021, Experiment 4.
Then the hook, in your own words: *"Same fan dataset as Experiment 2 — 100 readings,
temperature and the fan speed observed at it. Last time I looked at the rows. This time
I never look at a single row. The whole idea of statistics is to replace a hundred numbers
with about six that tell you the same story: where the data sits, how spread out it is,
and whether the two columns move together. Then I plot it, because a number can lie about
a shape and a picture can't."*

---

**Where the data sits — mean, median, mode (Q1–Q3)**
- Question: *what's a typical reading?*
- Do mean and median together, because the interesting thing isn't either number — it's
  **the gap between them**. They're almost identical here, and that tells you the data is
  roughly symmetric. If the mean were far above the median you'd know a few big values
  were dragging it up. That's the entire reason you compute both.
- Why the median resists that: it only cares about the middle position, so one enormous
  outlier moves it by one place. The mean gets pulled the whole way.
- Then the honest bit on mode: **every one of the 100 readings is unique**, so `mode()`
  comes back with all 100 values tied. That's not a bug — it's what mode means on
  continuous data, and the lesson is that **mode is a categorical tool.** So I bin
  temperature into Low/Mid/High with `pd.cut` and take the mode of *that*, which is the
  answer the question is actually after.

**How spread out it is — variance, std, range, IQR (Q4–Q7)**
- Question: *are the readings tightly packed or all over the place?*
- Variance first: average squared distance from the mean. Ask out loud why it's *squared* —
  because plain distances cancel out to zero, half above and half below.
- Then the payoff: **standard deviation is just the square root of variance**, and the
  reason you report std instead is **units**. Variance of fan speed is in "fan-speed
  squared", which means nothing. Std is in fan speed. Point at the check table where
  std² lands back on the variance — that's the relationship, shown rather than claimed.
- Range is max − min: one line, and one weakness — it's decided entirely by the two most
  extreme readings, so a single bad sensor value defines it.
- **IQR fixes exactly that.** It's the range of the middle 50%, so it ignores the tails.
  Then the 1.5×IQR rule: anything more than one and a half IQRs past the quartiles is
  flagged as an outlier. Read out the fence numbers and the count you actually got —
  don't claim a number you haven't looked at.
- Fan speed has a much bigger variance than temperature. Say why that's expected before
  someone asks: the two columns are on different scales, so comparing their spreads
  directly isn't very meaningful. That's a real caveat, not a footnote.

**Do the columns move together — correlation (Q8–Q10)**
- Question: *when temperature goes up, does fan speed follow?*
- Explain the scale once: −1 is a perfect downward line, 0 is no linear relationship,
  +1 is a perfect upward line. Ours is about 0.985 — very strong and positive.
- **Pearson vs Spearman is the concept worth the time.** Pearson measures how close the
  points are to a *straight line*. Spearman throws away the values and keeps only the
  *rank order*, then measures that. Here they're almost identical, which tells you the
  relationship is both increasing *and* basically straight.
- Say when they'd disagree, because that's what makes the pair useful: a curve that keeps
  going up — doubling every step, say — scores near 1 on Spearman and noticeably lower on
  Pearson. If you ever see those two numbers far apart, that's your signal the
  relationship is real but not a straight line.
- The caveat, said once and said plainly: **correlation is not causation.** These two
  really are causally linked, but the number alone could never prove that.

**Seeing it — heatmap, regression, box, histogram, pair plot (Q11–Q15)**
- Frame the section: *the numbers said 0.985. Now let's check the picture agrees.*
- **Heatmap:** it colours the correlation matrix so strong pairs jump out. Be upfront —
  with only two numerical columns this matrix is 2×2 and the diagonal is 1.0 by
  definition, so there's exactly one real number in it. On a dataset with twenty columns
  this is the plot that saves you reading four hundred numbers.
- **Regplot:** scatter plus the fitted line in one call. Point at it: the points hug the
  line, which is what a 0.985 is *supposed* to look like. That's the check — a
  correlation number with no plot behind it is a claim you haven't verified.
- **Box plot:** ties straight back to the IQR you computed. The box is Q1 to Q3, the line
  is the median, the whiskers stop at the 1.5×IQR fences, and any dot beyond them is an
  outlier. Say whether you see any, and match it against the count you printed earlier.
- **Histogram:** the shape question. Don't eyeball it — I printed the skewness, so read
  the number and then say what it means: near zero is symmetric, positive means a tail to
  the right, negative to the left. The KDE curve on top is a smoothed version of the same
  bars.
- **Pair plot:** every numerical column against every other, with each column's own
  distribution down the diagonal. Say what it's *for* — on a wide dataset it's the first
  thing you run, one glance and you know which pairs are worth investigating. With two
  columns here it's a 2×2 grid, so it's the technique on show, not the finding.

---

**Close with** — the workflow, not the function names:
*where does it sit (mean/median/mode) → how spread out is it (variance/std/range/IQR) →
do the columns move together (Pearson/Spearman) → and does a plot agree with the numbers.*
Then the one line to leave them with: every summary statistic throws information away on
purpose — that's why you always plot it before you trust it.
