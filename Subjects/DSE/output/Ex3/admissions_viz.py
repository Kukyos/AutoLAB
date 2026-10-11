# Ex 3 - Data Visualization (University Admissions dataset)
# URK24CS1021

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (7, 4.5)

# Loading the dataset
df = pd.read_csv("admissions.csv")
print(df)
print("\nShape:", df.shape)
print("\nData types:")
print(df.dtypes)

# 1. Scatter Plot: SAT_Score vs. GPA (colour by Admitted)
sns.scatterplot(data=df, x="GPA", y="SAT_Score", hue="Admitted",
                style="Admitted", s=120)
plt.title("SAT Score vs GPA, coloured by admission status")
plt.xlabel("GPA")
plt.ylabel("SAT Score")
plt.tight_layout()
plt.show()

# 2. Box Plot: ACT_Score distribution by Admitted status
sns.boxplot(data=df, x="Admitted", y="ACT_Score",
            hue="Admitted", palette="Set2", legend=False)
plt.title("ACT Score distribution by admission status")
plt.xlabel("Admitted")
plt.ylabel("ACT Score")
plt.tight_layout()
plt.show()

# 3. Bar Plot: Admission rate by Recommendation_Strength
# Admitted is Yes/No, so the admission rate is the mean of (Admitted == "Yes")
rate = (df.groupby("Recommendation_Strength")["Admitted"]
          .apply(lambda s: (s == "Yes").mean())
          .reindex(["Weak", "Moderate", "Strong"]))
print("Admission rate:")
print(rate)

sns.barplot(x=rate.index, y=rate.values, hue=rate.index,
            palette="Blues_d", legend=False)
plt.title("Admission rate by recommendation strength")
plt.xlabel("Recommendation Strength")
plt.ylabel("Admission rate")
plt.ylim(0, 1)
plt.tight_layout()
plt.show()

# 4. Histogram: Distribution of Extracurriculars
# whole numbers 0-5, so give it explicit bins instead of the automatic ones
plt.hist(df["Extracurriculars"], bins=range(0, 7), edgecolor="black",
         align="left", color="#4C72B0")
plt.xticks(range(0, 6))
plt.yticks(range(0, 6))  # counts are whole students, not 2.5 of one
plt.title("Distribution of extracurricular activities")
plt.xlabel("Number of extracurriculars")
plt.ylabel("Number of students")
plt.tight_layout()
plt.show()

# 5. Violin Plot: GPA distribution by Admitted status
sns.violinplot(data=df, x="Admitted", y="GPA", hue="Admitted",
               palette="Set3", legend=False)
plt.title("GPA distribution by admission status")
plt.xlabel("Admitted")
plt.ylabel("GPA")
plt.tight_layout()
plt.show()