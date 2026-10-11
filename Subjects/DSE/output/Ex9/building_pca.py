# Ex 9 - Dimensionality Reduction Using Pca
# URK24CS1021

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

sns.set_theme(style="whitegrid")
pd.set_option("display.width", 110)
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_colwidth", 18)

SEED = 1021  # my reg no
results = []  # one row per model, for the final comparison table

# 1. Import the dataset
df = pd.read_csv("building_data.csv")
print("Rows loaded:", len(df))
print(df.head())

# 2. Information about the dataset
df.info()

# 3. Shape and column names
print("Shape (rows, columns):", df.shape)
for i, col in enumerate(df.columns, 1):
    print(i, col)

# 4. Statistical summary and missing values
print(df.describe().round(2).T)
print("\nMissing values in the whole file:", df.isnull().sum().sum())
print("Duplicate rows:", df.duplicated().sum())

# 5. The target and the text columns
# the task: from everything else about a building, predict its Building_Status
print(df["Building_Status"].value_counts())
print("\nIf a model just guessed, it would be right about",
      round(100 / df["Building_Status"].nunique(), 1), "% of the time")
print("\nCategories in the other text columns:")
for col in ["City", "Area", "Building_Type", "Maintenance_Priority"]:
    print(col, "->", df[col].nunique(), "values")

# 6. Preparing the features
# City has one value for every row, so it cannot tell two buildings apart.
# Last_Inspection_Date is a text date, not a number the model can use.
X = df.drop(columns=["Building_Status", "City", "Last_Inspection_Date"])
y = df["Building_Status"]

# PCA works on numbers, so the three text columns become 0/1 columns
X = pd.get_dummies(X, columns=["Area", "Building_Type", "Maintenance_Priority"],
                   drop_first=True).astype(float)
print("Features before:", df.shape[1] - 1, "-> after encoding:", X.shape[1])
print(list(X.columns))

# 7. Train-test split and scaling
# the test set is locked away first, so nothing below ever learns from it
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y)
print("Train:", X_train.shape, " Test:", X_test.shape)

# PCA chases variance, and Electricity_Bill is in the tens of thousands while
# Occupancy_Rate is under 100, so unscaled it would be the only thing PCA saw.
# the scaler learns its mean and std from the training rows only
scaler = StandardScaler().fit(X_train)
Xtr, Xte = scaler.transform(X_train), scaler.transform(X_test)
print("Largest column std before scaling:", round(X_train.std().max(), 1))
print("Largest column std after scaling :", round(Xtr.std(axis=0).max(), 1))

# 8. Classification on the original features (before PCA)
def fit_and_score(name, model, A, B, label):
    start = time.perf_counter()
    model.fit(A, y_train)
    secs = time.perf_counter() - start
    acc = accuracy_score(y_test, model.predict(B))
    results.append({"Model": name, "Data": label, "Features": A.shape[1],
                    "Accuracy": acc, "Train time (s)": secs})
    print(name, "|", label, "|", A.shape[1], "features | accuracy",
          round(acc, 4), "| time", round(secs, 4), "s")

fit_and_score("Logistic Regression", LogisticRegression(max_iter=2000),
              Xtr, Xte, "Original")
fit_and_score("Random Forest", RandomForestClassifier(random_state=SEED),
              Xtr, Xte, "Original")

# 9. Applying PCA and the explained variance
# fit on the training rows only, then apply the same rotation to the test rows
pca_full = PCA(random_state=SEED).fit(Xtr)
ratio = pca_full.explained_variance_ratio_
cum = ratio.cumsum()

var = pd.DataFrame({"Variance": ratio.round(4), "Cumulative": cum.round(4)},
                   index=[f"PC{i}" for i in range(1, len(ratio) + 1)])
print(var.head(8).to_string())
print("...")
for target in (0.80, 0.90, 0.95):
    print(f"Components needed to keep {int(target*100)}% of the variance:",
          int(np.argmax(cum >= target)) + 1, "of", len(ratio))

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].bar(range(1, len(ratio) + 1), ratio, color="#4C72B0")
ax[0].set_title("Variance carried by each component")
ax[0].set_xlabel("component")
ax[1].plot(range(1, len(ratio) + 1), cum, marker="o", color="#C44E52")
ax[1].axhline(0.95, linestyle="--", color="grey")
ax[1].set_title("Cumulative variance kept")
ax[1].set_xlabel("number of components")
plt.tight_layout()
plt.show()

# 10. Classification after PCA
# keep enough components for 95% of the variance, then also try just 2
pca95 = PCA(n_components=0.95, random_state=SEED).fit(Xtr)
pca2 = PCA(n_components=2, random_state=SEED).fit(Xtr)
print("95% of the variance needs", pca95.n_components_, "components\n")

for pca, label in ((pca95, "PCA 95%"), (pca2, "PCA 2")):
    A, B = pca.transform(Xtr), pca.transform(Xte)
    fit_and_score("Logistic Regression", LogisticRegression(max_iter=2000),
                  A, B, label)
    fit_and_score("Random Forest", RandomForestClassifier(random_state=SEED),
                  A, B, label)

# 11. Comparison before and after PCA
table = pd.DataFrame(results)
table["Accuracy"] = table["Accuracy"].round(4)
table["Train time (s)"] = table["Train time (s)"].round(4)
print(table.to_string(index=False))
print("\nGuessing at random would score:",
      round(1 / y.nunique(), 4))
print("Always predicting the biggest class would score:",
      round(y_test.value_counts(normalize=True).max(), 4))

fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(data=table, x="Model", y="Accuracy", hue="Data", ax=ax)
ax.axhline(1 / y.nunique(), linestyle="--", color="grey")
ax.set_title("Accuracy before and after PCA (dashed line = guessing)")
ax.set_ylim(0, 1)
plt.tight_layout()
plt.show()

# 12. The data in two dimensions
# the two components that carry the most variance, coloured by the real status
pts = pca2.transform(Xtr)
plt.figure(figsize=(7, 5))
sns.scatterplot(x=pts[:, 0], y=pts[:, 1], hue=y_train.values, s=18, alpha=0.7)
plt.xlabel("PC 1")
plt.ylabel("PC 2")
plt.title("Building_Status in the first two components")
plt.tight_layout()
plt.show()
print("Variance kept by these two:", round(pca2.explained_variance_ratio_.sum(), 4))

# 13. How correlated are the original columns?
# PCA squeezes out redundancy, and redundancy shows up as correlation
corr = X.corr().abs().values
np.fill_diagonal(corr, 0)
print("Strongest correlation between any two features:", corr.max().round(3))
print("Pairs above 0.5:", int((corr > 0.5).sum() // 2))
print("Average absolute correlation:", corr.mean().round(3))

# 14. The same pipeline on data that does have redundancy
# sanity check: breast cancer data (built into sklearn) has 30 measurements
# that move together. if my code is right, PCA should squeeze it hard
from sklearn.datasets import load_breast_cancer
bc = load_breast_cancer()
bX_tr, bX_te, by_tr, by_te = train_test_split(
    bc.data, bc.target, test_size=0.2, random_state=SEED, stratify=bc.target)
sc = StandardScaler().fit(bX_tr)
bX_tr, bX_te = sc.transform(bX_tr), sc.transform(bX_te)
print("Original features:", bX_tr.shape[1])
print("Pairs of features correlated above 0.9:",
      int((np.abs(np.corrcoef(bX_tr.T)) > 0.9).sum() - bX_tr.shape[1]) // 2)

bp = PCA(n_components=0.95, random_state=SEED).fit(bX_tr)
print("Components for 95% of the variance:", bp.n_components_)
for label, A, B in (("original", bX_tr, bX_te),
                    ("PCA 95%", bp.transform(bX_tr), bp.transform(bX_te))):
    m = LogisticRegression(max_iter=2000).fit(A, by_tr)
    print(label.ljust(9), A.shape[1], "features | accuracy",
          round(accuracy_score(by_te, m.predict(B)), 4))

# 15. Interpretations
acc = table.set_index(["Model", "Data"])["Accuracy"]
print("INTERPRETATIONS")
print("-" * 66)
print("1. The task is to predict Building_Status (3 balanced classes) from")
print("   the other columns. Guessing scores", round(1 / y.nunique(), 3),
      "; every model before and")
print("   after PCA lands around that line, from", round(acc.min(), 3), "to", round(acc.max(), 3), ".")
print("   So in this file the features carry almost no information about")
print("   the status, and no choice of model or reduction can create it.")
print("2. PCA moved the scores only by noise (the test set is 250 rows, so")
print("   one more right answer is 0.4%), and it had almost nothing to")
print("   remove: the 95% cut needed", pca95.n_components_, "of", Xtr.shape[1], "components.")
print("   The first component carries only", round(ratio[0] * 100, 1), "% of the variance.")
print("3. That is exactly what question 13 predicted. PCA removes redundancy,")
print("   and redundancy is correlation. The strongest correlation between")
print("   any two features here is only", corr.max().round(2), ", so the columns are")
print("   close to independent and there is no shared variation to compress.")
print("4. The two-component plot shows the same thing: the three statuses are")
print("   piled on top of each other, with no region that belongs to one.")
print("5. Question 14 proves the code is not the problem. On breast cancer")
print("   data, where the measurements overlap heavily, the same pipeline")
print("   keeps", bp.n_components_, "of 30 components and the accuracy does not change.")
print("6. Lesson: PCA is a tool for correlated data. Check the correlation")
print("   first, and expect little from it when the columns are independent.")
print("7. Training time is tiny for every model, because 1250 rows is small.")
print("   The speed-up from fewer features only matters at a much larger size.")