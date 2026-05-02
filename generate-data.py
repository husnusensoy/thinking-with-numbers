import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# A simple script for generating water consumption data for our trend test with simulation example.

group_col = "moy"
value_col = "m3"

np.random.seed(42)

months = np.repeat(np.arange(1, 13), 100)

# positive trend with less variance
values_trend = (
    np.abs(np.random.normal(loc=0.4, scale=0.05, size=len(months)))
    + np.repeat(range(1, 13), 100) / 50
)

# no trend
values_no_trend = np.abs(np.random.normal(loc=0.4, scale=0.2, size=len(months)))

# seasonality
values_seasonal = (
    np.abs(np.random.normal(loc=0.4, scale=0.2, size=len(months)))
    + np.sin(np.linspace(0, np.pi, len(months))) * 0.3
)

# no trend but level difference
values_step = (
    np.abs(np.random.normal(loc=0.4, scale=0.2, size=len(months)))
    + np.where(months > 6, 0.4, 0.0)  # 0.4 m3 increase after 6th month
)

# outilers
values_outlier = np.abs(np.random.normal(loc=0.4, scale=0.2, size=len(months)))
random_indices = np.random.choice(len(months), 10, replace=False)
values_outlier[random_indices] = values_outlier[random_indices] * 5

df_besiktas = pd.DataFrame({"district": "BESIKTAS", group_col: months, value_col: values_trend})
df_sariyer = pd.DataFrame({"district": "SARIYER", group_col: months, value_col: values_no_trend})
df_kadikoy = pd.DataFrame({"district": "KADIKOY", group_col: months, value_col: values_seasonal})
df_uskudar = pd.DataFrame({"district": "USKUDAR", group_col: months, value_col: values_step})
df_beyoglu = pd.DataFrame({"district": "BEYOGLU", group_col: months, value_col: values_outlier})

df = pd.concat([df_besiktas, df_sariyer, df_kadikoy, df_uskudar, df_beyoglu], ignore_index=True)
df.to_csv("data/water_consumption.csv")

plt.figure(figsize=(10, 6))
for district in df["district"].unique():
    subset = df[df["district"] == district]
    means = subset.groupby(group_col)[value_col].mean()
    plt.plot(means.index, means.values, marker="o", label=district)


plt.title("District Water Consumption Trend")
plt.xlabel("Month of Year")
plt.ylabel("Avg m3 Consumption")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
