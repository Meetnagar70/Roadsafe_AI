import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Paths
input_csv = "data/accidents_with_districts_cleaned.csv"
output_csv = "data/accidents_with_clusters.csv"
model_path = "analyzer/models/dbscan_model.joblib"
preview_img = "analyzer/models/cluster_preview.png"

# 🚀 Step 1: Load dataset
print("📥 Loading data...")
df = pd.read_csv(input_csv)

# Drop rows with missing lat/lon
df = df.dropna(subset=["latitude", "longitude"])

# 🚦 Optional: Reset index
df = df.reset_index(drop=True)

# Step 2: Prepare data for clustering
coords = df[["latitude", "longitude"]]
coords_scaled = StandardScaler().fit_transform(coords)

# Step 3: Apply DBSCAN
print("🔍 Running DBSCAN clustering...")
dbscan = DBSCAN(eps=0.05, min_samples=10)
dbscan.fit(coords_scaled)

# Step 4: Save model
os.makedirs(os.path.dirname(model_path), exist_ok=True)
joblib.dump(dbscan, model_path)
print(f"✅ Model saved to {model_path}")

# Step 5: Save preview image
print("📊 Generating preview plot...")
df["cluster_label"] = dbscan.labels_
plt.figure(figsize=(10, 6))
plt.scatter(df["longitude"], df["latitude"], c=df["cluster_label"], cmap="tab20", s=5)
plt.title("DBSCAN Clustering Preview")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.tight_layout()
plt.savefig(preview_img)
plt.close()
print(f"🖼️ Saved cluster preview image at {preview_img}")

# Step 6: Count stats
n_clusters = len(set(dbscan.labels_)) - (1 if -1 in dbscan.labels_ else 0)
n_noise = list(dbscan.labels_).count(-1)
print(f"🧠 Clusters found: {n_clusters}")
print(f"🌪️ Noise points: {n_noise}")

# Step 7: Save full dataset with cluster labels
os.makedirs(os.path.dirname(output_csv), exist_ok=True)
df.to_csv(output_csv, index=False)
print(f"✅ Saved dataset with cluster labels at {output_csv}")
