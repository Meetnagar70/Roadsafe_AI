# roadsafe_ai/analyzer/scripts/split_by_state.py

import pandas as pd
import os

print("🚀 Starting to split all_india.csv by State...")

# Input CSV file
input_path = "C:/Py_Group/roadsafe_ai/data/all_india.csv"
df = pd.read_csv(input_path)

# Check for required columns
required_cols = ['State', 'District', 'latitude', 'longitude']
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"❌ Column '{col}' is missing in the dataset.")

# Drop rows with missing values in important fields
df = df.dropna(subset=['State', 'District', 'latitude', 'longitude'])

# Output folder
output_dir = "C:/Py_Group/roadsafe_ai/data/states"
os.makedirs(output_dir, exist_ok=True)

# Group and save by State
for state in df['State'].unique():
    state_df = df[df['State'] == state]
    safe_state_name = state.replace(" ", "_").replace("/", "-")
    output_file = os.path.join(output_dir, f"{safe_state_name}.csv")
    state_df.to_csv(output_file, index=False)
    print(f"✅ Saved {len(state_df)} rows to {output_file}")

print("🎉 All states saved successfully with District and coordinates.")
