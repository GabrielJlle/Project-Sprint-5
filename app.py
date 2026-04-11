import pandas as pd
import plotly.express as px
import folium as fl
import json
import streamlit as st
import streamlit_folium as stf

#Average Meal Price Chart
restaurants_data['average_meal'] = restaurants_data['price'].apply(lambda x: x['avg_meal_eur']) #filtering the column

fig1 = px.histogram(restaurants_data, title="Average price", x='average_meal', labels={'average_meal':'Meal: Average Price', 'count':'Count'}) #setting the chart
fig1.show() #ploting the chart

#Min and Max rating chart
restaurants_data['rating_min'] = restaurants_data['rating'].apply(lambda x: x['min']) #filtering minimum rating
restaurants_data['rating_max'] = restaurants_data['rating'].apply(lambda x: x['max']) #filtering maximum rating
restaurants_gp = restaurants_data.groupby(['rating_max', 'rating_min']).agg({'name': lambda x: '<br>'.join(x), 'rating_min': 'first', 'rating_max': 'first'}).reset_index(drop=True)


fig2 = px.scatter(restaurants_gp, title='Rating Max/Min', x='rating_min', y='rating_max', opacity=0.7, hover_name='name', labels={'rating_min':'Minimum rating', 'rating_max':'Maximum rating'}) #setting scatter chart
fig2.show() #plotting the chart

#cuisine and price chart
def price_cuisine(df): #function to filter the range from 'price' and split the types of cuisine of restaurants that has more than one type
    df_copy = df.copy() #creates a copy of the dataset
    df_copy['price_range'] = df_copy['price'].apply(lambda x: x['range']) #filters just the range from the column 'price'

    expanded_rows = [] #creating an empty list
    for index, row in df_copy.iterrows(): #iterates the dataset to split the type of cuisines
        if row['cuisine'] and len(row['cuisine']) > 1: #filters just when the cuisines has more than one type 
            for cuisine_type in row['cuisine']: #iterates on the filter
                new_row = row.copy() #copies the row
                new_row['cuisine'] = cuisine_type #adds the iterated cuisine type to the copied row 
                expanded_rows.append(new_row) #adds the rows into the empty list
    return pd.DataFrame(expanded_rows) #turning the list into a Data Frame
    
fig3 = px.bar(price_cuisine(restaurants_data), title='Relation Price Average x Cuisine', x='price_range', color='cuisine', hover_name='name', labels={'price_range':'Price range', 'count':'Count'}, category_orders={'price_range': ['€', '€€', '€€€', '€€€€']}) #creates a bar chart
fig3.show() #plotting the chart

#map
m = fl.Map(location=(51.8985, -8.4756), zoom_start=11, tiles='CartoDB positron') #setting the map to Cork City centre

for index, row in restaurants_data.iterrows(): #loop to add each restaurant as a marker in the map
    cords_dic = row['coordinates'] #filtering the row
    cords_list = [cords_dic['lat'],cords_dic['lng']] #filtering lat and lng
    fl.Marker(cords_list, popup=row['name'], tooltip='Click for info', icon=fl.Icon(icon='cutlery'), prefix='fa').add_to(m) #adding markers to the restaurants

display(m) #displaying the map