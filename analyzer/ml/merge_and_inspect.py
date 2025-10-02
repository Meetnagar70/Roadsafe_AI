import pandas as pd

# Load all CSVs
accidents = pd.read_csv('data/raw/AccidentsBig.csv')
vehicles = pd.read_csv('data/raw/VehiclesBig.csv')
casualties = pd.read_csv('data/raw/CasualtiesBig.csv')

print("🔹 Loaded")

# === Aggregate Vehicles by Accident_Index ===
vehicles_agg = vehicles.groupby('Accident_Index').agg({
    'Vehicle_Type': 'count',  # Total vehicles
    'Age_of_Vehicle': 'mean',
    'Engine_Capacity_(CC)': 'mean'
}).rename(columns={
    'Vehicle_Type': 'Num_Vehicles',
    'Age_of_Vehicle': 'Avg_Vehicle_Age',
    'Engine_Capacity_(CC)': 'Avg_Engine_CC'
}).reset_index()

# === Aggregate Casualties by Accident_Index ===
casualties_agg = casualties.groupby('Accident_Index').agg({
    'Casualty_Severity': 'count',  # Total casualties
}).rename(columns={'Casualty_Severity': 'Num_Casualties'}).reset_index()

# === Merge All ===
merged = accidents.merge(vehicles_agg, on='Accident_Index', how='left')
merged = merged.merge(casualties_agg, on='Accident_Index', how='left')

# Fill NA values after merge
merged['Num_Casualties'] = merged['Num_Casualties'].fillna(0).astype(int)
merged['Num_Vehicles'] = merged['Num_Vehicles'].fillna(0).astype(int)

# Save cleaned/merged dataset
merged.to_csv('data/merged/accidents_full.csv', index=False)

# Show sample output
print("\n🔹 Merged Shape:", merged.shape)
print("\n🔹 Columns:\n", merged.columns.tolist())
print("\n🔹 Head:\n", merged.head(3))
