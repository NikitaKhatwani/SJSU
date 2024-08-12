import overpy
import pandas as pd
import math

# Initialize the Overpass API
api = overpy.Overpass()

# Define the bounding box around San Jose State University (diagonal area)
# These coordinates need to be adjusted to fit your specific diagonal area
south, west, north, east = 37.33166324918992,-121.88604200109424, 37.336006100006, -121.87649626703674,

# Overpass API query to get all buildings within the bounding box
query = f"""
    [out:json];
    (
      way["building"]({south},{west},{north},{east});
      relation["building"]({south},{west},{north},{east});
    );
    out center;
"""

# Fetch the data
result = api.query(query)

# List to hold the building data
buildings = []

# Example function to check if a point is within the diagonal area
def is_within_diagonal_area(lat, lon, sw, ne):
    # Example logic to determine if a point is within the diagonal area
    # This will vary depending on the shape and orientation of your diagonal area
    # For simplicity, let's assume a simple diagonal from (sw) to (ne)
    return sw[0] <= lat <= ne[0] and sw[1] <= lon <= ne[1]

# Define the diagonal corners of the area
sw_corner = (37.3315, -121.886)
ne_corner = (37.3397, -121.875)

# Extract the data
for way in result.ways:
    lat = way.center_lat
    lon = way.center_lon
    if is_within_diagonal_area(lat, lon, sw_corner, ne_corner):
        building_info = {
            "id": way.id,
            "name": way.tags.get("name", "N/A"),
            "lat": lat,
            "lon": lon
        }
        buildings.append(building_info)

# Convert the list to a DataFrame
df = pd.DataFrame(buildings)

# Save to CSV (optional)
df.to_csv("sjsu_buildings.csv", index=False)

print(df)