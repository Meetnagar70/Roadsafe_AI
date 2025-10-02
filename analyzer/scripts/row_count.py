import pandas as pd

# Load your district-level CSV
df = pd.read_csv("data/accidents_with_districts.csv")

# Count missing values
missing_state = df['State'].isna().sum()
missing_district = df['District'].isna().sum()
missing_both = df[df['State'].isna() & df['District'].isna()].shape[0]

# Total rows with any missing values in ST_NM or District
missing_either = df[df['State'].isna() | df['District'].isna()].shape[0]

# Output
print("🧮 Missing value summary:")
print(f"Missing State (State):     {missing_state}")
print(f"Missing District:          {missing_district}")
print(f"Missing Both:              {missing_both}")
print(f"Missing Either (Total):    {missing_either}")
print(f"✅ Total Rows:              {len(df)}")

# Drop rows where either State or District is missing
df_clean = df.dropna(subset=['State', 'District'])

# Save cleaned data
df_clean.to_csv("data/accidents_with_districts_cleaned.csv", index=False)

print(f"✅ Cleaned data saved with {len(df_clean)} rows (dropped {len(df) - len(df_clean)} rows).")
