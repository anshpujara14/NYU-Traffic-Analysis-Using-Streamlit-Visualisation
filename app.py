## Importing libraries
import pandas as pd
import streamlit as st
import numpy as np
import pydeck as pdk
#import matplotlib.pyplot as plt
import plotly.express as px

data_url = '/home/ansh/Desktop/Streamlit_Project/Motor_Vehicle_Collisions_-_Crashes(1).csv'

st.title('MV Collisions in NYC')
st.markdown('Streamlit app to analyze mv collisions in NYC')

## Loading Data
@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(data_url, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data.copy()

## Plotting the area where number of collisions equals the value of slider
st.header('Where are the most people injured in NYC?')
injured_people = st.slider('Number of people injured in vehicle collision' , 0, 19) ## Makes a slider
st.map(data.query('injured_persons >= @injured_people')[['latitude', 'longitude']].dropna(how='any')) ## Plots a map with [['latitude', 'longitude']]

## Filtering Data to see number of collisions at a particular time
st.header('How many collisions occured during a given time of day?')
hour = st.slider('Hour to look at', 0, 23) ## Slider to select the time
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle colllisions between %i:00 and %i:00" % (hour, (hour+1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style = 'mapbox://styles/mapbox/light-v9',
    initial_view_state={
        'latitude': midpoint[0],
        'longitude': midpoint[1],
        'zoom': 11,
        'pitch': 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data = data[['date/time', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 100, ## Radius of idividual point
        extruded=True, ## Makes the map 3D
        pickable=True,
        elevation_scale = 4,
        elevation_range = [0,1000],
        ),
    ]
))

st.subheader("Breakdown by minute between %i:00 and %i:00 " % (hour, (hour+1) % 24))

## Creating a dataframe 'filtered' by filtering the hours selected
filtered = data[(data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))]

##Plot the interactive bar chart plotly.express and the data frame 'filtered'
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

## Create a drop box to select particular data points
st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[['on_street_name', 'injured_pedestrians']].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[['on_street_name', 'injured_cyclists']].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])

else :
    st.write(original_data.query("injured_motorists >= 1")[['on_street_name', 'injured_motorists']].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])




if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
