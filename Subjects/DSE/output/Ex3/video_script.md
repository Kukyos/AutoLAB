# Ex 3 — Code explanation (teaching cues)
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
