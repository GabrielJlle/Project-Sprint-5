# importing all libraries, modules, packages
import pandas as pd
import plotly.express as px
import folium as fl
import streamlit as st
from streamlit_folium import st_folium

# data reading (using pd to read because later is going to be easier to use filters in the dataset)
restaurants_data = pd.read_json('restaurants.json')

st.header('Data viewer: Cork City Restaurants')
df_flat = pd.json_normalize(restaurants_data.to_dict(orient='records'))
df_flat = df_flat.rename(columns={'rating.average': 'average rating', 'price.range': 'price range',
                         'price.avg_meal_eur': 'meal average price €', 'opening_hours': 'opening hours'})
st.dataframe(df_flat, width=700, height=425,
             column_config={'coordinates.lat': None, 'coordinates.lng': None, 'rating.max': None, 'rating.min': None})

# Average Meal Price Chart
st.header('Histogram x Scatter chart')
hist_button = st.checkbox('Plot a histogram')
scat_button = st.checkbox('Plot a scatter chart')

if hist_button:
    st.write(
        "Plotting a histogram for the average price of a meal of restaurants in Cork")
    restaurants_data['average_meal'] = restaurants_data['price'].apply(
        lambda x: x['avg_meal_eur'])  # filtering the column

    fig1 = px.histogram(restaurants_data, x='average_meal', labels={
        'average_meal': 'Meal: Average Price', 'count': 'Count'})  # setting the chart
    st.plotly_chart(fig1, use_container_width=True)  # ploting the chart

# Min and Max rating chart
if scat_button:
    st.write(
        "Plotting a scatter chart for the maximum and mininum rates of restaurants in Cork")
    restaurants_data['rating_min'] = restaurants_data['rating'].apply(
        lambda x: x['min'])  # filtering minimum rating
    restaurants_data['rating_max'] = restaurants_data['rating'].apply(
        lambda x: x['max'])  # filtering maximum rating
    restaurants_gp = restaurants_data.groupby(['rating_max', 'rating_min']).agg(
        {'name': lambda x: '<br>'.join(x), 'rating_min': 'first', 'rating_max': 'first'}).reset_index(drop=True)

    fig2 = px.scatter(restaurants_gp, x='rating_min', y='rating_max', opacity=0.7, hover_name='name',
                      labels={'rating_min': 'Minimum rating', 'rating_max': 'Maximum rating'})  # setting scatter chart
    st.plotly_chart(fig2, use_container_width=True)  # plotting the chart

# cuisine and price chart
st.header('Relation Price Average x Cuisine')


def price_cuisine(df):  # function to filter the range from 'price' and split the types of cuisine of restaurants that has more than one type
    df_copy = df.copy()  # creates a copy of the dataset
    # filters just the range from the column 'price'
    df_copy['price_range'] = df_copy['price'].apply(lambda x: x['range'])

    expanded_rows = []  # creating an empty list
    for index, row in df_copy.iterrows():  # iterates the dataset to split the type of cuisines
        # filters just when the cuisines has more than one type
        if row['cuisine'] and len(row['cuisine']) > 1:
            for cuisine_type in row['cuisine']:  # iterates on the filter
                new_row = row.copy()  # copies the row
                # adds the iterated cuisine type to the copied row
                new_row['cuisine'] = cuisine_type
                # adds the rows into the empty list
                expanded_rows.append(new_row)
    return pd.DataFrame(expanded_rows)  # turning the list into a Data Frame


# To scroll down all the cuisine options it's necessary to first unmark all the options shown in the chart sidebar
fig3 = px.bar(price_cuisine(restaurants_data), x='price_range', color='cuisine', hover_name='name', labels={
              'price_range': 'Price range', 'count': 'Count'}, category_orders={'price_range': ['€', '€€', '€€€', '€€€€']})  # creates a bar chart
st.plotly_chart(fig3, use_container_width=True)  # plotting the chart

# map
st.header("Map")
#######
m = fl.Map(location=(51.8985, -8.4756), zoom_start=11,
           tiles='CartoDB positron')  # setting the map to Cork City centre

filtered_data = restaurants_data  # setting a different dataset to be filtered
func_data = price_cuisine(filtered_data)  # applying a function

# setting an extra option in the selection box
names = ["All"] + list(filtered_data['name'].unique())
# setting an extra option in the selection box
cuisine = ["All"] + list(func_data['cuisine'].unique())
# setting an extra option in the selection box
price = ["All"] + list(func_data['price_range'].unique())

name_filter = st.selectbox(
    label="Name", options=names)  # selection which filters the name

cuisine_filter = st.selectbox(
    label="Cuisine", options=cuisine)  # selection which filters the cuisine

price_range_filter = st.selectbox(
    label="Price Range", options=price)  # selection which filters the price range

if name_filter != "All":
    # setting the right selection when the user chooses an option
    filtered_data = filtered_data[filtered_data['name'] == name_filter]

if cuisine_filter != "All":
    # setting the right selection when the user chooses an option
    filtered_data = func_data[func_data['cuisine'] == cuisine_filter]

if price_range_filter != "All":
    filtered_data = func_data[func_data['price_range']
                              == price_range_filter]  # setting the right selection when the user chooses an option

# st.write(restaurants_data.columns)

for index, row in filtered_data.iterrows():  # loop to add each restaurant as a marker in the map
    cords_dic = row['coordinates']  # filtering the row
    # filtering lat and lng
    cords_list = [cords_dic['lat'], cords_dic['lng']]
    fl.Marker(cords_list, popup=row['name'], tooltip='Click for info', icon=fl.Icon(
        icon='cutlery'), prefix='fa').add_to(m)  # adding markers to the restaurants

st_data = st_folium(m, width=700, height=450)  # displaying the map
