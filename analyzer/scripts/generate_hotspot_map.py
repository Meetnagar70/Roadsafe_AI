import pandas as pd
import folium
from folium.plugins import MarkerCluster

# ---------- START ----------
print("🟢 Starting hotspot map generation...")

# Load cleaned data
df = pd.read_csv("data/cleaned_data.csv")

# Filter to ensure valid coordinates
df = df[(df['latitude'].notnull()) & (df['longitude'].notnull())]

# Create base map centered on India
map_center = [21.0, 78.0]  # Central India lat/lon
m = folium.Map(location=map_center, zoom_start=5, tiles="OpenStreetMap")

# Add clustered accident markers
marker_cluster = MarkerCluster().add_to(m)

for _, row in df.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"Date: {row.get('date', 'N/A')}\nSeverity: {row.get('severity', 'N/A')}",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(marker_cluster)

# Save the map to HTML
m.save("outputs/hotspot_map.html")

print("✅ Hotspot map saved to outputs/hotspot_map.html")
