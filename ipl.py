


import pandas as pd

# 1. Load original Kaggle dataset
df = pd.read_csv("archive/IPL.csv", low_memory=False)

print("Original shape:", df.shape)

# 2. Remove completely empty column
df = df.drop(columns=["power_surge_start"])

# 3. Convert date into datetime format
df["date"] = pd.to_datetime(df["date"])

# 4. Check duplicate rows
print("Duplicate rows:", df.duplicated().sum())

# 5. Check missing values
print("\nMissing values:")
print(df.isnull().sum())

# 6. Save cleaned dataset
df.to_csv("archive/cleaned_IPL.csv", index=False)

print("\nCleaned dataset saved successfully!")
print("Final shape:", df.shape)