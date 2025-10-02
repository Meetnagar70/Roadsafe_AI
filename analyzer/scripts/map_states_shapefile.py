print("🚀 Script started: Mapping states using shapefile and cleaning empty rows...")

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Paths
input_csv = "data/cleaned_accidents.csv"
shapefile_path = "data/shapefiles/Admin2.shp"
output_csv = "data/accidents_with_states.csv"

# Load CSV
df = pd.read_csv(input_csv)

# Drop completely empty rows (all NaN or blank)
df.dropna(how='all', inplace=True)

# Drop rows with missing lat/lon
df = df.dropna(subset=['latitude', 'longitude'])

# Remove rows where lat/lon are not valid numbers
df = df[pd.to_numeric(df["latitude"], errors="coerce").notnull()]
df = df[pd.to_numeric(df["longitude"], errors="coerce").notnull()]

# Convert lat/lon to float
df["latitude"] = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)

print(f"✔ Cleaned dataset: {len(df)} valid accident records")

# Convert to GeoDataFrame
geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
accidents_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Load shapefile
states_gdf = gpd.read_file(shapefile_path)
states_gdf = states_gdf.to_crs("EPSG:4326")

print(f"✔ Loaded shapefile with {len(states_gdf)} regions")

# Spatial join
accidents_with_state = gpd.sjoin(accidents_gdf, states_gdf, how="left", predicate="within")

# Guess column for state
possible_state_cols = ["st_name", "STATE_NAME", "NAME_1", "NAME_2", "admin"]
for col in possible_state_cols:
    if col in accidents_with_state.columns:
        accidents_with_state.rename(columns={col: "state"}, inplace=True)
        break

# Drop helper columns
final_df = accidents_with_state.drop(columns=["geometry", "index_right"], errors="ignore")

# Save result
final_df.to_csv(output_csv, index=False)
print(f"✅ Saved cleaned and mapped data to: {output_csv}")
