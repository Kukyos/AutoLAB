# Ex 8 - Recommender System
# URK24CS1021

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sns.set_theme(style="white")
pd.set_option("display.width", 110)
pd.set_option("display.max_columns", 20)
pd.set_option("display.max_colwidth", 48)

# 1. Create the DataFrame
productivity_apps_data = {
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

apps = pd.DataFrame(productivity_apps_data)
print("Shape:", apps.shape)
print(apps[['app_name', 'function']])

# 2. Look at the text we have to work with
print(apps.loc[0].to_string())
print()
print("Missing values:", apps.isnull().sum().sum())
print("Average description length:",
      round(apps["description"].str.split().str.len().mean(), 1), "words")

# 3. Combine the features into one field
# a recommender can only compare what it can see, so the description and the
# function tags go into one string per app. lowercase so "Focus" and "focus"
# count as the same word
apps["combined"] = (apps["description"] + " " + apps["function"]).str.lower()
print(apps.loc[6, "app_name"], "->")
print(apps.loc[6, "combined"])

# 4. TF-IDF: turn the text into numbers
# TF = how often a word appears in this app's text
# IDF = how rare that word is across all the apps
# so "app" (in many rows) is worth little and "pomodoro" (in one) is worth a lot
tfidf = TfidfVectorizer(stop_words="english")
matrix = tfidf.fit_transform(apps["combined"])

print("TF-IDF matrix shape (apps x words):", matrix.shape)
words = tfidf.get_feature_names_out()
print("First 12 words:", list(words[:12]))

# the heaviest words for one app
row = pd.Series(matrix[6].toarray()[0], index=words)
print("\nHeaviest words for", apps.loc[6, "app_name"])
print(row.sort_values(ascending=False).head(5).round(3).to_string())

# 5. Cosine similarity between every pair of apps
# cosine similarity = the angle between two TF-IDF vectors.
# 1 = same direction (same words), 0 = nothing in common
sim = cosine_similarity(matrix)
sim_df = pd.DataFrame(sim, index=apps["app_name"], columns=apps["app_name"])

print("Similarity matrix shape:", sim.shape)
print("Diagonal (each app against itself):", np.diag(sim).round(2)[:3], "...")
print()
print(sim_df.round(2).to_string())

plt.figure(figsize=(8, 6.2))
sns.heatmap(sim_df, annot=True, fmt=".2f", cmap="YlGnBu", cbar=False, annot_kws={"size": 7})
plt.title("How similar is each app to every other app?")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

# 6. The recommender function
def recommend(app_name, n=3):
    # find the app, take its row of similarities, sort high to low,
    # skip position 0 because that is the app itself
    i = apps.index[apps["app_name"] == app_name][0]
    order = sim[i].argsort()[::-1][1:n + 1]
    out = apps.loc[order, ["app_name", "function"]].copy()
    out["similarity"] = sim[i][order].round(3)
    return out.reset_index(drop=True)

print(recommend("Todoist"))

# 7. Test the recommender on sample apps
for name in ["Forest", "Evernote", "Habitica", "RescueTime"]:
    print("If you liked", name + ":")
    print(recommend(name).to_string(index=False))
    print()

# 8. Recommend from more than one liked app
# a real user likes several things, so average the similarity rows of the
# liked apps and recommend what is closest to the whole taste, not one app
liked = ["Todoist", "Notion"]
idx = apps.index[apps["app_name"].isin(liked)]
taste = sim[idx].mean(axis=0)
taste[idx] = -1  # never recommend what they already have
top = taste.argsort()[::-1][:3]
print("User liked:", liked)
print(pd.DataFrame({"app_name": apps.loc[top, "app_name"].values,
                    "score": taste[top].round(3)}).to_string(index=False))

# 9. Interpretations
best = sim.copy()
np.fill_diagonal(best, 0)
a, b = np.unravel_index(best.argmax(), best.shape)
print("INTERPRETATIONS")
print("-" * 66)
print("1. This is content-based filtering: the recommender never looks at")
print("   other users. It only compares what the apps themselves say.")
print("2. The most similar pair in the whole table is", apps.loc[a, "app_name"],
      "and", apps.loc[b, "app_name"] + ",")
print("   at", round(best[a, b], 3), "- they share the words task, management and app.")
print("3. Forest and Focus Keeper are both focus timers, but they only score")
print("   0.2 because the texts share the two words focus and timer. Forest")
print("   talks about trees and phones, Focus Keeper about pomodoro and")
print("   breaks, and TF-IDF cannot know those mean the same thing. It")
print("   matches words, not meaning. Habitica shows the same problem: its")
print("   best match, Notion, scores only 0.07 off a single shared word.")
print("4. Most scores are low because 10 short texts share few words. A")
print("   score of 0.1 here is not bad, it is just a small vocabulary.")
print("5. Weakness: a brand new app with no description cannot be placed,")
print("   and the system can only ever suggest more of the same - it will")
print("   never surprise the user the way a collaborative recommender can.")