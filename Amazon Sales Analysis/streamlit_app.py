import pandas as pd
import numpy as np
import requests
import string
import os
from io import StringIO
import streamlit as st
from streamlit_option_menu import option_menu
import warnings 
from datetime import datetime, timedelta
import plotly.express as px
import base64


#import streamlit as st
st.set_page_config(
    layout="wide", 
    page_title="Amazon Indian Regional Sales",
    initial_sidebar_state="expanded",
)

#ETL Process Stage: 
# Function to import the CSV data: 
def read_csv_from_url(url: str, encoding='ISO-8859-1') -> pd.DataFrame:
    try:
        response = requests.get(url)
        response.raise_for_status() 
           
        csv_text = StringIO(response.text)  
           
        data = pd.read_csv(csv_text, encoding=encoding)
        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the CSV file from {url}: {e}")
    except pd.errors.EmptyDataError:
        print(f"No data found in the CSV file at {url}.")
    except pd.errors.ParserError:
        print(f"Error parsing the CSV file at {url}.")
    except Exception as e:
        print(f"An error occurred while reading the CSV file at {url}: {e}")
    return pd.DataFrame() 


# Importing the Data: 
path= "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/refs/heads/main/Amazon%20Sales%20Analysis/Amazon%20Sale%20Report.csv"
df  = read_csv_from_url(path, encoding='ISO-8859-1')

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

df['Year'] = df['Date'].dt.year

df['Month']=  df['Date'].dt.month

df['Amount'] = df['Amount'].fillna(0)

df['Amount'] = df['Amount']*0.01150

# Function to format as currency:
def format_currency(value):
    value = float(value)
    return "${:,.2f}".format(value)

#df['Amount'] = df['Amount'].apply(format_currency)

# Mapping the Month Column: 
month_order = {1:'January', 
               2:'February', 
               3:'March', 
               4:'April', 
               5:'May', 
               6:'June', 
               7:'July', 
               8:'August', 
               9:'September', 
               10:'October', 
               11:'November', 
               12:'December'
            }

df['Month'] =  df['Month'].map(month_order)

# Convert 'Month_Name' to a categorical type with a specified order
df['Month'] = pd.Categorical(df['Month'], categories=list(month_order.values()), ordered=True)

# Sort the DataFrame by Year and Month_Name
df = df.sort_values(by=['Year', 'Month'])

print(df['ship-state'].unique())


# Rename - Configuration of the Status": 
df['Status'] = df['Status'].replace({
    'Shipped': 'In Transit-  Courier',
    'Cancelled': 'Cancelled',
    'Shipped - Delivered to Buyer':'Delivered',
    'Shipped - Returned to Seller':'Returned-Seller', 
    'Shipped - Rejected by Buyer':'Rejected',
    'Shipped - Lost in Transit':'Lost',
    'Shipped - Out for Delivery':'In Transit - Customer',
    'Shipped - Returning to Seller':'In Transit - Seller',
    'Shipped - Picked Up' 'Pending':'Delivered Waiting Collection',
    'Pending - Waiting for Pick Up':'Waiting Pick Up', 
    'Shipped - Damaged':'Damaged', 
    'Shipping':'Packing Order',
 })

#print(df['Year'].astype('str').unique())

# Rename the column that provides us with the Detail from  which website the purchase was made: 
df['Sales Channel'] = df['Sales Channel'].replace({
   'Amazon.in': 'Amazon Website', 
   'Non-Amazon': 'Non - Amazon',
})


# Creating a default Color Theme:
print(df['ship-city'].unique())
# Define the color schemes:
color_theme_list = {
    'One': ['#5d88b3', '#2e4459','#6d93ba','#becfe0','#495766', '#1d2328','#8c96a0','#d8e3ec'],
    'Two': ['#005172','#003044', '#001822', '#4c859c', '#99b9c6','#4c859c' , '#99b2bc','#668b9a'],
    'Three': ['#002748', '#193c5a', '#32526c', '#4c677e', '#667d91', '#7f93a3','#99a8b5', '#b2bec8'],
    'Four': ['#2d2a27', '#5a544e','#cac5c1','#f4f3f2','#005475', '#008cc4', '#006289', '#005475']
}
base64_image = "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/main/Amazon%20Sales%20Analysis/Images/amazon-logo-1024x683.png-1.jpg"
response =  requests.get(base64_image)
image_sidebar = response.content

# Creating a Sidebar:
with st.sidebar:
    #bst.markdown("<h3 style='text-align: left;'>SLA FILTERI</h3>", unsafe_allow_html=True)
    # Specify the relative path to the image
    
    #image_sidebar= os.path.join("Images", "amazon-logo-1024x683.png-1.jpg")  

    # Replace with your image name
    #base64_image = get_base64_image(groups_icon)
    st.image(image_sidebar)
    
    # Initial selection summary:
    if st.checkbox("Annual Report", value=True):
        selected_month = sorted(df["Month"].unique())
    else:
        selected_month = st.sidebar.multiselect("Select Month",sorted((df["Month"]).unique()),default=sorted(df["Month"].unique()))
    
    if st.checkbox("Overall Sales by State", value=True):
        selected_status = sorted(df["Status"].astype('str').unique())
    else:
        selected_status = st.multiselect("Select Product Phase",sorted((df["Status"].astype('str')).unique()), default=sorted(df["Status"].astype('str').unique()))
        
        # Initial selection summary:
    if st.checkbox("eCommerce Site:", value=True):
        ecommerce_site = sorted(df["Sales Channel"].unique())
    else:
        ecommerce_site = st.sidebar.multiselect("Sale Site",sorted((df["Sales Channel"]).unique()),default=sorted(df["Sales Channel"].unique()))
    
    selected_color_theme = st.selectbox('Select a color theme', list(color_theme_list.keys()))

# Master dataframe through which most dataframe will be made
filtering_df = df[(df['Month'].isin(selected_month)) & df['Sales Channel'].isin(ecommerce_site)]

# Renaming AR to the appropriate state name: 
#filtering_df['ship-state'].str.lower()

filtering_df.loc[filtering_df['ship-state'] == 'AR', 'ship-state'] = 'ARUNACHAL PRADESH'

# Sales_df: 
filter = ['Cancelled','Returned-Seller','Lost','Rejected','Damaged']

Sales_df = filtering_df[~filtering_df['Status'].isin(filter)]

# sales by states: 
states_log= filtering_df.groupby(['ship-state'])['Amount'].sum().reset_index()


Product_groups = Sales_df.groupby(['Category','Fulfilment', 'Status'])['Amount'].sum().reset_index()

total_Product = Product_groups.groupby('Category')['Amount'].sum().reset_index()

filtered_category_totals_new = filtering_df.groupby(['Status','Category'])['Amount'].sum().reset_index()

# Step 1: Rename all occurrences of 'A' in the 'Category' column to 'Alpha':
total_state_sales = ['Delivered','In Transit-  Courier','In Transit - Customer','Packing Order','Waiting Pick Up','Delivered Waiting Collection']

filtered_category_totals_new.loc[filtered_category_totals_new['Status'].isin(total_state_sales), 'Status'] = 'Delivered'

# Step 2: Group by the 'Category' column and sum the 'Count'
filtered_category_totals = filtered_category_totals_new.groupby(['Status','Category'], as_index=False).agg({'Amount':'sum'})

name_category_totals = filtering_df.groupby(['Category', 'Fulfilment','Status'])['Amount'].sum().reset_index()

category_totals = filtering_df.groupby(['Category', 'Fulfilment'])['Amount'].sum().reset_index()

sub_categories  = name_category_totals.groupby('Category', as_index=False)['Amount'].sum()

#sub_categories['u_service_offering_subcategory'] = name_category_totals['u_service_offering_subcategory'].replace(renaming_mapping)

#sub_categories_df =  sub_categories.groupby('Category', as_index=False)['Amount'].sum()

sub_categories_sorted = sub_categories.sort_values(by="Amount", ascending=False)

def ensure_all_states(df, required_states=None):
    if required_states is None:
        required_states = ['Delivered','Lost','Cancelled','Rejected','Damaged','Returned-Seller','In Transit - Seller']
    
    # Check for missing states
    missing_states = [state for state in required_states if state not in df['Status'].values]
    
    # Create a DataFrame for missing states with count 0
    missing_states_df = pd.DataFrame({'Status': missing_states, 'Amount': [0] * len(missing_states)})
    
    # Concatenate the original DataFrame with the missing states DataFrame
    df = pd.concat([df, missing_states_df], ignore_index=True)
    
    return df

# Step 1: Group by 'assignment_group' and sum the 'Count'
grouped_counts = filtered_category_totals.groupby('Category')['Amount'].sum().reset_index()

# Step 2: Find the maximum count and the corresponding assignment group
max_assignment_1 = grouped_counts.loc[grouped_counts['Amount'].idxmax()]

max_assignment = max_assignment_1.loc['Category']

# Step 3: Calculate the total count of all assignment groups
total_count_groups_count= grouped_counts['Amount'].sum()

max_assignement_value = int(max_assignment_1['Amount'])

# Step 4: Calculate the percentage of the maximum count relative to the total count
max_percentage = f"{float(round((max_assignment_1['Amount'] / total_count_groups_count) * 100, 3))}%"


# Calculate the Fulfilment that brought the most sales: 
def calculate_max_user(users_totals):
        # Check if DataFrame is empty
        if name_category_totals.empty:
            print("The DataFrame is empty.")
            return {"max_user": 0, "max_incident_count": 0, "percentage": 0}

        # Group by 'Fulfilment' and sum 'Count'
        total_person = name_category_totals.groupby('Fulfilment')['Amount'].sum().reset_index()

        # Check if total_person is empty
        if total_person.empty:
            print("No Products Sold to report.")
            return {"max_user": 0, "max_incident_count": 0, "percentage": 0}

        # Identify the user(s) with the maximum incident count
        max_incident_count = total_person['Amount'].max()
        max_users = total_person[total_person['Amount'] == max_incident_count]
        
        if len(max_users) > 1:
            state_priority = ['Delivered','Lost','Cancelled','Rejected','Damaged','Returned-Seller','In Transit - Seller']
            state_sums = name_category_totals[name_category_totals['Status'].isin(state_priority)].groupby(['Fulfilment', 'Status'])['Amount'].sum().unstack(fill_value=0)
            
           
            max_user = None
            max_state_sum = 0
           
            for state in state_priority:
                if state in state_sums.columns:
                    state_sums_sorted = state_sums[state].nlargest(1)
                    if state_sums_sorted.iloc[0] > max_state_sum:
                        max_state_sum = state_sums_sorted.iloc[0]
                        max_user = state_sums_sorted.index[0]
            if max_user is None:
                max_user = max_users.iloc[0]['Fulfilment']
        else:
            max_user = max_users.iloc[0]['Fulfilment']
           
        if max_user == 0 or not max_user:
            print("No user with incidents to report.")
            return {"max_user": 0, "max_incident_count": 0, "percentage": 0}
   
        #Calculate the percentage of incidents handled by the max user
        total_incident_count = total_person['Amount'].sum()
        percentage = (max_incident_count / total_incident_count) * 100 if total_incident_count > 0 else 0
        percentage = round(percentage)

        print(f"User with the highest incidents: {max_user} with {max_incident_count} incidents")
        print(f"Percentage of incidents handled by {max_user}: {percentage}%")

        return max_user, max_incident_count,percentage

max_user,max_incident_count,percentage = calculate_max_user(name_category_totals)


groups_loc = "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/main/Amazon%20Sales%20Analysis/Images/shop-solid.svg"
response =  requests.get(groups_loc)
groups_icon = response.text

# Construct the path to the SVG file
svg_icon_path = "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/main/Amazon%20Sales%20Analysis/Images/shirt-solid.svg"
response = requests.get(svg_icon_path)
svg_icon = response.text
 
# Construct the path to the SVG file
svg_progress_path = "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/main/Amazon%20Sales%20Analysis/Images/trash-solid.svg"
response = requests.get(svg_progress_path)
svg_progress = response.text

# Getting a icon using CSS stle: - Highest
svg_new_path= "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/main/Amazon%20Sales%20Analysis/Images/route-solid.svg"
response = requests.get(svg_new_path)
svg_new = response.text

# Getting a icon using CSS stle: - Highest
svg_seller_path= "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/main/Amazon%20Sales%20Analysis/Images/right-left-solid.svg"
response = requests.get(svg_seller_path)
svg_seller = response.text

# Getting a icon using CSS stle: - Highest
svg_return_path= "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/main/Amazon%20Sales%20Analysis/Images/truck-solid.svg"
response = requests.get(svg_return_path)
svg_return = response.text

# Getting a icon using CSS style: - Highest:
svg_resolved_path= "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/main/Amazon%20Sales%20Analysis/Images/money-rupee-circle-line.svg"
response = requests.get(svg_resolved_path)
svg_resolved = response.text
  
# Getting a icon using CSS style: - Highest : Fulfilment Stuff.
svg_total_path = "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/main/Amazon%20Sales%20Analysis/Images/shop-solid.svg"
reponse = requests.get(svg_total_path)
svg_total = reponse.text

# Getting a icon using CSS style: - Highest 
svg_icon_path_1= "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/main/Amazon%20Sales%20Analysis/Images/file-excel-solid.svg"
response = requests.get(svg_icon_path_1)
svg_hold = response.text


svg_cancelled_path = "https://raw.githubusercontent.com/GomolemoKototsiAnalyst/Data-Analysis-Personal-Projects/main/Amazon%20Sales%20Analysis/Images/ban-solid (1).svg"
response = requests.get(svg_cancelled_path)
svg_cancelled = response.text


def get_max_group(Product_groups, selected_states):
        # Check if DataFrame is empty
        if Product_groups.empty:
            print("The DataFrame is empty.")
            max_group = None
            group_max_incident_count = 0
            percentage_group = 0
            return None, None, 0
        
        else:
            # Group by 'assignment_group' and sum 'Incident Count'
            total_group = Product_groups.groupby('Category')['Amount'].sum().reset_index()
            
        # Check if total_group is empty
        if total_group.empty:
            print("No incidents to report.")
            group_with_max_incidents = None
            group_max_incident_count = 0
        else:
            # Identify the group with the maximum incident count
            max_group = total_group.loc[total_group['Amount'].idxmax()]
                
            # Handle ties by checking states
            tied_groups = total_group[total_group['Amount'] == max_group['Amount']]
            if len(tied_groups) > 1:
                # Check state counts for tied groups
                state_counts = Product_groups[Product_groups['Category'].isin(Product_groups['Category'])]
                state_priority = ['Delivered','Lost','Cancelled','Rejected','Damaged','Returned-Seller','In Transit - Seller']
                state_counts['state_Priority'] = pd.Categorical(state_counts['state'], categories=state_priority, ordered=True)
                state_counts = state_counts.sort_values(by=['state_Priority', 'Amount'], ascending=[True, False])
                
                max_group = state_counts.groupby('Category')['Amount'].sum().idxmax()
                
            # Extract the group's name and the incident count
            group_with_max_incidents = max_group if isinstance(max_group, str) else max_group['Category']
            group_max_incident_count = total_group.loc[total_group['Category'] == group_with_max_incidents, 'Amount'].values[0]
             
        # Calculate percentage if any incidents are present
        if group_max_incident_count > 0:
            total_group_count = total_group['Amount'].sum()
            percentage_group = (group_max_incident_count / total_group_count) * 100
            percentage_group = round(percentage_group)
        else:
            percentage_group = 0
        return group_with_max_incidents, group_max_incident_count, percentage_group
        
group_with_max_incidents, group_max_incident_count, percentage_group = get_max_group(Product_groups,selected_status)

# Creating a function to get totals:
def total_counts(df,state_list=selected_status):
    if state_list is None:
        # Default list of states to include in the total count
        state_list = ['Delivered','Lost','Cancelled','Rejected','Damaged','Returned-Seller','In Transit - Seller']
    
    # Initialize total_counts to zero
    total_counts = 0
    
    # Loop over each state in the state_list
    for state in state_list:
        # Check if the state exists in the DataFrame
        if state in df['Status'].values:
            # Add the count for the existing state
            total_counts += df.loc[df['Status'] == state, 'Amount'].values[0]
        else:
            # If the state is missing, assume its count is zero
            total_counts += 0
    
    return total_counts

def get_state_counts(df, selected_states):
    state_counts = {state: {'count': 0, 'percentage': 0.0} for state in selected_states}
    
    # Calculate the total count for all selected states
    total_count = df[df['Status'].isin(selected_states)]['Amount'].sum()
    
    # Calculate counts for each selected state
    for state in selected_states:
        count = int(df.loc[df['Status'] == state, 'Amount'].sum()) # Use sum() to handle multiple entries
        state_counts[state]['count'] = count
    
    # Calculate the percentage for each state
    if total_count > 0:
        for state in selected_states:
            state_counts[state]['percentage'] = round(float(round((state_counts[state]['count'] / total_count) * 100, 2)), 3)
    
    # Add the total count to the dictionary
    state_counts['total'] = int(total_count)
    
    return state_counts

#state_list = ['Delivered','Lost','Cancelled','Rejected','Damaged','Returned-Seller','In Transit - Seller']

# Assuming filtered_category_totals is your DataFrame and selected_status is your list of states
state_counts = get_state_counts(filtered_category_totals, selected_status)

 # Safely access the counts and percentages for each selected state
totals = {state: {
    'total': state_counts.get(state, {}).get('count', 0),
    'percentage': state_counts.get(state, {}).get('percentage', 0.0)
} for state in selected_status}

# Example of accessing specific totals
total_in_progress = int(totals.get('Damaged', {}).get('total', 0))
percentage_in_progress = f"{float(totals.get('Damaged', {}).get('percentage', 0.0))}%"

total_cancelled = int(totals.get('Cancelled', {}).get('total', 0))
percentage_cancelled = f"{float(totals.get('Cancelled', {}).get('percentage', 0.0))}%"


total_new = int(totals.get('Lost', {}).get('total', 0))
percentage_new = f"{float(totals.get('Lost', {}).get('percentage', 0.0))}%"

total_resolved = int(totals.get('Delivered', {}).get('total', 0))
percentage_resolved = f"{float(totals.get('Delivered', {}).get('percentage', 0.0))}%"

total_on_hold = int(totals.get('Rejected', {}).get('total', 0))
percentage_on_hold = f"{float(totals.get('Rejected', {}).get('percentage', 0.0))}%"

total_on_returned = int(totals.get('Returned-Seller', {}).get('total', 0))
percentage_on_returned = f"{float(totals.get('Returned-Seller', {}).get('percentage', 0.0))}%"

total_on_seller = int(totals.get('In Transit - Seller', {}).get('total', 0))
percentage_on_seller = f"{float(totals.get('In Transit - Seller', {}).get('percentage', 0.0))}%"

# The total loss of Sales/Deferred Sales for all selected states
#total_count_overall= int(state_counts.get('Deferred Sales', 0))
#percentage_total = f"{sum(totals[state]['percentage'] for state in selected_status)}%"



# Plotting a Choropleth
url = 'https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson'
response = requests.get(url)
counties = response.json()

def create_choropleth(states_log, counties, selected_color_theme):
    # Check if there are no states selected or all selected states have zero incidents
    if states_log.empty or states_log['Amount'].sum() == 0:
        # Placeholder DataFrame: Display all states with zero incidents
        states_log = pd.DataFrame({
            'ship-state': [feature['properties']['NAME_1'] for feature in counties['features']],  # Use all states in the geojson
            'Amount': [0] * len(counties['features'])
        })

    # Determine the max incidents for setting the color range
    max_incidents = states_log['Amount'].max()

    # Avoid division by zero in color range calculation
    range_color = (0, max_incidents if max_incidents > 0 else 1)

    # Check if all incident counts are zero
    if states_log['Amount'].sum() == 0:
        # Create a base map with no highlights
        fig = px.choropleth_mapbox(
            states_log,
            geojson=counties,
            locations='ship-state',
            featureidkey="properties.NAME_1",
            color_discrete_sequence=['lightgrey'],  # Default color when no incidents
            mapbox_style="carto-positron",
            zoom=3.5,
            center={"lat": 20.5937, "lon": 78.9629},
            opacity=0.5,
            labels={'Amount': 'Total Sales (in dollars)'}
        )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig

    # Create the choropleth map with incident highlights
    fig = px.choropleth_mapbox(
        states_log,
        geojson=counties,
        locations='ship-state',
        featureidkey="properties.NAME_1",
        color='Amount',
        color_continuous_scale=color_theme_list[selected_color_theme],
        range_color=range_color,
        mapbox_style="carto-positron",
        zoom=3.5,
        center={"lat": 20.5937, "lon": 78.9629},  # Center on India
        opacity=0.5,
        labels={'Amount': 'Total Sales (in dollars)'}
    )
    #fig.update_geos(scope="asia")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig

choropleth = create_choropleth(states_log, counties, selected_color_theme)

## Main Page for the Board: 
col = st.columns((2,4,2), vertical_alignment="top")
colors = ['#3e6184','#2e4459' ,'#5d88b3', '#92afcc', '#d5e0ec']

with  col[0]:
    #print('Gomolemo Testing Working')
    st.write("#### Amazon Sales Indicators:")
    # CSS styling my St.Metric: 
    pmg_him = f"""
    <style>
    @media (prefers-color-scheme: light) {{
        [data-testid="stMetric"] {{
            border-radius: 5px;
            border: 2px solid #000;
            margin: 5px;  /* Reduce space between metrics */
            padding: 10px;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-start;
            height: 100px; /* Adjust height as needed */
            overflow: hidden; /* Ensure content does not overflow */
            }}
    }}
    
    @media (prefers-color-scheme: dark) {{
        [data-testid="stMetric"] {{
            border-radius: 10px;
            border: 2px solid #000;
            margin: 5px;  /* Reduce space between metrics */
            padding: 10px;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-start;
            height: 100px; /* Adjust height as needed */
            overflow: hidden; /* Ensure content does not overflow */
            }}
    }}
    [data-testid="stMetricText"] {{
        display: flex;
        flex-direction: column;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        width: 100%;
    }}
    [data-testid="stMetricIcon"] {{
        margin-right: 10px;
        flex-shrink: 0; /* Prevent icon from shrinking */
    }}
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"],
    [data-testid="stMetricLabel"] {{
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }}
    [data-testid="stMetricValue"]{{
        font-weight: bold;
        font-size: 1.5em;
    }}
    [data-testid="stMetricDelta"]{{
        font-weight: bold;
        font-size: 1.5em;
    }}
    [data-testid="stMetricLabel"] {{
        font-weight: bold;
        font-size: 1em; 
    }}
    </style>
    """
    st.markdown(pmg_him, unsafe_allow_html=True)
    
    #st.write("### Support Incidents KPIs:")
    with st.container():
        title_person = f'Top Sales Division: {max_user}'
        value_person = f'{str(max_incident_count)}'
        delta_person = f'% Contribution YTD:{str(percentage)}%'
        
        #group_with_max_incidents, group_max_incident_count, percentage_group = get_max_group(Product_groups, selected_status)
        #icon = svg_icon.replace('<svg', '<svg style="width: 40px; height: 40px;"')
        def metric_with_icon(label, value, delta, svg_icon):
            #Resize the SVG icon
            resized_icon = svg_icon.replace('<svg', '<svg style="width: 40px; height: 40px;"')
            html = f"""
            <div style="display: flex; align-items: center; border: 2px solid #000; padding: 10px; border-radius: 5px;">
            <div style="display: flex; align-items: center;">
                <div style="display: inline-block;">{resized_icon}</div>
                <div style="display: inline-block; margin-left: 8px;">
                    <div style="font-weight: bold;">{label}</div>
                    <div style="font-size: 2rem;">{value}</div>
                    <div style="color: {'green' if delta.startswith('+') else '#3e6184'};">{delta}</div>
                </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            
        #Top Service Group :
        title_group = f'Top Category Sales: {group_with_max_incidents}'
        value_group = f'{str(group_max_incident_count)}'
        delta_group = f'% Overall Sales Contribution YTD:{percentage_group}%'

        # Metrics:  
        Progress_id = f'Damaged'
        Resolved_id =  f'Delivered'
        Hold_id = f'Rejected'
        Cancelled_id = f'Cancelled'
        New_id = 'Lost'
        return_id = 'Returned-Seller'
        seller_id = 'In Transit - Seller'
        Workload_id = f'Deferred Sales'
        #svg_progress = encode_image(svg_progress_path)
        # Display Incident Summary Indicator: 
        #metric_with_icon(Progress_id, total_in_progress, percentage_in_progress, svg_progress)
        metric_with_icon(Resolved_id, f'{format_currency(total_resolved)}', percentage_resolved, svg_resolved)
        #metric_with_icon(Hold_id, total_on_hold ,percentage_on_hold, svg_hold)
        metric_with_icon(New_id,f'{format_currency(total_new)}' ,percentage_new, svg_new)
        metric_with_icon(return_id, f'{format_currency(total_on_returned)}',percentage_on_returned, svg_return)
        metric_with_icon(seller_id,f'{format_currency(total_on_seller)}',percentage_on_seller,svg_seller)
        #metric_with_icon(Cancelled_id, total_cancelled ,percentage_cancelled, svg_cancelled)
        #metric_with_icon(Workload_id, total_count_overall,percentage_total, svg_total)

        #Displing the user:  Which Business drove the most Sales in 2020 was it Amazon Inhouse or Externam Merchants:           
        metric_with_icon(title_person, f'{format_currency(value_person)}' ,delta_person,groups_icon)
        metric_with_icon(title_group, f'{format_currency(value_group)}',delta_group, svg_icon)


with col[1]:
    st.write("#### Amazon Sales Footprint by Indian States:")
    st.plotly_chart(choropleth, use_container_width=True)
    #st.write("#### Top Service Requests:")
    set_color_map = [
         '#5d88b3',  '#92afcc' ,'#5d88b3', '#2e4459','#6d93ba','#becfe0','#495766', '#1d2328','#8c96a0','#d8e3ec',
         '#005172','#003044', '#001822', '#4c859c', '#99b9c6','#4c859c' , '#99b2bc','#668b9a','#002748', '#193c5a', 
         '#32526c', '#4c677e', '#667d91', '#7f93a3','#99a8b5', '#b2bec8', '#2d2a27', '#5a544e','#cac5c1','#f4f3f2',
         '#005475', '#008cc4', '#006289', '#005475', '#5d88b3','#537AA1','#4A6C8F','#415F7D','#7D9FC2','#8DABC9',
         '#9DB7D1','#ADC3D8','#BECFE0', '#37516B','#2E4459','#253647','#1B2835', '#6C7C8A', '#818E9B','#96A1AB',
         '#ABB4BC'
    ]
    
    # Ensure the number of colors matches the unique values in `ship-state`
    unique_states = states_log['ship-state'].unique()
    color_map_dict = {state: set_color_map[i % len(set_color_map)] for i, state in enumerate(unique_states)}

    color_map = list(set_color_map)
    states_log = states_log.sort_values(by='Amount', ascending=False)
    fig = px.bar(
        states_log,
        x='ship-state',
        y='Amount',
        color='ship-state',
        color_discrete_map= color_map_dict,
        barmode='group',
        title='Total Sales by Indian State in Rupees',
        labels={'Amount': 'Total Sales', 'Ship State': 'State'}
    )
    #fig.update_layout(width=500,height=550)
    st.plotly_chart(fig, use_container_width=True)

with col[2]:
    # Function to create a progress bar in HTML
    def get_progress_bar_html(value, max_value=None, color='#3e6184'):
        if max_value is None:
            max_value = max(sub_categories_sorted['Amount'])
        percentage = (value / max_value) * 100
        formatted_value = format_currency(value) 
        return f"""
        <div style="background-color: #f3f3f3; border-radius: 5px; width: 100%; height: 20px; margin: 5px 0;">
                <div style="background-color: {color}; width: {percentage}%; height: 100%; border-radius: 5px;"></div>
        </div>
        <div style="text-align: right; font-weight: bold;">{formatted_value}</div>  <!-- Display the count value -->
        """
    
    # Function to create HTML representation of the DataFrame
    def create_html_table(df):
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<thead><tr><th style="padding: 8px; text-align: left;">Products</th><th style="padding: 8px; text-align: left;">Amount</th></tr></thead>'
        html += '<tbody>'
        for _, row in df.iterrows():
            html += f'<tr><td style="padding: 8px; border: 1px solid #ddd;">{row["Category"]}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #ddd;">{get_progress_bar_html(row["Amount"])}</td></tr>'
        html += '</tbody></table>'
        return html
        
    html_table = create_html_table(sub_categories_sorted)
    #st.markdown(create_html_table(sub_categories_sorted), unsafe_allow_html=True)
    
    st.markdown(
        """
        <style>
        .scrollable-table {
            max-height: 700px; /* Adjust height as needed */
            overflow-y: auto;
            overflow-x: hidden;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        </style>
        <div class="scrollable-table">
        """ + html_table + """
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # About the Board Type of Information: 
    with st.expander("Dashboard Overview: ", expanded=True):
        st.write('''
            - **Data Source**: Kaggle Hub: Amazon India's Sales Report for the period March, April, May, & June 2022.
            - **Summary**: Most Commercial Sales were made from Amazon retail stores and not external merchants. Accounting for 69 percent overall sales for the period (in dollars). 
            - Overall most sold product in the period were T-Shirts and their most profitable state is 
            ''')
