import pandas as pd
import os

print("📂 Loading cleaned data with districts...")
df = pd.read_csv("data/accidents_with_districts.csv")

# Drop rows where District or State is missing (if any)
df = df.dropna(subset=["District", "State"])
print(f"✅ Rows with valid district & state: {len(df)}")

# Base output folder
base_folder = "districts"
os.makedirs(base_folder, exist_ok=True)

# Group by state and district
grouped = df.groupby(["State", "District"])

count = 0
for (state, district), group in grouped:
    # Clean names
    state_clean = state.strip().replace(" ", "_").replace("/", "_")
    district_clean = district.strip().replace(" ", "_").replace("/", "_")

    # Make state folder
    state_folder = os.path.join(base_folder, state_clean)
    os.makedirs(state_folder, exist_ok=True)

    # File path
    file_path = os.path.join(state_folder, f"{district_clean}.csv")
    group.to_csv(file_path, index=False)
    count += 1

print(f"✅ Saved {count} district-wise CSVs in '{base_folder}/[STATE]/[DISTRICT].csv'")
