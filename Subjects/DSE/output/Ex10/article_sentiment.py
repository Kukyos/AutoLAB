# Ex 10 - Sentiment Analysis
# URK24CS1021

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sns.set_theme(style="whitegrid")
pd.set_option("display.width", 110)
pd.set_option("display.max_columns", 20)
pd.set_option("display.max_colwidth", 60)

vader = SentimentIntensityAnalyzer()

# 1. Import the dataset
df = pd.read_csv("bbc-text-1.csv")
print("Rows loaded:", len(df))
print(df.head())

# 2. Information, shape and column names
df.info()
print("\nShape (rows, columns):", df.shape)
print("Columns:", list(df.columns))

# 3. Missing values, duplicates and article length
print("Missing values:", df.isnull().sum().sum())
print("Duplicate rows:", df.duplicated().sum())
words = df["text"].str.split().str.len()
print("\nWords per article:")
print(words.describe().round(0).to_string())

# 4. Cleaning
# the same article appears more than once in the file. counting it twice would
# weight its category twice, so the copies go
before = len(df)
df = df.drop_duplicates().reset_index(drop=True)
print("Rows before:", before, "-> after:", len(df))
print("\nArticles per category:")
print(df["category"].value_counts().to_string())

# 5. How VADER scores a sentence
tests = ["The team played brilliantly and won the final",
         "The team did not play well and lost the final",
         "The match is on Saturday at the national stadium"]
for t in tests:
    s = vader.polarity_scores(t)
    print(t)
    print("   neg", s["neg"], "| neu", s["neu"], "| pos", s["pos"],
          "| compound", s["compound"])

# 6. Why a whole article cannot be scored in one go
# compound is squashed into -1..+1, so a long text full of emotional words
# just pins itself to the end of the scale
sample = df.sample(300, random_state=1021)
whole = sample["text"].map(lambda t: vader.polarity_scores(t)["compound"])
print("Articles scoring beyond +-0.95 when scored whole:",
      round((whole.abs() > 0.95).mean() * 100, 1), "%")
print(whole.round(2).describe().to_string())

# 7. Scoring every article in chunks
# fix: cut each article into pieces of 25 words, score every piece, and
# average. the text has no full stops left in it, so word chunks are the
# only way to split it
def article_score(text, size=25):
    w = text.split()
    parts = [" ".join(w[i:i + size]) for i in range(0, len(w), size)]
    return np.mean([vader.polarity_scores(p)["compound"] for p in parts])

df["score"] = df["text"].map(article_score)
print(df["score"].describe().round(3).to_string())

# 8. Positive, negative or neutral
# +-0.05 is the cut-off VADER recommends
def label(score):
    if score >= 0.05:
        return "positive"
    if score <= -0.05:
        return "negative"
    return "neutral"

df["sentiment"] = df["score"].map(label)
counts = df["sentiment"].value_counts()
print(counts.to_string())
print()
print((counts / len(df) * 100).round(1).astype(str).add(" %").to_string())

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
sns.histplot(df["score"], bins=40, kde=True, color="#4C72B0", ax=ax[0])
ax[0].axvline(0.05, color="grey", linestyle="--")
ax[0].axvline(-0.05, color="grey", linestyle="--")
ax[0].set_title("Sentiment score of each article")
ax[0].set_xlabel("average compound score")
order = ["positive", "neutral", "negative"]
sns.countplot(data=df, x="sentiment", order=order, hue="sentiment",
              palette=["#55A868", "#8C8C8C", "#C44E52"], legend=False, ax=ax[1])
ax[1].set_title("How many articles of each kind")
plt.tight_layout()
plt.show()

# 9. Sentiment by category
by_cat = df.groupby("category")["score"].agg(["mean", "median", "std"]).round(3)
print(by_cat.sort_values("mean", ascending=False).to_string())

share = (pd.crosstab(df["category"], df["sentiment"], normalize="index") * 100).round(1)
share = share[["positive", "neutral", "negative"]]
print("\nShare of each sentiment inside each category (%):")
print(share.to_string())

fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
sns.boxplot(data=df, x="category", y="score", hue="category", palette="Set2",
            legend=False, ax=ax[0])
ax[0].axhline(0, color="grey", linestyle="--")
ax[0].set_title("Score spread per category")
share.plot(kind="bar", stacked=True, ax=ax[1], rot=0,
           color=["#55A868", "#8C8C8C", "#C44E52"])
ax[1].set_title("Positive / neutral / negative share (%)")
ax[1].legend(loc="lower right", fontsize=8)
plt.tight_layout()
plt.show()

# 10. The most positive and most negative articles
top = df.nlargest(3, "score")
bottom = df.nsmallest(3, "score")
print("MOST POSITIVE")
for _, r in top.iterrows():
    print(f"  {r['score']:+.3f}  [{r['category']}]  {r['text'][:110]}...")
print("\nMOST NEGATIVE")
for _, r in bottom.iterrows():
    print(f"  {r['score']:+.3f}  [{r['category']}]  {r['text'][:110]}...")

# 11. Which words are doing the work?
# VADER's dictionary of word -> valence. count how often each of those words
# shows up in the articles, per category, to see what drives the scores
lex = vader.lexicon
def top_words(cat, sign, n=6):
    c = Counter(w for t in df.loc[df["category"] == cat, "text"]
                for w in t.split() if w in lex and lex[w] * sign > 0)
    return [w for w, _ in c.most_common(n)]

for cat in sorted(df["category"].unique()):
    print(cat.ljust(14), "+", top_words(cat, 1))
    print(" " * 14, "-", top_words(cat, -1))

# 12. Interpretations
m = by_cat["mean"]
print("INTERPRETATIONS")
print("-" * 66)
print("1. The dataset has topic labels (sport, tech, ...) but no sentiment")
print("   labels, so VADER was used as it needs no training. The price is")
print("   that there is no accuracy to report, only results to read.")
print("2. Scoring a whole article fails: question 6 shows", round((whole.abs() > 0.95).mean() * 100),
      "% of long texts")
print("   pinned to the ends of the scale. Averaging 25-word chunks spreads")
print("   the scores out into a usable range.")
print("3. Overall", round(counts["positive"] / len(df) * 100), "% of articles are positive,",
      round(counts["negative"] / len(df) * 100), "% negative and",
      round(counts["neutral"] / len(df) * 100), "% neutral. But the average score is only",
      round(df["score"].mean(), 3), ".")
print("   The neutral band (+-0.05) is narrow and most articles sit just")
print("   above it, so \"positive\" here mostly means mildly positive.")
print("4. The most positive category is", m.idxmax(), "(mean", m.max(), ") and the least")
print("   positive is", m.idxmin(), "(mean", m.min(), ").")
print("5. Question 11 shows why. Entertainment and sport are built from")
print("   best, won, awards and win. Business mixes growth and profits with")
print("   cut, debt and deficit, and politics mixes support with war,")
print("   accused and denied, so the good and bad words cancel out.")
print("6. Limit: VADER scores words, not meaning. It counts the word like")
print("   as positive even when it only means similar to, and no is the top")
print("   negative word in every category.")
print("   It also cannot tell that a win in sport is a loss for another team.")
print("7. A \"positive\" score here means the language is positive, not that")
print("   the event was. That is the difference between sentiment of the")
print("   text and sentiment about the subject.")