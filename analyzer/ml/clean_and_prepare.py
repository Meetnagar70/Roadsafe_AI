import pandas as pd
import os

# Paths
input_path = "C:/Py_Group/roadsafe_ai/data/merged/accidents_full.csv"
output_path = "C:/Py_Group/roadsafe_ai/data/cleaned_accidents.csv"

# Load
df = pd.read_csv(input_path)

# 🔹 Drop completely empty columns (like ,,,,,)
df.dropna(axis=1, how='all', inplace=True)

# 🔹 Drop completely empty rows (like ,,,,,,,,,)
df.dropna(axis=0, how='all', inplace=True)

# Optional: print shape before and after filtering
print("✅ After removing empty columns/rows")
print(f"🔹 Shape: {df.shape}")
print(f"🔹 Columns: {list(df.columns)}")

# Filter and rename necessary columns
df = df[[
    'Accident_Index', 'Date', 'Time', 'latitude', 'longitude',
    'Accident_Severity', 'Number_of_Vehicles', 'Number_of_Casualties',
    'Road_Type', 'Weather_Conditions', 'Light_Conditions'
]]

# Convert date format
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')

# Drop rows where date conversion failed
df.dropna(subset=['Date'], inplace=True)

# Mappings
accident_severity_map = {
    1: 'Fatal',
    2: 'Serious injury',
    3: 'Minor injury'
}

road_type_map = {
    1: 'Roundabout',
    2: 'One way street',
    3: 'Dual carriageway',
    6: 'Single carriageway',
    7: 'Slip road',
    9: 'Unknown',
    12: 'One way street',
    -1: 'Data missing'
}

weather_conditions_map = {
    1: 'Fine no high winds',
    2: 'Raining no high winds',
    3: 'Snowing no high winds',
    4: 'Fine + high winds',
    5: 'Raining + high winds',
    6: 'Snowing + high winds',
    7: 'Fog or mist',
    8: 'Other',
    9: 'Unknown'
}

light_conditions_map = {
    1: 'Daylight',
    4: 'Darkness - lights lit',
    5: 'Darkness - lights unlit',
    6: 'Darkness - no lighting',
    7: 'Darkness - lighting unknown'
}

# Apply mappings
df['Accident_Severity'] = df['Accident_Severity'].map(accident_severity_map)
df['Road_Type'] = df['Road_Type'].map(road_type_map)
df['Weather_Conditions'] = df['Weather_Conditions'].map(weather_conditions_map)
df['Light_Conditions'] = df['Light_Conditions'].map(light_conditions_map)

# Save
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)

print(f"✅ Cleaned and mapped dataset saved to {output_path}")
print(f"🔹 Final shape: {df.shape}")
print(f"🔹 Columns: {list(df.columns)}")
print("🔹 Sample:")
print(df.head(3))
