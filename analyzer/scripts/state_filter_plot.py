# roadsafe_ai/analyzer/scripts/state_filter_plot.py

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

print("🔄 Script started...")

# === Load Data ===
df = pd.read_csv("C:/Py_Group/roadsafe_ai/data/accidents_with_states.csv")
df = df.dropna(subset=['latitude', 'longitude', 'ST_NM'])

# === Input: State Name ===
state = input("🔹 Enter state name (e.g., Maharashtra): ").strip()

# === Filter State ===
state_df = df[df['ST_NM'].str.lower() == state.lower()]
if state_df.empty:
    print(f"❌ No data found for '{state}'")
    exit()
else:
    print(f"✅ Loaded {len(state_df)} rows for {state}")

# === Output Directory ===
output_dir = "C:/Py_Group/roadsafe_ai/analyzer/output"
os.makedirs(output_dir, exist_ok=True)

# === Pie Chart: Severity Distribution ===
plt.figure(figsize=(6, 6))
state_df['Accident_Severity'].value_counts().plot.pie(autopct='%1.1f%%', startangle=140, colors=sns.color_palette("Set3"))
plt.title(f"Accident Severity Distribution in {state}")
plt.ylabel("")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, f"{state}_severity_pie.png"))
plt.close()
print("📊 Severity pie chart saved.")

# === Heatmap: Accident Locations ===
plt.figure(figsize=(8, 6))
sns.kdeplot(
    data=state_df,
    x="longitude", y="latitude",
    cmap="Reds", fill=True, bw_adjust=0.5, thresh=0.05
)
plt.title(f"Accident Hotspots in {state}")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.savefig(os.path.join(output_dir, f"{state}_heatmap.png"))
plt.close()
print("🗺️ Heatmap saved.")

print("✅ Visualization complete.")
