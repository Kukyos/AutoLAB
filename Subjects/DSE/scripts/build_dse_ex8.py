"""Build Cleo's DSE Ex-8 record (content-based recommender system on the
productivity apps data from the question bank, row 20). Content only - the
docx/notebook/screenshot machinery lives in dse_record.py.

    python Subjects/DSE/scripts/build_dse_ex8.py
"""
from __future__ import annotations

from pathlib import Path

from dse_record import Exp, build

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "output" / "Ex8"

TITLE = "RECOMMENDER SYSTEM"
DATE = "02/10/2026"

AIM = ("To build a content-based recommender system in Python that suggests similar "
       "items by comparing their text descriptions, using TF-IDF vectors and cosine "
       "similarity.")

DESC = (
    "A recommender system predicts what a user is likely to want next. A content-based "
    "recommender does it without looking at other users at all: it describes every item "
    "by its own features, and recommends the items whose features look most like the "
    "ones the user already liked. Here every app is described by two text fields, what "
    "it does and its function tags. TF-IDF turns that text into a vector of numbers, "
    "giving a high weight to words that are frequent in one app's text but rare across "
    "the other apps, so shared filler words count for little. Cosine similarity then "
    "measures the angle between two vectors: 1 means the texts point in exactly the "
    "same direction, 0 means they share no words at all."
)

DATA = '''productivity_apps_data = {
    'app_name': [
        'Todoist', 'Evernote', 'Forest', 'Toggl Track', 'Google Keep',
        'Microsoft To Do', 'Focus Keeper', 'Notion', 'RescueTime', 'Habitica'
    ],
    'description': [
        'Task management app with projects, labels, and due dates for organizing work',
        'Note-taking app that syncs across devices with web clipping and organization',
        'Focus timer that grows virtual trees when you avoid using your phone',
        'Time tracking tool for monitoring how you spend time on different activities',
        'Simple note-taking service with color coding, labels, and checklist features',
        'Task management app with smart suggestions and integration with Office 365',
        'Pomodoro timer that uses 25-minute work sessions with short breaks',
        'All-in-one workspace for notes, tasks, databases, and collaborative work',
        'Automatic time tracking that shows how you spend time on websites and apps',
        'Gamified habit-building app that turns tasks into RPG game elements'
    ],
    'function': [
        'Task Management, Organization, Productivity',
        'Note-taking, Organization, Sync',
        'Focus, Time Management, Gamification',
        'Time Tracking, Analytics, Productivity',
        'Quick Notes, Checklists, Simple',
        'Task Management, Microsoft Integration',
        'Pomodoro Technique, Focus, Timer',
        'All-in-one, Workspace, Collaboration',
        'Automatic Tracking, Analytics, Focus',
        'Gamification, Habits, Motivation'
    ]
}
'''

QUESTION = (
    "Dataset (from the question bank, S.No 20, URK24CS1021):\n" + DATA +
    "\n\u2022 Create a DataFrame from the given data and display it.\n"
    "\u2022 Combine the text features of each app into one field.\n"
    "\u2022 Convert the text into numbers with TF-IDF.\n"
    "\u2022 Compute the cosine similarity between every pair of apps.\n"
    "\u2022 Build a function that recommends the most similar apps for a given app.\n"
    "\u2022 Test the recommender on sample apps and document your interpretations."
)

PREAMBLE = (
    "import numpy as np\n"
    "import pandas as pd\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n"
    "from sklearn.feature_extraction.text import TfidfVectorizer\n"
    "from sklearn.metrics.pairwise import cosine_similarity\n\n"
    'sns.set_theme(style="white")\n'
    'pd.set_option("display.width", 110)\n'
    'pd.set_option("display.max_columns", 20)\n'
    'pd.set_option("display.max_colwidth", 48)\n\n'
)

SECTIONS: list[tuple[str, str]] = [
    ("1. Create the DataFrame",
     DATA + "\n"
     "apps = pd.DataFrame(productivity_apps_data)\n"
     'print("Shape:", apps.shape)\n'
     "print(apps[['app_name', 'function']])"),

    ("2. Look at the text we have to work with",
     'print(apps.loc[0].to_string())\n'
     'print()\n'
     'print("Missing values:", apps.isnull().sum().sum())\n'
     'print("Average description length:",\n'
     '      round(apps["description"].str.split().str.len().mean(), 1), "words")'),

    ("3. Combine the features into one field",
     '# a recommender can only compare what it can see, so the description and the\n'
     '# function tags go into one string per app. lowercase so "Focus" and "focus"\n'
     '# count as the same word\n'
     'apps["combined"] = (apps["description"] + " " + apps["function"]).str.lower()\n'
     'print(apps.loc[6, "app_name"], "->")\n'
     'print(apps.loc[6, "combined"])'),

    ("4. TF-IDF: turn the text into numbers",
     '# TF = how often a word appears in this app\'s text\n'
     '# IDF = how rare that word is across all the apps\n'
     '# so "app" (in many rows) is worth little and "pomodoro" (in one) is worth a lot\n'
     'tfidf = TfidfVectorizer(stop_words="english")\n'
     'matrix = tfidf.fit_transform(apps["combined"])\n\n'
     'print("TF-IDF matrix shape (apps x words):", matrix.shape)\n'
     'words = tfidf.get_feature_names_out()\n'
     'print("First 12 words:", list(words[:12]))\n\n'
     '# the heaviest words for one app\n'
     'row = pd.Series(matrix[6].toarray()[0], index=words)\n'
     'print("\\nHeaviest words for", apps.loc[6, "app_name"])\n'
     'print(row.sort_values(ascending=False).head(5).round(3).to_string())'),

    ("5. Cosine similarity between every pair of apps",
     '# cosine similarity = the angle between two TF-IDF vectors.\n'
     '# 1 = same direction (same words), 0 = nothing in common\n'
     'sim = cosine_similarity(matrix)\n'
     'sim_df = pd.DataFrame(sim, index=apps["app_name"], columns=apps["app_name"])\n\n'
     'print("Similarity matrix shape:", sim.shape)\n'
     'print("Diagonal (each app against itself):", np.diag(sim).round(2)[:3], "...")\n'
     'print()\n'
     'print(sim_df.round(2).to_string())\n\n'
     'plt.figure(figsize=(8, 6.2))\n'
     'sns.heatmap(sim_df, annot=True, fmt=".2f", cmap="YlGnBu", cbar=False, annot_kws={"size": 7})\n'
     'plt.title("How similar is each app to every other app?")\n'
     'plt.xticks(rotation=45, ha="right")\n'
     'plt.tight_layout()\n'
     'plt.show()'),

    ("6. The recommender function",
     'def recommend(app_name, n=3):\n'
     '    # find the app, take its row of similarities, sort high to low,\n'
     '    # skip position 0 because that is the app itself\n'
     '    i = apps.index[apps["app_name"] == app_name][0]\n'
     '    order = sim[i].argsort()[::-1][1:n + 1]\n'
     '    out = apps.loc[order, ["app_name", "function"]].copy()\n'
     '    out["similarity"] = sim[i][order].round(3)\n'
     '    return out.reset_index(drop=True)\n\n'
     'print(recommend("Todoist"))'),

    ("7. Test the recommender on sample apps",
     'for name in ["Forest", "Evernote", "Habitica", "RescueTime"]:\n'
     '    print("If you liked", name + ":")\n'
     '    print(recommend(name).to_string(index=False))\n'
     '    print()'),

    ("8. Recommend from more than one liked app",
     '# a real user likes several things, so average the similarity rows of the\n'
     '# liked apps and recommend what is closest to the whole taste, not one app\n'
     'liked = ["Todoist", "Notion"]\n'
     'idx = apps.index[apps["app_name"].isin(liked)]\n'
     'taste = sim[idx].mean(axis=0)\n'
     'taste[idx] = -1  # never recommend what they already have\n'
     'top = taste.argsort()[::-1][:3]\n'
     'print("User liked:", liked)\n'
     'print(pd.DataFrame({"app_name": apps.loc[top, "app_name"].values,\n'
     '                    "score": taste[top].round(3)}).to_string(index=False))'),

    ("9. Interpretations",
     'best = sim.copy()\n'
     'np.fill_diagonal(best, 0)\n'
     'a, b = np.unravel_index(best.argmax(), best.shape)\n'
     'print("INTERPRETATIONS")\n'
     'print("-" * 66)\n'
     'print("1. This is content-based filtering: the recommender never looks at")\n'
     'print("   other users. It only compares what the apps themselves say.")\n'
     'print("2. The most similar pair in the whole table is", apps.loc[a, "app_name"],\n'
     '      "and", apps.loc[b, "app_name"] + ",")\n'
     'print("   at", round(best[a, b], 3), "- they share the words task, management and app.")\n'
     'print("3. Forest and Focus Keeper are both focus timers, but they only score")\n'
     'print("   0.2 because the texts share the two words focus and timer. Forest")\n'
     'print("   talks about trees and phones, Focus Keeper about pomodoro and")\n'
     'print("   breaks, and TF-IDF cannot know those mean the same thing. It")\n'
     'print("   matches words, not meaning. Habitica shows the same problem: its")\n'
     'print("   best match, Notion, scores only 0.07 off a single shared word.")\n'
     'print("4. Most scores are low because 10 short texts share few words. A")\n'
     'print("   score of 0.1 here is not bad, it is just a small vocabulary.")\n'
     'print("5. Weakness: a brand new app with no description cannot be placed,")\n'
     'print("   and the system can only ever suggest more of the same - it will")\n'
     'print("   never surprise the user the way a collaborative recommender can.")'),
]

NB_CELLS = [
    ("md", "# Ex 8 \u2014 Recommender System\n\n"
           "**Content-based filtering with TF-IDF and cosine similarity**  \n"
           "**Data:** productivity apps (S.No 20)  \n**Reg No:** URK24CS1021"),
    ("code",
     "import numpy as np\n"
     "import pandas as pd\n"
     "import matplotlib.pyplot as plt\n"
     "import seaborn as sns\n"
     "from sklearn.feature_extraction.text import TfidfVectorizer\n"
     "from sklearn.metrics.pairwise import cosine_similarity\n\n"
     + DATA + "\n"
     "apps = pd.DataFrame(productivity_apps_data)\n"
     "apps"),
    ("md", "### One text field per app"),
    ("code",
     "# lowercase so Focus and focus are the same word\n"
     'apps["combined"] = (apps["description"] + " " + apps["function"]).str.lower()\n'
     'apps.loc[6, "combined"]'),
    ("md", "### Text to numbers: TF-IDF"),
    ("code",
     "# common words get a low weight, words only one app uses get a high one\n"
     'tfidf = TfidfVectorizer(stop_words="english")\n'
     'matrix = tfidf.fit_transform(apps["combined"])\n'
     "matrix.shape"),
    ("code",
     "words = tfidf.get_feature_names_out()\n"
     "row = pd.Series(matrix[6].toarray()[0], index=words)\n"
     "row.sort_values(ascending=False).head(5)"),
    ("md", "### How close is every app to every other app?"),
    ("code",
     "sim = cosine_similarity(matrix)\n"
     'sim_df = pd.DataFrame(sim, index=apps["app_name"], columns=apps["app_name"])\n'
     "sim_df.round(2)"),
    ("code",
     "plt.figure(figsize=(8, 6))\n"
     'sns.heatmap(sim_df, annot=True, fmt=".2f", cmap="YlGnBu", cbar=False)\n'
     "plt.show()"),
    ("md", "### The recommender"),
    ("code",
     "def recommend(app_name, n=3):\n"
     "    # row of similarities, high to low, skip position 0 (the app itself)\n"
     '    i = apps.index[apps["app_name"] == app_name][0]\n'
     "    order = sim[i].argsort()[::-1][1:n + 1]\n"
     '    out = apps.loc[order, ["app_name", "function"]].copy()\n'
     '    out["similarity"] = sim[i][order].round(3)\n'
     "    return out.reset_index(drop=True)\n\n"
     'recommend("Todoist")'),
    ("code", 'recommend("Forest")'),
    ("code", 'recommend("Habitica")'),
    ("md", "### A user who likes more than one app"),
    ("code",
     'liked = ["Todoist", "Notion"]\n'
     'idx = apps.index[apps["app_name"].isin(liked)]\n'
     "taste = sim[idx].mean(axis=0)\n"
     "taste[idx] = -1  # not the ones they already have\n"
     "top = taste.argsort()[::-1][:3]\n"
     'pd.DataFrame({"app": apps.loc[top, "app_name"].values, "score": taste[top].round(3)})'),
]

# the video is made separately now (videos/ex8-...), this file only holds the record
VIDEO = "# Ex 8 \u2014 video\nSee videos/ex8-recommender/SCRIPT.md (written after the real run).\n"


def main() -> None:
    build(Exp(
        num=8, title=TITLE, date=DATE, out=OUT, aim=AIM,
        desc_label="Description (About Recommender Systems)", desc=DESC, question=QUESTION,
        preamble=PREAMBLE, sections=SECTIONS, nb_cells=NB_CELLS, video=VIDEO,
        script_name="app_recommender.py", notebook_name="Ex8_Recommender.ipynb",
        shot_command="python app_recommender.py", shot_cwd=r"C:\DSE\Ex8",
    ))


if __name__ == "__main__":
    main()
