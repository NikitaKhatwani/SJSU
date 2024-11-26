from re import U
import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.offline as pyo
import folium as fo
from streamlit_folium import folium_static, st_folium
# from PIL import Image
import plotly.express as px
import os
from functools import reduce



# Set map container to full width
st.set_page_config(layout="wide")
# st.set_page_config(layout="centered")

# Clear cache button
if st.button("Clear Cache"):
    st.cache_data.clear()
    st.success("Cache cleared!")

@st.cache_data
def load_data(file_path,sheetName,head_no):
    # Determine file extension
    file_extension = os.path.splitext(file_path)[-1].lower()

    # Use appropriate engine based on file type
    if file_extension == ".xlsb":
        data = pd.read_excel(file_path, sheet_name=sheetName, header=head_no, engine="pyxlsb")
    else:
        data = pd.read_excel(file_path, sheet_name=sheetName, header=head_no)  # Default engine

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
        popup=f"<strong>{building['name']}:</strong><br>{building['Area']} sq.ft<br>{building['Building Use Type']}",
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
        popup=f"<strong>{building['name']}:</strong><br>{building['Area']} sq.ft<br>{building['Building Use Type']}",
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

def plot_line_charts(timestamp,dfs, building_names,title_chart):
    """Generate line charts for each column in the DataFrame."""

    # Convert the series to datetime for x-axis
    # timestamp = pd.to_datetime(timestamp,errors='coerce')

    if building_names != "Aggregated campus":
        for column in dfs[0].columns:  # Assuming all DataFrames have the same columns

            chart_data = pd.DataFrame()
            chart_data['Timestamp'] = timestamp
            
            # Add each building's data to the chart data
            for i, df in enumerate(dfs):
                if column == "Simultaneuos Loads(H)" :
                     continue
                if column == "Simultaneuos Loads(C)" :
                     continue
                df[column] = pd.to_numeric(df[column], errors='coerce')
                building_name = building_names[i]
                
                building_data = df[column].values
                chart_data[f'{building_name} ({column})'] = building_data
                if column == "CS Heating Loads(kBtu)" and i==0:
                    chart_data["Simultaneuos Loads(H)"] = df["Simultaneuos Loads(H)"].values
                if column == "CS Cooling Loads(kBtu)" and i==0:
                    chart_data["Simultaneuos Loads(C)"] = df["Simultaneuos Loads(C)"].values


            # Check if the column has any valid data
            if chart_data[chart_data.columns[1:]].isnull().all().all():  # Check if all values are NaN
                continue  # Skip this column if it has no valid data
                
            # Create a new figure for each column
            fig = go.Figure()
            
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

        chart_data = pd.DataFrame()
        chart_data['Timestamp'] = timestamp

        
        # Initialize a variable to track the cumulative offset
        cumulative_offset = np.zeros(len(timestamp))  # Shape: (8760,)
        
        for column in dfs.columns:  # Assuming all DataFrames have the same columns
            if 'elec' in column.lower():
                continue
            dfs[column] = pd.to_numeric(dfs[column], errors='coerce')
            building_data = dfs[column].values
        
            # Assign colors based on column names
            if 'cs heating' in column.lower():
                color = 'rgba(255, 0, 0, 0.8)'  # Semi-transparent red for heating
                building_data = -building_data  # Mirror image for heating
                fill = 'tozeroy'  # Fill to zero
                
            # Assign colors based on column names
            elif 'space Heating + dhw' in column.lower():
                color = 'rgba(255, 165, 0, 0.5)'  # Semi-transparent red for heating
                building_data = -building_data  # Mirror image for heating
                fill = 'tozeroy'  # Fill to zero

            # Assign colors based on column names
            elif 'total heating' in column.lower():
                color = 'rgba(128, 0, 0, 0.5)'  # Semi-transparent red for heating
                building_data = -building_data  # Mirror image for heating
                fill = 'tozeroy'  # Fill to zero
        
            elif 'dhw' in column.lower():
                continue
                # color = 'rgba(0, 0, 0, 0.5)'  # Light green with 50% transparency for DHW
                # building_data = -building_data 
                # fill = 'tozeroy'
                
            elif 'cooling' in column.lower():
                color = 'rgba(0, 0, 255, 0.5)'  # Semi-transparent blue for cooling
                fill = 'tozeroy'  # Fill to zero
            elif 'elec' in column.lower():
                color = 'gray'
                fill = 'tozeroy'  # Fill to zero
            elif  "Simultaneuos Loads(H)".lower() in column.lower():

                color = 'rgba(255, 165, 0, 1)'  # Semi-transparent orange
                building_data = -building_data
                fill = 'tozeroy'
            elif "Simultaneuos Loads(C)".lower() in column.lower():
                color = 'rgba(255, 165, 0, 1)'  # Light blue
                fill = 'tozeroy'
            else:
                color = 'black'  # Default color if none match
                fill = 'tozeroy'

            fig.add_trace(
                go.Scatter(
                    x=chart_data['Timestamp'],
                    y=building_data,
                    mode='lines',
                    name=f'{building_names} ({column})',
                    line=dict(color=color),
                    fill=fill,  # Fill to zero
                    fillcolor=color  # Use the defined color for the fill
                )
            )
        
        # Set the title and axis labels
        fig.update_layout(
            title=title_chart,
            xaxis_title='Timestamp',
            yaxis_title=f'{title_chart} (kBtu)',
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


    st.header("SJSU Loads & Energy Use")

    # Load data
    buildings = load_data("sjsu_buildings.xlsx","sjsu_buildings",0)

    # #load timestamp
    timestamp_hourly = load_data("Hourly TImestamp.xlsx","Sheet1",0)

    buildings_TMY_loads = load_data("TMY SJSU Hourly All Buildings_excel_binary.xlsb","TMY SJSU Hourly All Buildings",0)
    # Ensure timestamp is a datetime object
    buildings_TMY_loads['timestamp'] = pd.to_datetime(buildings_TMY_loads['timestamp'])
    #filter main campus buildings
    main_campus_buildings = buildings[buildings["Campus"]=="Main campus"]

    #filter CS loads df to main campus
    main_campus_TMY_CS_loads = buildings_TMY_loads[buildings_TMY_loads["building_name"].isin(main_campus_buildings["name"])]
    
    # Group by the timestamp and sum the three columns
    aggregate_df = main_campus_TMY_CS_loads.groupby('timestamp', as_index=False).agg({
        'total misc.elec': 'sum',
        'heating.load.kBtu': 'sum',
        'cooling.load.kBtu': 'sum'
    })
    
    timestamp_TMY = aggregate_df['timestamp']
    aggregate_df = aggregate_df.drop('timestamp', axis=1, errors='ignore')

    unique_programs_MC = main_campus_buildings["Building Use Type"].unique().tolist()
    unique_regions = buildings["Region"].unique().tolist()
    

    # combined_buildingNames_programs = list(set(buildings["name"].tolist()+ unique_programs_MC.tolist()))
    # st.write("unique_programs_MC", type(unique_programs_MC),unique_programs_MC)

    # Create two columns
    col1, col2 = st.columns([1, 3])  # You can adjust the width ratio as needed

    with col1:
        # Filter control for interactivity
        selected_buildings = st.multiselect("Select Buildings to View:", buildings["name"].tolist())
        selected_program_MC = st.multiselect("Select Program Type to View (Main Campus only):", unique_programs_MC)
        selected_regions = st.multiselect("Select Region to View:", unique_regions)

        if selected_program_MC:
            selected_buildings_program = main_campus_buildings[main_campus_buildings["Building Use Type"].isin(selected_program_MC)]["name"].tolist()

            # Combine and get unique elements
            selected_buildings = list(set(selected_buildings) | set(selected_buildings_program))

        if selected_regions:
            selected_regions_list = buildings[buildings["Region"].isin(selected_regions)]["name"].tolist()

            # Combine and get unique elements
            selected_buildings = list(set(selected_buildings) | set(selected_regions_list))

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

        if selected_buildings !=[]:
            st.write("The following buildings have been selected:", ", ".join(selected_buildings))


        


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


    st.subheader("Pick Data for Visualization")
    measured_usage = st.checkbox("Measured Usage")
    CS_loads = st.checkbox("CS Loads")
    # aggregated_loads = st.checkbox("Main Campus aggregated loads")
    selected_aggregated_loads = st.checkbox("Selected buildings aggregated loads")

    # Load data
    combined_buildings_data = load_data("SJSU_SkySpark Data_Compiled_v2.0.xlsx","SkYSPark Data_w Will's Data",1)
    AEDA_buildings_data = load_data("20240918_SJSU_AEDA_Draft.xlsx","Inputs",3)
    
    combined_buildings_data["Building Name"] = combined_buildings_data["Building Name"].str.lower()
    AEDA_buildings_data["metadata.building_name"] = AEDA_buildings_data["metadata.building_name"].str.lower()
    AEDA_buildings_data["metadata.building_name"] = AEDA_buildings_data["metadata.building_name"].str.strip()
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
    results_df_CS = pd.DataFrame()

    # Get the list of missing buildings
    missing = st.checkbox("Missing Buildings")
    missing_buildings = buildings[~buildings["name"].str.lower().isin(AEDA_buildings_data["metadata.building_name"])]
    if missing:
        st.write("Missing AEDA buildings",missing_buildings["name"])

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

        if building_name == "Dudley Moorhead Hall".lower():
                building_name = "Dudley Moorehead Hall + IRC".lower()

        if building_name == "INSTRUCTIONAL RESOURCE CENTER".lower():
                st.warning("Intructional resource center shares the same meter as Dudley Moorehead Hall. Please select Dudley Moorehead Hall to view their combined usage.")

        if building_name == "Modular F".lower():
                building_name = "Modular F,A,B".lower()

        if building_name == "Modular A".lower():
                st.warning("Modular A and Modular B share the same meter as Modular F. Please select Modular F to view their combined usage.")
                continue
        
        if building_name == "Modular B".lower():
                st.warning("Modular B and Modular A share the same meter as Modular F. Please select Modular F to view their combined usage.")
                continue
        
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


        # if building_name in AEDA_buildings_data["metadata.building_name"].values or building_name in buildings_TMY_loads["building_name"].values:
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
            CS_dhw = buildings_TMY_loads.loc[buildings_TMY_loads["building_name"]==building_name,"DHW.load.kBtu"].reset_index(drop=True)
            CS_otherProcess = buildings_TMY_loads.loc[buildings_TMY_loads["building_name"]==building_name,"OtherProcess.load.kBtu"].reset_index(drop=True)
            # timestamp_TMY = buildings_TMY_loads.loc[buildings_TMY_loads["building_name"]=="4th Street Building".lower(),"timestamp"].reset_index(drop=True)
            timestamp_TMY = timestamp_hourly

            if timestamp.isna().all():
                timestamp = timestamp_2023

   
            # Combine Series into a DataFrame
            data_measured = pd.DataFrame({'Electricity (kWh) Usage': electricity, 'Gas (Therms) Usage': gas, 'Steam (Therms) Usage': steam, "Chilled Water (Ton-Hours)":CHW})
            data_TMY_CS = pd.DataFrame({'CS Electricity Loads(kBtu)': CS_elec,"CS Heating Loads(kBtu)":CS_heating,"CS Cooling Loads(kBtu)":CS_cooling,"CS DHW Loads(kBtu)":CS_dhw,"Other Heating Proces(kBtu)":CS_otherProces})

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

    # Create a copy of the list of DataFrames
    df_CS2 = [df.copy() for df in df_CS]  # Use a list comprehension to copy each DataFrame

    if df_CS2:
        # Sum the DataFrames
        final_df_CS = reduce(lambda x, y: x.add(y, fill_value=0), df_CS2)
        final_df_CS["Space Heating + DHW"] = final_df_CS["CS Heating Loads(kBtu)"] + final_df_CS["CS DHW Loads(kBtu)"]
        st.write("sss",final_df_CS["Space Heating + DHW"] )
        final_df_CS["Total Heating Loads"] = final_df_CS["CS Heating Loads(kBtu)"] + final_df_CS["CS DHW Loads(kBtu)"] + final_df_CS["Other Heating Proces(kBtu)"]
        final_df_CS["Simultaneuos Loads(H)"] = np.where(
                                                    final_df_CS["CS Cooling Loads(kBtu)"] * 1.3 > final_df_CS["Total Heating Loads"],
                                                    final_df_CS["Total Heating Loads"],
                                                    final_df_CS["CS Cooling Loads(kBtu)"]*1.3
                                                )
        final_df_CS["Simultaneuos Loads(C)"] = final_df_CS["Simultaneuos Loads(H)"]/1.3
        df_CS[0]["Simultaneuos Loads(H)"] = final_df_CS["Simultaneuos Loads(H)"]
        df_CS[0]["Simultaneuos Loads(C)"] = final_df_CS["Simultaneuos Loads(C)"]
        # final_df_CS["Simultaneuos Loads(H)"] =final_df_CS[["Total Heating Loads","CS Cooling Loads(kBtu)"]].min(axis=1)
        max_simult_h_load = round(final_df_CS["Simultaneuos Loads(H)"].max())
        max_simult_c_load = round(final_df_CS["Simultaneuos Loads(C)"].max())
        total_simult_h_load = round(final_df_CS["Simultaneuos Loads(H)"].sum())
        total_simult_c_load = round(final_df_CS["Simultaneuos Loads(C)"].sum())
        total_heating_load = round(final_df_CS["Total Heating Loads"].sum())
        total_cooling_load = round(final_df_CS["CS Cooling Loads(kBtu)"].sum())

        # Check if total_heating_load is 0 before calculating the percentage
        if total_heating_load != 0:
            percent_sim_heating = (total_simult_h_load / total_heating_load) * 100
        else:
            percent_sim_heating = 0  # or handle as needed, e.g., set to None or display a warning

        percent_sim_cooling = (total_simult_c_load/total_cooling_load)*100


        results_df_CS["Peak Simultaneuos Heating Loads"] =pd.NA
        results_df_CS.at[0,"Peak Simultaneuos Heating Loads"] = max_simult_h_load
        results_df_CS["Peak Simultaneuos Cooling Loads"] =pd.NA
        results_df_CS.at[0,"Peak Simultaneuos Cooling Loads"] = max_simult_c_load
        results_df_CS["Total Simultaneuos Heating Loads"] =pd.NA
        results_df_CS.at[0,"Total Simultaneuos Heating Loads"] = total_simult_h_load
        results_df_CS["Total Simultaneuos Cooling Loads"] =pd.NA
        results_df_CS.at[0,"Total Simultaneuos Cooling Loads"] = total_simult_c_load
        results_df_CS["Total Heating Loads"] =pd.NA
        results_df_CS.at[0,"Total Heating Loads"] = total_heating_load
        results_df_CS.at[1,"Total Simultaneuos Heating Loads"] = f"{round(percent_sim_heating, 1)}%"
        results_df_CS["Total Cooling Loads"] =pd.NA
        results_df_CS.at[0,"Total Cooling Loads"] = total_cooling_load
        results_df_CS.at[1,"Total Simultaneuos Cooling Loads"] = f"{round(percent_sim_cooling, 1)}%"
        results_df_CS.dropna(how='all', inplace=True)





        # Show the result
        st.write("**Aggregated & Simultaneous Loads:**")
        st.write(final_df_CS)
        st.write("**Simultaneous Totals:**")
        st.write(results_df_CS)
        saveGroup = st.checkbox("Save Group Results?")


        
        # Initialize saved_df in session state if it doesn't exist
        if 'saved_df' not in st.session_state:
            st.session_state.saved_df = pd.DataFrame(columns=[
                "Building Names",
                "Peak Simultaneuos Heating Loads",
                "Peak Simultaneuos Cooling Loads",
                "Total Simultaneuos Heating Loads",
                "Total Simultaneuos Cooling Loads",
                "Total Heating Loads",
                "Total Cooling Loads"
            ])

        if saveGroup:
             # Select the relevant columns from final_df_CS
             data_to_append = results_df_CS[["Peak Simultaneuos Heating Loads","Peak Simultaneuos Cooling Loads","Total Simultaneuos Heating Loads","Total Simultaneuos Cooling Loads","Total Heating Loads",
                "Total Cooling Loads"]]
             data_to_append["Building Names"] = pd.NA
             data_to_append["Program Type"] = pd.NA
             data_to_append.at[data_to_append.index[0], "Building Names"] = ", ".join(selected_buildings)
             program_selected_bldgs = buildings.loc[buildings["name"].isin(selected_buildings),"Building Use Type"].unique()
             data_to_append.at[data_to_append.index[0], "Program Type"] = ", ".join(program_selected_bldgs)
            # Drop empty rows
             st.session_state.saved_df.dropna(how='all', inplace=True)

            # Use pd.concat for appending
            # Concatenate to the existing saved_df
             st.session_state.saved_df = pd.concat([st.session_state.saved_df, data_to_append], ignore_index=True)   
             st.session_state.saved_df.dropna(how='all', inplace=True)
            # Ensure "Building Names" is of type string
             st.session_state.saved_df["Building Names"] = st.session_state.saved_df["Building Names"].astype(str)
             st.session_state.saved_df["Program Type"] = st.session_state.saved_df["Program Type"].astype(str)

             
        st.write(f"**Saved results:**")
        st.write(st.session_state.saved_df)
        # st.write(st.session_state.saved_df)





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
            plot_line_charts(timestamp, dfs, building_names,"measured")
        if CS_loads:
            load_CSdata = st.checkbox("Load Data Table")
            if load_CSdata:
                for index,df in enumerate(df_CS):
                    st.write(f"**{building_names[index].title()} Loads:**")
                    st.write(df)
                st.write("**Aggregated Campus loads:**", aggregate_df)
            plot_line_charts(timestamp_TMY, df_CS, building_names,"carbon signal loads")





    else:
        st.warning("No data found for the selected buildings.")

    # if aggregated_loads:
    #         plot_line_charts(timestamp_TMY, aggregate_df, "Aggregated campus","Main campus aggregated loads")


    if selected_aggregated_loads:
        if df_CS2:
            aggregate_selected_df = final_df_CS[["CS Electricity Loads(kBtu)","CS Heating Loads(kBtu)","CS Cooling Loads(kBtu)","CS DHW Loads(kBtu)","Other Heating Proces(kBtu)","Total Heating Loads","Simultaneuos Loads(H)","Simultaneuos Loads(C)"]]


            
            aggregate_monthly = pd.DataFrame()

            aggregate_monthly = final_df_CS[["CS Electricity Loads(kBtu)","CS Heating Loads(kBtu)","CS Cooling Loads(kBtu)","CS DHW Loads(kBtu)","Other Heating Proces(kBtu)","Total Heating Loads","Simultaneuos Loads(H)","Simultaneuos Loads(C)"]]
            aggregate_monthly['timestamp'] = timestamp_TMY
            # Assuming final_df_CS is your DataFrame and 'timestamp_TMY' is the timestamp column
            # aggregate_monthly['timestamp'] = pd.to_datetime(timestamp_TMY)  # Convert to datetime if not already
            # Set the timestamp as the index
            aggregate_monthly.set_index('timestamp', inplace=True)
            # Resample and sum by month
            monthly_sum = aggregate_monthly.resample('M').sum()

            # If you want to reset the index to have 'timestamp' as a column again
            monthly_sum.reset_index(inplace=True)
            timestamp_monthly = monthly_sum['timestamp']
            monthly_sum.drop('timestamp', axis=1, inplace=True)
            st.write("monthly_sum",monthly_sum)
            plot_line_charts(timestamp_TMY, aggregate_selected_df, "Aggregated campus","Selected campus aggregated hourly loads")
            plot_line_charts(timestamp_monthly, monthly_sum, "Aggregated campus","Selected campus aggregated monthly loads")

    

# Run the main function
if __name__ == "__main__":
    main()
