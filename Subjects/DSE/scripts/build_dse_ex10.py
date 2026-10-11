"""Build Cleo's DSE Ex-10 record (sentiment analysis on the article dataset,
VADER lexicon scoring). Content only.

    python Subjects/DSE/scripts/build_dse_ex10.py
"""
from __future__ import annotations

from pathlib import Path

from dse_record import Exp, build

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "output" / "Ex10"

TITLE = "SENTIMENT ANALYSIS"
DATE = "09/10/2026"

AIM = ("To perform sentiment analysis in Python on a collection of news articles, "
       "scoring each article as positive, negative or neutral with the VADER lexicon "
       "and comparing how sentiment differs between the article categories.")

DESC = (
    "Sentiment analysis decides whether a piece of text is positive, negative or "
    "neutral. This experiment uses the lexicon approach: VADER holds a dictionary of "
    "about 7,500 words, each with a valence score from \u22124 (terrible) to +4 "
    "(excellent), and adds rules for negation (\u201cnot good\u201d), intensifiers "
    "(\u201cvery good\u201d) and capitalisation. A piece of text is scored by combining "
    "the valence of its words into one compound score between \u22121 and +1. By "
    "convention a compound score of +0.05 or more is positive, \u22120.05 or less is "
    "negative, and anything in between is neutral. The dataset has no sentiment "
    "labels, so the method needs no training, but the result can only be judged by "
    "reading, not by an accuracy number."
)

QUESTION = (
    "Dataset: Article Dataset 2 (BBC news articles)\n"
    "(https://www.kaggle.com/datasets/amunsentom/article-dataset-2)\n"
    "Perform sentiment analysis for the given dataset. Refer to Kaggle programs for "
    "reference (from the code section).\n"
    "\u2022 Import the dataset and review it: first rows, information, shape, column "
    "names, missing values, duplicates.\n"
    "\u2022 Clean the data.\n"
    "\u2022 Score the sentiment of every article.\n"
    "\u2022 Classify each article as positive, negative or neutral.\n"
    "\u2022 Visualise the sentiment distribution and compare it across categories.\n"
    "\u2022 Document your interpretations."
)

PREAMBLE = (
    "import numpy as np\n"
    "import pandas as pd\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n"
    "from collections import Counter\n"
    "from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer\n\n"
    'sns.set_theme(style="whitegrid")\n'
    'pd.set_option("display.width", 110)\n'
    'pd.set_option("display.max_columns", 20)\n'
    'pd.set_option("display.max_colwidth", 60)\n\n'
    "vader = SentimentIntensityAnalyzer()\n\n"
)

SECTIONS: list[tuple[str, str]] = [
    ("1. Import the dataset",
     'df = pd.read_csv("bbc-text-1.csv")\n'
     'print("Rows loaded:", len(df))\n'
     "print(df.head())"),

    ("2. Information, shape and column names",
     "df.info()\n"
     'print("\\nShape (rows, columns):", df.shape)\n'
     'print("Columns:", list(df.columns))'),

    ("3. Missing values, duplicates and article length",
     'print("Missing values:", df.isnull().sum().sum())\n'
     'print("Duplicate rows:", df.duplicated().sum())\n'
     'words = df["text"].str.split().str.len()\n'
     'print("\\nWords per article:")\n'
     'print(words.describe().round(0).to_string())'),

    ("4. Cleaning",
     '# the same article appears more than once in the file. counting it twice would\n'
     '# weight its category twice, so the copies go\n'
     'before = len(df)\n'
     'df = df.drop_duplicates().reset_index(drop=True)\n'
     'print("Rows before:", before, "-> after:", len(df))\n'
     'print("\\nArticles per category:")\n'
     'print(df["category"].value_counts().to_string())'),

    ("5. How VADER scores a sentence",
     'tests = ["The team played brilliantly and won the final",\n'
     '         "The team did not play well and lost the final",\n'
     '         "The match is on Saturday at the national stadium"]\n'
     'for t in tests:\n'
     '    s = vader.polarity_scores(t)\n'
     '    print(t)\n'
     '    print("   neg", s["neg"], "| neu", s["neu"], "| pos", s["pos"],\n'
     '          "| compound", s["compound"])'),

    ("6. Why a whole article cannot be scored in one go",
     '# compound is squashed into -1..+1, so a long text full of emotional words\n'
     '# just pins itself to the end of the scale\n'
     'sample = df.sample(300, random_state=1021)\n'
     'whole = sample["text"].map(lambda t: vader.polarity_scores(t)["compound"])\n'
     'print("Articles scoring beyond +-0.95 when scored whole:",\n'
     '      round((whole.abs() > 0.95).mean() * 100, 1), "%")\n'
     'print(whole.round(2).describe().to_string())'),

    ("7. Scoring every article in chunks",
     '# fix: cut each article into pieces of 25 words, score every piece, and\n'
     '# average. the text has no full stops left in it, so word chunks are the\n'
     '# only way to split it\n'
     'def article_score(text, size=25):\n'
     '    w = text.split()\n'
     '    parts = [" ".join(w[i:i + size]) for i in range(0, len(w), size)]\n'
     '    return np.mean([vader.polarity_scores(p)["compound"] for p in parts])\n\n'
     'df["score"] = df["text"].map(article_score)\n'
     'print(df["score"].describe().round(3).to_string())'),

    ("8. Positive, negative or neutral",
     '# +-0.05 is the cut-off VADER recommends\n'
     'def label(score):\n'
     '    if score >= 0.05:\n'
     '        return "positive"\n'
     '    if score <= -0.05:\n'
     '        return "negative"\n'
     '    return "neutral"\n\n'
     'df["sentiment"] = df["score"].map(label)\n'
     'counts = df["sentiment"].value_counts()\n'
     'print(counts.to_string())\n'
     'print()\n'
     'print((counts / len(df) * 100).round(1).astype(str).add(" %").to_string())\n\n'
     'fig, ax = plt.subplots(1, 2, figsize=(11, 4))\n'
     'sns.histplot(df["score"], bins=40, kde=True, color="#4C72B0", ax=ax[0])\n'
     'ax[0].axvline(0.05, color="grey", linestyle="--")\n'
     'ax[0].axvline(-0.05, color="grey", linestyle="--")\n'
     'ax[0].set_title("Sentiment score of each article")\n'
     'ax[0].set_xlabel("average compound score")\n'
     'order = ["positive", "neutral", "negative"]\n'
     'sns.countplot(data=df, x="sentiment", order=order, hue="sentiment",\n'
     '              palette=["#55A868", "#8C8C8C", "#C44E52"], legend=False, ax=ax[1])\n'
     'ax[1].set_title("How many articles of each kind")\n'
     'plt.tight_layout()\n'
     'plt.show()'),

    ("9. Sentiment by category",
     'by_cat = df.groupby("category")["score"].agg(["mean", "median", "std"]).round(3)\n'
     'print(by_cat.sort_values("mean", ascending=False).to_string())\n\n'
     'share = (pd.crosstab(df["category"], df["sentiment"], normalize="index") * 100).round(1)\n'
     'share = share[["positive", "neutral", "negative"]]\n'
     'print("\\nShare of each sentiment inside each category (%):")\n'
     'print(share.to_string())\n\n'
     'fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))\n'
     'sns.boxplot(data=df, x="category", y="score", hue="category", palette="Set2",\n'
     '            legend=False, ax=ax[0])\n'
     'ax[0].axhline(0, color="grey", linestyle="--")\n'
     'ax[0].set_title("Score spread per category")\n'
     'share.plot(kind="bar", stacked=True, ax=ax[1], rot=0,\n'
     '           color=["#55A868", "#8C8C8C", "#C44E52"])\n'
     'ax[1].set_title("Positive / neutral / negative share (%)")\n'
     'ax[1].legend(loc="lower right", fontsize=8)\n'
     'plt.tight_layout()\n'
     'plt.show()'),

    ("10. The most positive and most negative articles",
     'top = df.nlargest(3, "score")\n'
     'bottom = df.nsmallest(3, "score")\n'
     'print("MOST POSITIVE")\n'
     'for _, r in top.iterrows():\n'
     '    print(f"  {r[\'score\']:+.3f}  [{r[\'category\']}]  {r[\'text\'][:110]}...")\n'
     'print("\\nMOST NEGATIVE")\n'
     'for _, r in bottom.iterrows():\n'
     '    print(f"  {r[\'score\']:+.3f}  [{r[\'category\']}]  {r[\'text\'][:110]}...")'),

    ("11. Which words are doing the work?",
     '# VADER\'s dictionary of word -> valence. count how often each of those words\n'
     '# shows up in the articles, per category, to see what drives the scores\n'
     'lex = vader.lexicon\n'
     'def top_words(cat, sign, n=6):\n'
     '    c = Counter(w for t in df.loc[df["category"] == cat, "text"]\n'
     '                for w in t.split() if w in lex and lex[w] * sign > 0)\n'
     '    return [w for w, _ in c.most_common(n)]\n\n'
     'for cat in sorted(df["category"].unique()):\n'
     '    print(cat.ljust(14), "+", top_words(cat, 1))\n'
     '    print(" " * 14, "-", top_words(cat, -1))'),

    ("12. Interpretations",
     'm = by_cat["mean"]\n'
     'print("INTERPRETATIONS")\n'
     'print("-" * 66)\n'
     'print("1. The dataset has topic labels (sport, tech, ...) but no sentiment")\n'
     'print("   labels, so VADER was used as it needs no training. The price is")\n'
     'print("   that there is no accuracy to report, only results to read.")\n'
     'print("2. Scoring a whole article fails: question 6 shows", round((whole.abs() > 0.95).mean() * 100),\n'
     '      "% of long texts")\n'
     'print("   pinned to the ends of the scale. Averaging 25-word chunks spreads")\n'
     'print("   the scores out into a usable range.")\n'
     'print("3. Overall", round(counts["positive"] / len(df) * 100), "% of articles are positive,",\n'
     '      round(counts["negative"] / len(df) * 100), "% negative and",\n'
     '      round(counts["neutral"] / len(df) * 100), "% neutral. But the average score is only",\n'
     '      round(df["score"].mean(), 3), ".")\n'
     'print("   The neutral band (+-0.05) is narrow and most articles sit just")\n'
     'print("   above it, so \\"positive\\" here mostly means mildly positive.")\n'
     'print("4. The most positive category is", m.idxmax(), "(mean", m.max(), ") and the least")\n'
     'print("   positive is", m.idxmin(), "(mean", m.min(), ").")\n'
     'print("5. Question 11 shows why. Entertainment and sport are built from")\n'
     'print("   best, won, awards and win. Business mixes growth and profits with")\n'
     'print("   cut, debt and deficit, and politics mixes support with war,")\n'
     'print("   accused and denied, so the good and bad words cancel out.")\n'
     'print("6. Limit: VADER scores words, not meaning. It counts the word like")\n'
     'print("   as positive even when it only means similar to, and no is the top")\n'
     'print("   negative word in every category.")\n'
     'print("   It also cannot tell that a win in sport is a loss for another team.")\n'
     'print("7. A \\"positive\\" score here means the language is positive, not that")\n'
     'print("   the event was. That is the difference between sentiment of the")\n'
     'print("   text and sentiment about the subject.")'),
]

NB_CELLS = [
    ("md", "# Ex 10 \u2014 Sentiment Analysis\n\n"
           "**Dataset:** Article Dataset 2 (BBC news)  \n"
           "**Method:** VADER lexicon scoring  \n**Reg No:** URK24CS1021"),
    ("code",
     "import numpy as np\n"
     "import pandas as pd\n"
     "import matplotlib.pyplot as plt\n"
     "import seaborn as sns\n"
     "from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer\n\n"
     "vader = SentimentIntensityAnalyzer()\n"
     'df = pd.read_csv("bbc-text-1.csv")\n'
     "df.head()"),
    ("code", "df.shape, df.isnull().sum().sum(), df.duplicated().sum()"),
    ("code",
     "# the same article is in the file more than once\n"
     "df = df.drop_duplicates().reset_index(drop=True)\n"
     'df["category"].value_counts()'),
    ("md", "### How VADER scores text"),
    ("code",
     'vader.polarity_scores("The team played brilliantly and won the final")'),
    ("code",
     'vader.polarity_scores("The team did not play well and lost the final")'),
    ("md", "### A whole article is too long to score in one go"),
    ("code",
     'sample = df.sample(300, random_state=1021)\n'
     'whole = sample["text"].map(lambda t: vader.polarity_scores(t)["compound"])\n'
     "(whole.abs() > 0.95).mean()"),
    ("code",
     "# score 25 words at a time and average\n"
     "def article_score(text, size=25):\n"
     "    w = text.split()\n"
     '    parts = [" ".join(w[i:i + size]) for i in range(0, len(w), size)]\n'
     '    return np.mean([vader.polarity_scores(p)["compound"] for p in parts])\n\n'
     'df["score"] = df["text"].map(article_score)\n'
     'df["score"].describe().round(3)'),
    ("code",
     "def label(score):\n"
     "    if score >= 0.05:\n"
     '        return "positive"\n'
     "    if score <= -0.05:\n"
     '        return "negative"\n'
     '    return "neutral"\n\n'
     'df["sentiment"] = df["score"].map(label)\n'
     'df["sentiment"].value_counts()'),
    ("code",
     'sns.histplot(df["score"], bins=40, kde=True)\n'
     "plt.show()"),
    ("md", "### Does sentiment depend on the kind of article?"),
    ("code",
     'df.groupby("category")["score"].mean().round(3).sort_values()'),
    ("code",
     'sns.boxplot(data=df, x="category", y="score")\n'
     "plt.axhline(0, color='grey', linestyle='--')\n"
     "plt.show()"),
]

VIDEO = "# Ex 10 \u2014 video\nSee videos/ex10-sentiment/SCRIPT.md (written after the real run).\n"


def main() -> None:
    build(Exp(
        num=10, title=TITLE, date=DATE, out=OUT, aim=AIM,
        desc_label="Description (About Sentiment Analysis)", desc=DESC, question=QUESTION,
        preamble=PREAMBLE, sections=SECTIONS, nb_cells=NB_CELLS, video=VIDEO,
        script_name="article_sentiment.py", notebook_name="Ex10_Sentiment.ipynb",
        shot_command="python article_sentiment.py", shot_cwd=r"C:\DSE\Ex10",
    ))


if __name__ == "__main__":
    main()
