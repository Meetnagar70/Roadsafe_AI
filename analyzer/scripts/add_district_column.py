import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

print("🚀 Starting district assignment...")

# Step 1: Load accident CSV
accident_csv = "data/cleaned_accidents.csv"
df = pd.read_csv(accident_csv)
print(f"✅ Loaded CSV with {len(df)} rows")

# Step 2: Drop rows without lat/lon
df = df.dropna(subset=["latitude", "longitude"])
print(f"🧹 After dropping missing lat/lon: {len(df)} rows")

# Step 3: Convert to GeoDataFrame
geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Step 4: Load districts shapefile
districts_shapefile = "data/shapefiles/districts/2011_Dist.shp"
districts = gpd.read_file(districts_shapefile)
print(f"🗺️ Districts shapefile loaded with {len(districts)} shapes")

# Step 5: Ensure matching CRS
districts = districts.to_crs(gdf.crs)

# Step 6: Spatial join to find district for each accident
joined = gpd.sjoin(gdf, districts, how="left", predicate="within")
print("🔁 Spatial join complete")

# Optional: Rename to clean names
joined = joined.rename(columns={
    'ST_NM': 'State',
    'DISTRICT': 'District'
})

# Show final columns
print(f"🧪 Final columns: {list(joined.columns)}")

# Step 7: Save selected columns to new CSV
columns_to_save = [
    'Accident_Index', 'Date', 'Time', 'latitude', 'longitude',
    'Accident_Severity', 'Number_of_Vehicles', 'Number_of_Casualties',
    'Road_Type', 'Weather_Conditions', 'Light_Conditions',
    'State', 'District'
]
output_csv = "data/accidents_with_districts.csv"
joined[columns_to_save].to_csv(output_csv, index=False)
print(f"✅ Saved with district and state: {output_csv}")
