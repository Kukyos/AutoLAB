"""Build Cleo's DSE Ex-9 record (PCA: a classification task before and after
dimensionality reduction, on the Bangalore smart building dataset). Content only.

    python Subjects/DSE/scripts/build_dse_ex9.py
"""
from __future__ import annotations

from pathlib import Path

from dse_record import Exp, build

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "output" / "Ex9"

TITLE = "DIMENSIONALITY REDUCTION USING PCA"
DATE = "01/10/2026"

AIM = ("To apply Principal Component Analysis (PCA) in Python to a high-dimensional "
       "dataset, to run the same classification task before and after the reduction, "
       "and to compare accuracy, training time and the number of features.")

DESC = (
    "A dataset with many columns is hard to visualise and slow to model, and many of the "
    "columns often say nearly the same thing. PCA (Principal Component Analysis) finds "
    "new axes, called principal components, that are combinations of the original "
    "columns. The first component points along the direction in which the data varies "
    "the most, the second along the next most, at right angles to the first, and so on. "
    "Keeping only the first few components gives a smaller dataset that holds most of the "
    "variation, and the explained variance ratio says exactly how much each component "
    "keeps. PCA only helps when the columns are correlated, because that is the "
    "redundancy it squeezes out. It is also sensitive to scale, so every column is "
    "standardised first."
)

QUESTION = (
    "Dataset: Bangalore Smart Building\n"
    "(https://www.kaggle.com/datasets/preethamgouda/banglore-smart-building)\n"
    "Review the given dataset. Perform an appropriate machine learning task before and "
    "after PCA. Compare the results.\n"
    "\u2022 Import the dataset and review it: first rows, information, shape, column "
    "names, statistical summary, missing values.\n"
    "\u2022 Prepare the data and scale the features.\n"
    "\u2022 Perform the machine learning task (classification) on the original features.\n"
    "\u2022 Apply PCA and study the explained variance.\n"
    "\u2022 Perform the same task on the PCA-reduced data.\n"
    "\u2022 Compare the results and document your interpretations."
)

PREAMBLE = (
    "import time\n"
    "import numpy as np\n"
    "import pandas as pd\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n"
    "from sklearn.model_selection import train_test_split\n"
    "from sklearn.preprocessing import StandardScaler\n"
    "from sklearn.decomposition import PCA\n"
    "from sklearn.linear_model import LogisticRegression\n"
    "from sklearn.ensemble import RandomForestClassifier\n"
    "from sklearn.metrics import accuracy_score\n\n"
    'sns.set_theme(style="whitegrid")\n'
    'pd.set_option("display.width", 110)\n'
    'pd.set_option("display.max_columns", 30)\n'
    'pd.set_option("display.max_colwidth", 18)\n\n'
    "SEED = 1021  # my reg no\n"
    "results = []  # one row per model, for the final comparison table\n\n"
)

SECTIONS: list[tuple[str, str]] = [
    ("1. Import the dataset",
     'df = pd.read_csv("building_data.csv")\n'
     'print("Rows loaded:", len(df))\n'
     "print(df.head())"),

    ("2. Information about the dataset",
     "df.info()"),

    ("3. Shape and column names",
     'print("Shape (rows, columns):", df.shape)\n'
     'for i, col in enumerate(df.columns, 1):\n'
     '    print(i, col)'),

    ("4. Statistical summary and missing values",
     "print(df.describe().round(2).T)\n"
     'print("\\nMissing values in the whole file:", df.isnull().sum().sum())\n'
     'print("Duplicate rows:", df.duplicated().sum())'),

    ("5. The target and the text columns",
     '# the task: from everything else about a building, predict its Building_Status\n'
     'print(df["Building_Status"].value_counts())\n'
     'print("\\nIf a model just guessed, it would be right about",\n'
     '      round(100 / df["Building_Status"].nunique(), 1), "% of the time")\n'
     'print("\\nCategories in the other text columns:")\n'
     'for col in ["City", "Area", "Building_Type", "Maintenance_Priority"]:\n'
     '    print(col, "->", df[col].nunique(), "values")'),

    ("6. Preparing the features",
     '# City has one value for every row, so it cannot tell two buildings apart.\n'
     '# Last_Inspection_Date is a text date, not a number the model can use.\n'
     'X = df.drop(columns=["Building_Status", "City", "Last_Inspection_Date"])\n'
     'y = df["Building_Status"]\n\n'
     '# PCA works on numbers, so the three text columns become 0/1 columns\n'
     'X = pd.get_dummies(X, columns=["Area", "Building_Type", "Maintenance_Priority"],\n'
     '                   drop_first=True).astype(float)\n'
     'print("Features before:", df.shape[1] - 1, "-> after encoding:", X.shape[1])\n'
     'print(list(X.columns))'),

    ("7. Train-test split and scaling",
     '# the test set is locked away first, so nothing below ever learns from it\n'
     'X_train, X_test, y_train, y_test = train_test_split(\n'
     '    X, y, test_size=0.2, random_state=SEED, stratify=y)\n'
     'print("Train:", X_train.shape, " Test:", X_test.shape)\n\n'
     '# PCA chases variance, and Electricity_Bill is in the tens of thousands while\n'
     '# Occupancy_Rate is under 100, so unscaled it would be the only thing PCA saw.\n'
     '# the scaler learns its mean and std from the training rows only\n'
     'scaler = StandardScaler().fit(X_train)\n'
     'Xtr, Xte = scaler.transform(X_train), scaler.transform(X_test)\n'
     'print("Largest column std before scaling:", round(X_train.std().max(), 1))\n'
     'print("Largest column std after scaling :", round(Xtr.std(axis=0).max(), 1))'),

    ("8. Classification on the original features (before PCA)",
     'def fit_and_score(name, model, A, B, label):\n'
     '    start = time.perf_counter()\n'
     '    model.fit(A, y_train)\n'
     '    secs = time.perf_counter() - start\n'
     '    acc = accuracy_score(y_test, model.predict(B))\n'
     '    results.append({"Model": name, "Data": label, "Features": A.shape[1],\n'
     '                    "Accuracy": acc, "Train time (s)": secs})\n'
     '    print(name, "|", label, "|", A.shape[1], "features | accuracy",\n'
     '          round(acc, 4), "| time", round(secs, 4), "s")\n\n'
     'fit_and_score("Logistic Regression", LogisticRegression(max_iter=2000),\n'
     '              Xtr, Xte, "Original")\n'
     'fit_and_score("Random Forest", RandomForestClassifier(random_state=SEED),\n'
     '              Xtr, Xte, "Original")'),

    ("9. Applying PCA and the explained variance",
     '# fit on the training rows only, then apply the same rotation to the test rows\n'
     'pca_full = PCA(random_state=SEED).fit(Xtr)\n'
     'ratio = pca_full.explained_variance_ratio_\n'
     'cum = ratio.cumsum()\n\n'
     'var = pd.DataFrame({"Variance": ratio.round(4), "Cumulative": cum.round(4)},\n'
     '                   index=[f"PC{i}" for i in range(1, len(ratio) + 1)])\n'
     'print(var.head(8).to_string())\n'
     'print("...")\n'
     'for target in (0.80, 0.90, 0.95):\n'
     '    print(f"Components needed to keep {int(target*100)}% of the variance:",\n'
     '          int(np.argmax(cum >= target)) + 1, "of", len(ratio))\n\n'
     'fig, ax = plt.subplots(1, 2, figsize=(11, 4))\n'
     'ax[0].bar(range(1, len(ratio) + 1), ratio, color="#4C72B0")\n'
     'ax[0].set_title("Variance carried by each component")\n'
     'ax[0].set_xlabel("component")\n'
     'ax[1].plot(range(1, len(ratio) + 1), cum, marker="o", color="#C44E52")\n'
     'ax[1].axhline(0.95, linestyle="--", color="grey")\n'
     'ax[1].set_title("Cumulative variance kept")\n'
     'ax[1].set_xlabel("number of components")\n'
     'plt.tight_layout()\n'
     'plt.show()'),

    ("10. Classification after PCA",
     '# keep enough components for 95% of the variance, then also try just 2\n'
     'pca95 = PCA(n_components=0.95, random_state=SEED).fit(Xtr)\n'
     'pca2 = PCA(n_components=2, random_state=SEED).fit(Xtr)\n'
     'print("95% of the variance needs", pca95.n_components_, "components\\n")\n\n'
     'for pca, label in ((pca95, "PCA 95%"), (pca2, "PCA 2")):\n'
     '    A, B = pca.transform(Xtr), pca.transform(Xte)\n'
     '    fit_and_score("Logistic Regression", LogisticRegression(max_iter=2000),\n'
     '                  A, B, label)\n'
     '    fit_and_score("Random Forest", RandomForestClassifier(random_state=SEED),\n'
     '                  A, B, label)'),

    ("11. Comparison before and after PCA",
     'table = pd.DataFrame(results)\n'
     'table["Accuracy"] = table["Accuracy"].round(4)\n'
     'table["Train time (s)"] = table["Train time (s)"].round(4)\n'
     'print(table.to_string(index=False))\n'
     'print("\\nGuessing at random would score:",\n'
     '      round(1 / y.nunique(), 4))\n'
     'print("Always predicting the biggest class would score:",\n'
     '      round(y_test.value_counts(normalize=True).max(), 4))\n\n'
     'fig, ax = plt.subplots(figsize=(8, 4))\n'
     'sns.barplot(data=table, x="Model", y="Accuracy", hue="Data", ax=ax)\n'
     'ax.axhline(1 / y.nunique(), linestyle="--", color="grey")\n'
     'ax.set_title("Accuracy before and after PCA (dashed line = guessing)")\n'
     'ax.set_ylim(0, 1)\n'
     'plt.tight_layout()\n'
     'plt.show()'),

    ("12. The data in two dimensions",
     '# the two components that carry the most variance, coloured by the real status\n'
     'pts = pca2.transform(Xtr)\n'
     'plt.figure(figsize=(7, 5))\n'
     'sns.scatterplot(x=pts[:, 0], y=pts[:, 1], hue=y_train.values, s=18, alpha=0.7)\n'
     'plt.xlabel("PC 1")\n'
     'plt.ylabel("PC 2")\n'
     'plt.title("Building_Status in the first two components")\n'
     'plt.tight_layout()\n'
     'plt.show()\n'
     'print("Variance kept by these two:", round(pca2.explained_variance_ratio_.sum(), 4))'),

    ("13. How correlated are the original columns?",
     '# PCA squeezes out redundancy, and redundancy shows up as correlation\n'
     'corr = X.corr().abs().values\n'
     'np.fill_diagonal(corr, 0)\n'
     'print("Strongest correlation between any two features:", corr.max().round(3))\n'
     'print("Pairs above 0.5:", int((corr > 0.5).sum() // 2))\n'
     'print("Average absolute correlation:", corr.mean().round(3))'),

    ("14. The same pipeline on data that does have redundancy",
     '# sanity check: breast cancer data (built into sklearn) has 30 measurements\n'
     '# that move together. if my code is right, PCA should squeeze it hard\n'
     'from sklearn.datasets import load_breast_cancer\n'
     'bc = load_breast_cancer()\n'
     'bX_tr, bX_te, by_tr, by_te = train_test_split(\n'
     '    bc.data, bc.target, test_size=0.2, random_state=SEED, stratify=bc.target)\n'
     'sc = StandardScaler().fit(bX_tr)\n'
     'bX_tr, bX_te = sc.transform(bX_tr), sc.transform(bX_te)\n'
     'print("Original features:", bX_tr.shape[1])\n'
     'print("Pairs of features correlated above 0.9:",\n'
     '      int((np.abs(np.corrcoef(bX_tr.T)) > 0.9).sum() - bX_tr.shape[1]) // 2)\n\n'
     'bp = PCA(n_components=0.95, random_state=SEED).fit(bX_tr)\n'
     'print("Components for 95% of the variance:", bp.n_components_)\n'
     'for label, A, B in (("original", bX_tr, bX_te),\n'
     '                    ("PCA 95%", bp.transform(bX_tr), bp.transform(bX_te))):\n'
     '    m = LogisticRegression(max_iter=2000).fit(A, by_tr)\n'
     '    print(label.ljust(9), A.shape[1], "features | accuracy",\n'
     '          round(accuracy_score(by_te, m.predict(B)), 4))'),

    ("15. Interpretations",
     'acc = table.set_index(["Model", "Data"])["Accuracy"]\n'
     'print("INTERPRETATIONS")\n'
     'print("-" * 66)\n'
     'print("1. The task is to predict Building_Status (3 balanced classes) from")\n'
     'print("   the other columns. Guessing scores", round(1 / y.nunique(), 3),\n'
     '      "; every model before and")\n'
     'print("   after PCA lands around that line, from", round(acc.min(), 3), "to", round(acc.max(), 3), ".")\n'
     'print("   So in this file the features carry almost no information about")\n'
     'print("   the status, and no choice of model or reduction can create it.")\n'
     'print("2. PCA moved the scores only by noise (the test set is 250 rows, so")\n'
     'print("   one more right answer is 0.4%), and it had almost nothing to")\n'
     'print("   remove: the 95% cut needed", pca95.n_components_, "of", Xtr.shape[1], "components.")\n'
     'print("   The first component carries only", round(ratio[0] * 100, 1), "% of the variance.")\n'
     'print("3. That is exactly what question 13 predicted. PCA removes redundancy,")\n'
     'print("   and redundancy is correlation. The strongest correlation between")\n'
     'print("   any two features here is only", corr.max().round(2), ", so the columns are")\n'
     'print("   close to independent and there is no shared variation to compress.")\n'
     'print("4. The two-component plot shows the same thing: the three statuses are")\n'
     'print("   piled on top of each other, with no region that belongs to one.")\n'
     'print("5. Question 14 proves the code is not the problem. On breast cancer")\n'
     'print("   data, where the measurements overlap heavily, the same pipeline")\n'
     'print("   keeps", bp.n_components_, "of 30 components and the accuracy does not change.")\n'
     'print("6. Lesson: PCA is a tool for correlated data. Check the correlation")\n'
     'print("   first, and expect little from it when the columns are independent.")\n'
     'print("7. Training time is tiny for every model, because 1250 rows is small.")\n'
     'print("   The speed-up from fewer features only matters at a much larger size.")'),
]

NB_CELLS = [
    ("md", "# Ex 9 \u2014 Dimensionality Reduction using PCA\n\n"
           "**Dataset:** Bangalore Smart Building  \n"
           "**Task:** predict `Building_Status` before and after PCA  \n**Reg No:** URK24CS1021"),
    ("code",
     "import time\n"
     "import numpy as np\n"
     "import pandas as pd\n"
     "import matplotlib.pyplot as plt\n"
     "import seaborn as sns\n"
     "from sklearn.model_selection import train_test_split\n"
     "from sklearn.preprocessing import StandardScaler\n"
     "from sklearn.decomposition import PCA\n"
     "from sklearn.linear_model import LogisticRegression\n"
     "from sklearn.ensemble import RandomForestClassifier\n"
     "from sklearn.metrics import accuracy_score\n\n"
     "SEED = 1021\n"
     'df = pd.read_csv("building_data.csv")\n'
     "df.head()"),
    ("code", "df.shape, df.isnull().sum().sum()"),
    ("code", "df.describe().round(2).T"),
    ("md", "### What are we predicting, and what is guessing worth?"),
    ("code", 'df["Building_Status"].value_counts()'),
    ("md", "### Prepare the features"),
    ("code",
     "# City is the same for every row, the date is text\n"
     'X = df.drop(columns=["Building_Status", "City", "Last_Inspection_Date"])\n'
     'y = df["Building_Status"]\n\n'
     "# PCA needs numbers, so text columns become 0/1 columns\n"
     'X = pd.get_dummies(X, columns=["Area", "Building_Type", "Maintenance_Priority"],\n'
     "                   drop_first=True).astype(float)\n"
     "X.shape"),
    ("code",
     "# split first, so the test rows never influence scaling or PCA\n"
     "X_train, X_test, y_train, y_test = train_test_split(\n"
     "    X, y, test_size=0.2, random_state=SEED, stratify=y)\n\n"
     "scaler = StandardScaler().fit(X_train)\n"
     "Xtr, Xte = scaler.transform(X_train), scaler.transform(X_test)\n"
     "Xtr.shape, Xte.shape"),
    ("md", "### Before PCA"),
    ("code",
     "results = []\n\n"
     "def fit_and_score(name, model, A, B, label):\n"
     "    start = time.perf_counter()\n"
     "    model.fit(A, y_train)\n"
     "    secs = time.perf_counter() - start\n"
     "    acc = accuracy_score(y_test, model.predict(B))\n"
     '    results.append({"Model": name, "Data": label, "Features": A.shape[1],\n'
     '                    "Accuracy": round(acc, 4), "Time": round(secs, 4)})\n\n'
     'fit_and_score("Logistic Regression", LogisticRegression(max_iter=2000), Xtr, Xte, "Original")\n'
     'fit_and_score("Random Forest", RandomForestClassifier(random_state=SEED), Xtr, Xte, "Original")\n'
     "pd.DataFrame(results)"),
    ("md", "### PCA and the explained variance"),
    ("code",
     "pca_full = PCA(random_state=SEED).fit(Xtr)\n"
     "cum = pca_full.explained_variance_ratio_.cumsum()\n"
     "cum.round(3)"),
    ("code",
     "plt.plot(range(1, len(cum) + 1), cum, marker='o')\n"
     "plt.axhline(0.95, linestyle='--', color='grey')\n"
     "plt.xlabel('components')\n"
     "plt.ylabel('variance kept')\n"
     "plt.show()"),
    ("md", "### After PCA"),
    ("code",
     "pca95 = PCA(n_components=0.95, random_state=SEED).fit(Xtr)\n"
     "pca2 = PCA(n_components=2, random_state=SEED).fit(Xtr)\n\n"
     'for pca, label in ((pca95, "PCA 95%"), (pca2, "PCA 2")):\n'
     "    A, B = pca.transform(Xtr), pca.transform(Xte)\n"
     '    fit_and_score("Logistic Regression", LogisticRegression(max_iter=2000), A, B, label)\n'
     '    fit_and_score("Random Forest", RandomForestClassifier(random_state=SEED), A, B, label)\n'
     "pd.DataFrame(results)"),
    ("md", "### Why so little change? Check the correlation"),
    ("code",
     "corr = X.corr().abs().values\n"
     "np.fill_diagonal(corr, 0)\n"
     "corr.max().round(3)"),
    ("code",
     "pts = pca2.transform(Xtr)\n"
     "sns.scatterplot(x=pts[:, 0], y=pts[:, 1], hue=y_train.values, s=18)\n"
     "plt.show()"),
]

VIDEO = "# Ex 9 \u2014 video\nSee videos/ex9-pca/SCRIPT.md (written after the real run).\n"


def main() -> None:
    build(Exp(
        num=9, title=TITLE, date=DATE, out=OUT, aim=AIM,
        desc_label="Description (About PCA)", desc=DESC, question=QUESTION,
        preamble=PREAMBLE, sections=SECTIONS, nb_cells=NB_CELLS, video=VIDEO,
        script_name="building_pca.py", notebook_name="Ex9_PCA.ipynb",
        shot_command="python building_pca.py", shot_cwd=r"C:\DSE\Ex9",
    ))


if __name__ == "__main__":
    main()
