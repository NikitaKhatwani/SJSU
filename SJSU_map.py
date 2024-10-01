from re import U
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.offline as pyo
# import matplotlib.pyplot as plt
import folium as fo
from streamlit_folium import folium_static, st_folium
# from PIL import Image
import plotly.express as px
import os



# Set map container to full width
st.set_page_config(layout="wide")
# st.set_page_config(layout="centered")



@st.cache_data
def load_data(file_path,sheetName,head_no):
    # Load data from CSV or any other source
    data = pd.read_excel(file_path,sheet_name=sheetName,header=head_no)
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
        popup=f"<strong>{building['name']}:</strong><br>{building['Area']} sq.ft",
        radius=radius,
        color=color,
        fill_color=color,
        fill_opacity=1
    )
    
    # Add a label next to the circle marker
    label = fo.Marker(
        location=[building["lat"]+0.00001, building["lon"]],
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

# Function to generate map markers with labels next to the circle markers
def create_marker_ModularA(building,color,radius):
    # Create a circle marker
    circle_marker = fo.CircleMarker(
        location=[building["lat"], building["lon"]],
        popup=f"<strong>{building['name']}:</strong><br>{building['Area']} sq.ft",
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
            icon_anchor=(80, 30)  # Adjust to position label correctly
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
        if row["name"]=="MODULAR A":
            circle_marker, label = create_marker_ModularA(row.to_dict(),color,radius)
        if row["name"]=="CORPORATION YARD OFFICES":
            circle_marker, label = create_marker_ModularA(row.to_dict(),color,radius)
        if row["name"]=="CAMPUS VILLAGE GARAGE":
            circle_marker, label = create_marker_ModularA(row.to_dict(),color,radius)
        # map.add_child(circle_marker)
        map.add_child(label)

def filter_buildings(buildings, selected_buildings):
    """Filter buildings DataFrame based on selected buildings."""
    if selected_buildings:
        return buildings[buildings["name"].isin(selected_buildings)]
    return buildings

def plot_line_charts(timestamp,dfs, building_names):
    """Generate line charts for each column in the DataFrame."""

        # Convert the series to datetime for x-axis
    timestamp = pd.to_datetime(timestamp)
    
    if building_names != "Aggregated campus":
        # Create a new figure for the selected buildings
        fig = go.Figure()
    
        for column in dfs[0].columns:  # Assuming all DataFrames have the same columns
            chart_data = pd.DataFrame()
            chart_data['Timestamp'] = timestamp
            
            # Add each building's data to the chart data
            for i, df in enumerate(dfs):
                df[column] = pd.to_numeric(df[column], errors='coerce')
                building_name = building_names[i]
                building_data = df[column].values
                chart_data[f'{building_name} ({column})'] = building_data
            
            # Melt the DataFrame to a long format (not needed for Plotly)
            
            # Plot each building's data
            for building in chart_data.columns[1:]:  # Skip the Timestamp column
                fig.add_trace(
                    go.Scatter(
                        x=chart_data['Timestamp'],
                        y=chart_data[building],
                        mode='lines',
                        name=building
                    )
                )
    
        # Set the title and axis labels
        fig.update_layout(
            title=f'{column}',
            xaxis_title='Timestamp',
            yaxis_title=column,
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1d", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            )
        )
    
        # Show the figure
        st.plotly_chart(fig, use_container_width=True)

    if building_names == "Aggregated campus":
        # Create a new figure for the selected buildings
        fig = go.Figure()
        
        # Prepare data for each building
        for column in dfs.columns:  # Assuming all DataFrames have the same columns
            dfs[column] = pd.to_numeric(dfs[column], errors='coerce')
            building_data = dfs[column].values
            
            # Assign colors based on column names
            if 'heating' in column.lower():
                color = 'red'
            elif 'cooling' in column.lower():
                color = 'blue'
            elif 'elec' in column.lower():
                color = 'gray'
            else:
                color = 'black'  # Default color if none match
    
            fig.add_trace(
                go.Scatter(x=timestamp, y=building_data, mode='lines', name=f'{building_names} ({column})', line=dict(color=color))
            )
    
        # Set the title and axis labels
        fig.update_layout(
            title='Aggregated Campus Loads Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Aggregated Campus Loads (kBtu)',
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1d", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            )
        )
        
        # Show the figure
        st.plotly_chart(fig, use_container_width=True)

def main():

    st.header("SJSU Energy Use")
    # Load data
    buildings = load_data("sjsu_buildings.xlsx","sjsu_buildings",0)

    buildings_TMY_loads = load_data("TMY SJSU Hourly All Buildings_excel.xlsx","TMY SJSU Hourly All Buildings",0)
    # Ensure timestamp is a datetime object
    buildings_TMY_loads['timestamp'] = pd.to_datetime(buildings_TMY_loads['timestamp'])
    # Group by the timestamp and sum the three columns
    aggregate_df = buildings_TMY_loads.groupby('timestamp', as_index=False).agg({
        'total misc.elec': 'sum',
        'heating.load.kBtu': 'sum',
        'cooling.load.kBtu': 'sum'
    })
    
    timestamp_TMY = aggregate_df['timestamp']
    aggregate_df = aggregate_df.drop('timestamp', axis=1, errors='ignore')

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

        gas = st.checkbox("Gas")
        gas_df = filtered_df[filtered_df["Gas (Yes or No)"] == "Y"]
        if gas:
            st.subheader(f"There are {gas_df.shape[0]} buildings with a gas connection")
            
        label = st.checkbox("Building Names")
        

        shared_meter = st.checkbox("Shared meters")


        


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

        if not shared_meter:
        # Add markers for selected buildings
            add_building_markers(map, filtered_df,"#00b3b3",7)






        # Filter by selected meter number
        if shared_meter:

            buildings.columns = buildings.columns.str.strip()

            filtered_bldg = buildings.dropna(subset=['Sharing meters'])
            filtered_df = filtered_bldg[filtered_bldg['Sharing meters'] != ""]
            add_building_markers(map, filtered_df,"#00b3b3",7)
            
            unique_sharing_meters = filtered_bldg['Sharing meters'].unique()

            for text in unique_sharing_meters:
                # Filter DataFrame for the current text
                filtered_df_2 = filtered_bldg[filtered_bldg['Sharing meters'] == text]
                
                # Extract coordinates for this text
                coordinates = filtered_df_2[["lat", "lon"]].values.tolist()

                draw_dotted_line_meters(map,coordinates)

        if label:
            add_building_label(map, filtered_df,"#77a8a8",7)

        if districtTherm:
            coords = districtTherm_df[["lat", "lon"]].values.tolist()
            add_building_markers(map, districtTherm_df,"#c94c4c",9)
            
            # add_building_label(map, districtTherm_df,"#cc0000",7)
            # Draw lines if there are at least 2 points
            # if len(coords) > 1:
            #     draw_dotted_line_districtTherm(map,coords)

        
        if districtCHW:
            coords = districtCHW_df[["lat", "lon"]].values.tolist()
            add_building_markers(map, districtCHW_df,"#05395a",7)

        if districtElec:
            coords = districtTElec_df[["lat", "lon"]].values.tolist()
            add_building_markers(map, districtTElec_df,"#e09501",4)


        if gas:
            coords = gas_df[["lat", "lon"]].values.tolist()
            add_building_markers(map, gas_df,"#b61119",2)
        


        # Display the map
        st_folium(map, width=1500, height=800)
    st.subheader("Data Visualization")
    st.subheader("Pick Data for Visualization")
    measured_usage = st.checkbox("Measured Usage")
    CS_loads = st.checkbox("CS Loads")
    aggregated_loads = st.checkbox("Campus aggrgated loads")
    # Load data
    combined_buildings_data = load_data("SJSU_SkySpark Data_Compiled_v2.0.xlsx","SkYSPark Data_w Will's Data",1)
    AEDA_buildings_data = load_data("20240906_SJSU_AEDA_Draft.xlsx","Inputs",3)
    
    combined_buildings_data["Building Name"] = combined_buildings_data["Building Name"].str.lower()
    AEDA_buildings_data["metadata.building_name"] = AEDA_buildings_data["metadata.building_name"].str.lower()
    elec_columns_to_select = [f"measurement.E.{i}" for i in range(1, 13)]
    gas_columns_to_select = [f"measurement.G.{i}" for i in range(1, 13)]
    steam_columns_to_select = [f"measurement.S.{i}" for i in range(1, 13)]
    CHW_columns_to_select = [f"measurement.C.{i}" for i in range(1, 13)]

    buildings_TMY_loads["building_name"] = buildings_TMY_loads["building_name"].str.lower()

    dfs = []
    df_CS = []
    building_names = []
    numbered_meters_list=[]
    combined_EUIdf = pd.DataFrame()

    # if selected_buildings:
    for building_name in selected_buildings:
        building_name = building_name.lower()
        # building_name = selected_buildings[0].lower()  # Assuming one building is selected for now

        if building_name == "Campus Village A".lower():
                building_name = "Campus Village 1".lower()

        if building_name == "Campus Village B".lower():
                st.warning("Campus Village A, B and C are combined under the Campus Village 1 meter. The data for this meter has been put under Campus Village A. Please select Campus Village A to view their combined usage.")

        
        if building_name == "Campus Village C".lower():
                st.warning("Campus Village A, B and C are combined under the Campus Village 1 meter. The data for this meter has been put under Campus Village A. Please select Campus Village A to view their combined usage.")

        if building_name == "spx central":
                building_name = "spx central & east".lower()

        if building_name == "spx east":
                st.warning("SPX east shares the same meter as SPX central. Please select SPX central to view their combined usage.")

        if building_name == "dudley moorehead hall":
                building_name = "Dudley Moorehead Hall + IRC".lower()

        if building_name == "INSTRUCTIONAL RESOURCE CENTER".lower():
                st.warning("Intructional resource center shares the same meter as Dudley Moorehead Hall. Please select Dudley Moorehead Hall to view their combined usage.")

        if building_name == "Modular F".lower():
                building_name = "Modular F,A,B".lower()

        if building_name == "Modular A".lower():
                st.warning("Modular A and Modular B share the same meter as Modular F. Please select Modular F to view their combined usage.")

        if building_name == "Modular B".lower():
                st.warning("Modular B and Modular A share the same meter as Modular F. Please select Modular F to view their combined usage.")

        if building_name == "corporation yard offices".lower():
                building_name = "corporation yard offices+yard trades".lower()

        if building_name == "Corporation Yard Trades Building".lower():
                st.warning("Corporation Yard Trade shares the same meter as Corporation Yard Offices. Please select Corporation Yard Offices to view their combined usage.")


        if building_name == "Boccardo Business Classroom Building".lower():
                building_name = "Boccardo Business Classroom Building +Business Tower".lower()

        if building_name == "Business Tower".lower():
                st.warning("Business Tower shares the same meter as Boccardo Business Classroom Building. Please select Boccardo Business Classroom Building to view their combined usage.")


        if building_name == "Moss Landing Marine Lab Main Laboratory".lower():
                building_name = "Moss Landing Marine Lab Main Laboratory +aquaculture facility +marine operations".lower()

        if building_name == "Moss Landing Marine Lab Aquaculture Facility".lower():
                st.warning("All meters for the Moss Landing Marine Lab Aquaculture Facility & Marine Operations have been combined with the main laboratory meter. Please select Moss Landing Marine Lab Main Laboratory to view their combined usage")


        if building_name == "Joe West Hall (Stu Res)".lower():
                building_name = "Joe West Hall".lower()
        
        if building_name in AEDA_buildings_data["metadata.building_name"].values:
            electricity = AEDA_buildings_data.loc[AEDA_buildings_data["metadata.building_name"]==building_name,elec_columns_to_select].values.squeeze()
            gas = AEDA_buildings_data.loc[AEDA_buildings_data["metadata.building_name"]==building_name,gas_columns_to_select].values.squeeze()
            steam = AEDA_buildings_data.loc[AEDA_buildings_data["metadata.building_name"]==building_name,steam_columns_to_select].values.squeeze()
            CHW = AEDA_buildings_data.loc[AEDA_buildings_data["metadata.building_name"]==building_name,CHW_columns_to_select].values.squeeze()
            # elect = combined_buildings_data
            meters = combined_buildings_data.loc[combined_buildings_data["Building Name"]==building_name,"List of meter names"].dropna().values.tolist()
            timestamp = combined_buildings_data.loc[combined_buildings_data["Building Name"]==building_name,"Timestamp"].reset_index(drop=True)
            timestamp_2018 = combined_buildings_data.loc[combined_buildings_data["Building Name"]=="SPX Central & east".lower(),"Timestamp"].reset_index(drop=True)
            timestamp_2023 = combined_buildings_data.loc[combined_buildings_data["Building Name"]=="Art".lower(),"Timestamp"].reset_index(drop=True)

            CS_elec = buildings_TMY_loads.loc[buildings_TMY_loads["building_name"]==building_name,"total misc.elec"].reset_index(drop=True)
            CS_heating = buildings_TMY_loads.loc[buildings_TMY_loads["building_name"]==building_name,"heating.load.kBtu"].reset_index(drop=True)
            CS_cooling = buildings_TMY_loads.loc[buildings_TMY_loads["building_name"]==building_name,"cooling.load.kBtu"].reset_index(drop=True)
            timestamp_TMY = buildings_TMY_loads.loc[buildings_TMY_loads["building_name"]==building_name,"timestamp"].reset_index(drop=True)

            if timestamp.isna().all():

                timestamp = timestamp_2023

   
            # Combine Series into a DataFrame
            data_measured = pd.DataFrame({'Electricity (kWh) Usage': electricity, 'Gas (Therms) Usage': gas, 'Steam (Therms) Usage': steam, "Chilled Water (Ton-Hours)":CHW})
            data_TMY_CS = pd.DataFrame({'CS Electricity Loads(kBtu)': CS_elec,"CS Heating Loads(kBtu)":CS_heating,"CS Cooling Loads(kBtu)":CS_cooling})

            # Create a numbered list
            measured_totalEUI = [round(AEDA_buildings_data.loc[AEDA_buildings_data["metadata.building_name"]==building_name,"measurement.eui.total"].values[0])]
            measured_elecEUI = [round(AEDA_buildings_data.loc[AEDA_buildings_data["metadata.building_name"]==building_name,"measurement.eui.E"].values[0])]
            measured_gasEUI = [round(AEDA_buildings_data.loc[AEDA_buildings_data["metadata.building_name"]==building_name,"measurement.eui.G"].values[0])]
            measured_steamEUI = [round(AEDA_buildings_data.loc[AEDA_buildings_data["metadata.building_name"]==building_name,"eui.measurement.S"].values[0])]
            measured_chwEUI = [round(AEDA_buildings_data.loc[AEDA_buildings_data["metadata.building_name"]==building_name,"measurement.eui.C"].values[0])]
            EUI_df = pd.DataFrame({'Building Name':[building_name],'Total EUI': measured_totalEUI,'Elec EUI':measured_elecEUI,'Gas EUI':measured_gasEUI,'Steam EUI':measured_steamEUI,'CHW EUI':measured_chwEUI},index=[0])
            combined_EUIdf = pd.concat([combined_EUIdf, EUI_df], ignore_index=True)
            # st.write(f"{building_name}:")
            # st.write(f"Total Site EUI:{measured_totalEUI}, Elec EUI:{measured_elecEUI}, Gas EUI:{measured_gasEUI}, Steam EUI:{measured_steamEUI}, CHW EUI:{measured_chwEUI}")
            numbered_meters = "\n".join(f"{i+1}. {item}" for i, item in enumerate(meters))
            numbered_meters_list.append(numbered_meters)

            dfs.append(data_measured)
            df_CS.append(data_TMY_CS)
            building_names.append(building_name)
    




    if dfs:
        # st.write("222",dfs)
        if measured_usage:
            st.write("Measured EUIs:")
            st.write(combined_EUIdf)
            meter_name = st.checkbox("Load Meter Names")
            if meter_name:
                for index,meterList in enumerate(numbered_meters_list):     
                    st.write(f"**{building_names[index].title()} Meters:**")
                    st.write(f"{meterList}")
            plot_line_charts(timestamp, dfs, building_names)
        if CS_loads:
            load_CSdata = st.checkbox("Load Data Table")
            if load_CSdata:
                for index,df in enumerate(df_CS):
                    st.write(f"**{building_names[index].title()} Loads:**")
                    st.write(df)
                st.write("**Aggregated Campus loads:**", aggregate_df)
            plot_line_charts(timestamp_TMY, df_CS, building_names)

    else:
        st.warning("No data found for the selected buildings.")

    if aggregated_loads:
            plot_line_charts(timestamp_TMY, aggregate_df, "Aggregated campus")

    

# Run the main function
if __name__ == "__main__":
    main()
