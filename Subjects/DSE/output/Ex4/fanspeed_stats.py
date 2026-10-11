# Ex 4 - Descriptive Statistics and Correlation (fanspeed.csv)
# URK24CS1021

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (7, 4.5)
pd.set_option("display.width", 120)

# Loading the dataset
df = pd.read_csv("fanspeed.csv")
print(df.head())
print("\nShape:", df.shape)
print("\nData types:")
print(df.dtypes)

# 1. Mean of each numerical column
print("Mean:")
print(df.mean(numeric_only=True))

# 2. Median of each numerical column, compared to the mean
print("Median:")
print(df.median(numeric_only=True))

compare = pd.DataFrame({"mean": df.mean(numeric_only=True),
                        "median": df.median(numeric_only=True)})
compare["difference"] = compare["mean"] - compare["median"]
print("\nMean vs median:")
print(compare)

# 3. Mode(s) for numerical and categorical columns
# every reading in this dataset is unique, so every value ties as a mode
for col in df.columns:
    modes = df[col].mode()
    print(col, "-> number of modes:", len(modes))
    print("   first few:", list(modes.head(3)))

# the dataset has no categorical column, so derive one by binning temperature
df["Temp_Band"] = pd.cut(df["Temperature"], bins=[5, 15, 25, 35],
                          labels=["Low", "Mid", "High"], include_lowest=True)
print("\nCounts per band:")
print(df["Temp_Band"].value_counts())
print("\nMode of the categorical column:", list(df["Temp_Band"].mode()))

# 4. Variance of each numerical column
print("Variance:")
print(df.var(numeric_only=True))
print("\nHighest variance:", df.var(numeric_only=True).idxmax())

# 5. Standard deviation, and how it relates to variance
print("Standard deviation:")
print(df.std(numeric_only=True))

check = pd.DataFrame({"variance": df.var(numeric_only=True),
                      "std": df.std(numeric_only=True)})
check["std squared"] = check["std"] ** 2
print("\nStd is the square root of variance:")
print(check)

# 6. Range (max - min) of each numerical column
nums = df.select_dtypes(include="number")
rng = pd.DataFrame({"min": nums.min(), "max": nums.max()})
rng["range"] = rng["max"] - rng["min"]
print(rng)
print("\nWidest range:", rng["range"].idxmax())

# 7. Inter-quartile range and the 1.5xIQR outlier rule
q1 = nums.quantile(0.25)
q3 = nums.quantile(0.75)
iqr = q3 - q1
fences = pd.DataFrame({"Q1": q1, "Q3": q3, "IQR": iqr,
                       "lower fence": q1 - 1.5 * iqr,
                       "upper fence": q3 + 1.5 * iqr})
print(fences)

print("\nOutliers per column:")
for col in nums.columns:
    low = q1[col] - 1.5 * iqr[col]
    high = q3[col] + 1.5 * iqr[col]
    out = nums[(nums[col] < low) | (nums[col] > high)]
    print("  ", col, "->", len(out), "outliers")

# 8. Correlation matrix for all numerical variables
corr = nums.corr()
print(corr)
# only two numerical columns, so there is exactly one pair to compare
print("\nTemperature vs Observed Fan Speed:",
      round(corr.loc["Temperature", "Observed Fan Speed"], 4))

# 9. Pearson correlation between two selected columns
pearson = df["Temperature"].corr(df["Observed Fan Speed"], method="pearson")
print("Pearson correlation:", round(pearson, 4))
print("Direction:", "positive" if pearson > 0 else
      ("negative" if pearson < 0 else "neutral"))

# 10. Spearman rank correlation, compared to Pearson
spearman = df["Temperature"].corr(df["Observed Fan Speed"], method="spearman")
print("Spearman correlation:", round(spearman, 4))
print("Pearson correlation :", round(pearson, 4))
print("Difference          :", round(pearson - spearman, 4))

# 11. Heatmap of the correlation matrix
sns.heatmap(corr, annot=True, fmt=".3f", cmap="coolwarm",
            vmin=-1, vmax=1, square=True)
plt.title("Correlation matrix")
plt.tight_layout()
plt.show()

# 12. Scatter plot with a regression line
sns.regplot(data=df, x="Temperature", y="Observed Fan Speed",
            scatter_kws={"s": 30, "alpha": 0.7},
            line_kws={"color": "red"})
plt.title("Observed Fan Speed vs Temperature, with regression line")
plt.tight_layout()
plt.show()

# 13. Box plot for a numerical column
sns.boxplot(y=df["Observed Fan Speed"], color="#8FBC8F")
plt.title("Observed Fan Speed - box plot")
plt.tight_layout()
plt.show()

# 14. Histogram for a numerical column
print("Skewness:", round(df["Observed Fan Speed"].skew(), 4))
sns.histplot(df["Observed Fan Speed"], bins=12, kde=True, color="#4C72B0")
plt.title("Distribution of Observed Fan Speed")
plt.xlabel("Observed Fan Speed")
plt.tight_layout()
plt.show()

# 15. Pair plot of the numerical variables
sns.pairplot(nums, diag_kind="hist", height=2.6)
plt.suptitle("Pair plot - Temperature and Observed Fan Speed", y=1.02)
plt.show()