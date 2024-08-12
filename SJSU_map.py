from re import U
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import pandas as pd
# import plotly.offline as pyo
# import matplotlib.pyplot as plt
import folium as fo
from streamlit_folium import folium_static, st_folium
# from PIL import Image
# import plotly.express as px
import os



# Set map container to full width
st.set_page_config(layout="wide")
# st.set_page_config(layout="centered")



# @st.cache_data
def load_data(file_path,sheetName):
    # Load data from CSV or any other source
    data = pd.read_excel(file_path,sheet_name=sheetName)
    return data

#tiles="cartodbpositron",
#tiles='Esri WorldImagery', tiles='Esri WorldStreetMap',
def create_map(center_lat, center_lon,tiles, zoom_start=17):
    """Create a base map centered at the given coordinates."""
    return fo.Map(location=[center_lat, center_lon], tiles=tiles,
                 zoom_start=16, min_zoom=2, max_zoom=30)

# Function to generate map markers with labels next to the circle markers
def create_marker(building,color,radius):
    # Create a circle marker
    circle_marker = fo.CircleMarker(
        location=[building["lat"], building["lon"]],
        popup=f"<strong>Building: {building['name']}</strong><br>Meter No: {building['Meter No.']}",
        radius=radius,
        color=color,
        fill_color=color,
        fill_opacity=1
    )
    
    # Add a label next to the circle marker
    label = fo.Marker(
        location=[building["lat"], building["lon"]],
        icon=fo.DivIcon(
            html=f"""
            <div style="font-size: 7pt; color: black; background-color: white; border-radius: 4px; padding: 3px; text-align: left; white-space: nowrap; min-width: 25px; max-width: 240px; box-shadow: 0 0 5px rgba(0,0,0,0.5);display: inline-block;">
                <strong>{building['name']}</strong>
            </div>""",
            icon_size=(100, 60),  # Adjust size based on expected label size
            icon_anchor=(30, 30)  # Adjust to position label correctly
        )
    )
    
    return circle_marker, label

# Function to draw dotted lines between buildings
def draw_dotted_line_meters(map,coords, color="#669900"):
    fo.PolyLine(
        locations=coords,
        color=color,
        weight=2,
        dash_array='5, 5'  # Dotted line style
    ).add_to(map)

# Function to draw dotted lines between buildings
def draw_dotted_line_districtTherm(map,coords, color="#003366"):
    fo.PolyLine(
        locations=coords,
        color=color,
        weight=2,
        dash_array='5, 5'  # Dotted line style
    ).add_to(map)

# Function to draw dotted lines between buildings
def draw_dotted_line_districtElec(map,coords, color="#ffbb99"):
    fo.PolyLine(
        locations=coords,
        color=color,
        weight=2,
        dash_array='5, 5'  # Dotted line style
    ).add_to(map)

def add_building_markers(map, df,color,radius):
    """Add markers and labels for buildings in the given DataFrame."""
    for _, row in df.iterrows():
        circle_marker, label = create_marker(row.to_dict(),color,radius)
        map.add_child(circle_marker)
        # map.add_child(label)


def add_building_label(map, df,color,radius):
    """Add markers and labels for buildings in the given DataFrame."""
    for _, row in df.iterrows():
        circle_marker, label = create_marker(row.to_dict(),color,radius)
        # map.add_child(circle_marker)
        map.add_child(label)

def filter_buildings(buildings, selected_buildings):
    """Filter buildings DataFrame based on selected buildings."""
    if selected_buildings:
        return buildings[buildings["name"].isin(selected_buildings)]
    return buildings

def plot_line_charts(df):
    """Generate line charts for each column in the DataFrame."""
    st.subheader("Data Visualization")

    # Convert the first column to datetime for x-axis
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]], errors='coerce')
    timestamp_col = df.columns[0]

    # Ensure all other columns are numeric
    for column in df.columns[1:]:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # Drop columns with all NaN values
    df = df.dropna(axis=1, how='all')

    # Create a chart for each column
    # Create a chart for each column
    for column in df.columns[1:]:
        # Escape special characters in column names
        escaped_column = column.replace(":", "\\:").replace("/", "\\/")
        
        if df[column].notna().any():  # Check if column has any non-NaN values
            chart = alt.Chart(df).mark_line().encode(
                x=alt.X(timestamp_col, title='Timestamp', type='temporal'),
                y=alt.Y(escaped_column, title=column, type='quantitative'),
                tooltip=[timestamp_col, escaped_column]
            ).properties(
                width=600,
                height=400,
                title=f'{column} Over Time'
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning(f"The column '{column}' has no valid data and cannot be plotted.")

def main():

    st.header("SJSU Campus Map")
    # Load data
    buildings = load_data("sjsu_buildings.xlsx","sjsu_buildings")

    # Create two columns
    col1, col2 = st.columns([1, 3])  # You can adjust the width ratio as needed

    with col1:
        # Filter control for interactivity
        selected_buildings = st.multiselect("Select Buildings to View:", buildings["name"].tolist())

        # Filter buildings based on selection
        filtered_df = filter_buildings(buildings, selected_buildings)

        districtTherm = st.checkbox("District Steam")
        districtTherm_df = filtered_df[filtered_df["District Steam (Yes or No)"] == "yes"]
        if districtTherm:
            st.subheader(f"There are {districtTherm_df.shape[0]} buildings on the district steam/CHW loop")

        districtCHW = st.checkbox("District CHW")
        districtCHW_df = filtered_df[filtered_df["District Steam (Yes or No)"] == "yes"]
        if districtCHW:
            st.subheader(f"There are {districtCHW_df.shape[0]} buildings on the district steam/CHW loop")    

        districtElec = st.checkbox("District Electricity")
        districtTElec_df = filtered_df[filtered_df["District Electricity(Yes or No)"] == "yes"]
        if districtElec:
            st.subheader(f"There are {districtTElec_df.shape[0]} buildings on the district electric loop")
            
        label = st.checkbox("Building Names")
        
        # tiles_options = st.selectbox("Select Base Map", ["Basic", "Satellite"])
        # if tiles_options == "Basic":
        #     tiles = "cartodbpositron"
        # else:
        #     tiles='Esri WorldImagery'
        # Dropdown menu for meter number selection
        selected_meter = st.selectbox("Select Meter Number to Connect:", buildings["Meter No."].unique().tolist())


        


    with col2:
        tiles_options = st.radio("Select Base Map", ["Basic", "Satellite","Street Map"],horizontal =True)
        if tiles_options == "Basic":
            tiles = "cartodbpositron"
        elif tiles_options == "Satellite":
            tiles='Esri WorldImagery'
        else: 
            tiles='Esri WorldStreetMap'
        # Map configuration with centered view
        # center_lat = buildings["lat"].mean()
        # center_lon = buildings["lon"].mean()
        center_lat = 37.33485333	
        center_lon = -121.8813539
        
        map = create_map(center_lat, center_lon,tiles)


        # Add markers for selected buildings
        add_building_markers(map, filtered_df,"#00b3b3",7)
        if label:
            add_building_label(map, filtered_df,"#77a8a8",7)
        # # Add markers and lines based on selected buildings and meter number
        # if selected_buildings:
        #     filtered_df = buildings[buildings["name"].isin(selected_buildings)]
        # else:
        #     filtered_df = buildings


        # # Add markers based on selected buildings or all buildings
        # if selected_buildings:
        #     filtered_df = buildings[buildings["name"].isin(selected_buildings)]  # Filter DataFrame
        #     for index, row in filtered_df.iterrows():  # Iterate over filtered DataFrame
        #         circle_marker, label = create_marker(row.to_dict())
        #         map.add_child(circle_marker)  # Convert row to dictionary
        # else:
        #     for index, row in buildings.iterrows():
        #         circle_marker, label = create_marker(row.to_dict())
        #         map.add_child(circle_marker)




        # Filter by selected meter number
        if selected_meter:
            meter_df = filtered_df[filtered_df["Meter No."]==selected_meter]
            coords = meter_df[["lat", "lon"]].values.tolist()
            add_building_label(map, meter_df,"#00ace6",7)
            # # Draw markers and labels for buildings with the selected meter number
            # for index, row in meter_df.iterrows():
            #     circle_marker, label = create_marker(row.to_dict())
            #     map.add_child(circle_marker)
            #     map.add_child(label)
            
            # Draw lines if there are at least 2 points
            if len(coords) > 1:
                draw_dotted_line_meters(map,coords)


        if districtTherm:
            coords = districtTherm_df[["lat", "lon"]].values.tolist()
            add_building_markers(map, districtTherm_df,"#c94c4c",8)
            
            # add_building_label(map, districtTherm_df,"#cc0000",7)
            # Draw lines if there are at least 2 points
            # if len(coords) > 1:
            #     draw_dotted_line_districtTherm(map,coords)

        
        if districtCHW:
            coords = districtCHW_df[["lat", "lon"]].values.tolist()
            add_building_markers(map, districtCHW_df,"#05395a",6)

        if districtElec:
            coords = districtTElec_df[["lat", "lon"]].values.tolist()
            add_building_markers(map, districtTElec_df,"#eea29a",3)

            # add_building_label(map, districtTElec_df,"#e6b800",5)
            # Draw lines if there are at least 2 points
            # if len(coords) > 1:
            #     draw_dotted_line_districtElec(map,coords)

        


        # Display the map
        st_folium(map, width=1500, height=800)

        if selected_buildings:
            building_name = selected_buildings[0]  # Assuming one building is selected for now
            st.write("Building name:",building_name)
            folder_path = "Meter Data"
            file_found = False
            for file_name in os.listdir(folder_path):
                if building_name in file_name and file_name.endswith(".xlsx"):
                    file_path = os.path.join(folder_path, file_name)
                    # Load the data from the found file
                    data = load_data(file_path, "Sheet1")  # Adjust sheet name if needed
                    st.write("Data preview:", data.head(10))
                    plot_line_charts(data)
                    file_found = True
                    break
            
            if not file_found:
                st.warning("No data file found for the selected building.")


# Run the main function
if __name__ == "__main__":
    main()
