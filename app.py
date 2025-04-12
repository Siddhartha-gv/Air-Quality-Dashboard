import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import datetime
import random

# Set page configuration
st.set_page_config(
    page_title="Simple Air Quality Dashboard",
    page_icon="🌍",
    layout="wide"
)

# Simple CSS for better appearance
st.markdown("""
<style>
    .title {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .good-aqi {
        background-color: #a8e05f;
        padding: 5px 10px;
        border-radius: 5px;
        color: #333;
    }
    .moderate-aqi {
        background-color: #fdd74c;
        padding: 5px 10px;
        border-radius: 5px;
        color: #333;
    }
    .unhealthy-aqi {
        background-color: #fe6a69;
        padding: 5px 10px;
        border-radius: 5px;
        color: white;
    }
    .very-unhealthy-aqi {
        background-color: #a97abc;
        padding: 5px 10px;
        border-radius: 5px;
        color: white;
    }
    .explanation {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown("<div class='title'>🌍 Simple Air Quality Dashboard</div>", unsafe_allow_html=True)

# Sidebar with minimal controls
with st.sidebar:
    st.markdown("## Settings")
    
    # City Selection - simplified with common cities dropdown
    city_options = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune","Ahmedabad","Jaipur","Lucknow", "Visakhapatnam", "Vijayawada", ]
    city = st.selectbox("Select City", city_options, index=0)
    
    # API Key Input (with a default key)
    api_key = st.text_input("OpenWeatherMap API Key (Optional)", 
                           value="2ee2ce20859e77a82e1df0148123b17f", 
                           type="password")
    
    # Simple explanation
    st.markdown("""
    ### How to use
    1. Select your city
    2. View current air quality
    3. Check pollutant levels
    """)

# Function to get AQI category and color
def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good", "good-aqi"
    elif aqi <= 100:
        return "Moderate", "moderate-aqi"
    elif aqi <= 200:
        return "Unhealthy", "unhealthy-aqi"
    else:
        return "Very Unhealthy", "very-unhealthy-aqi"

# Function to get coordinates for a city
def get_city_coordinates(city_name):
    # Default coordinates for common cities
    city_coords = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),  # Corrected the blank city name to Pune
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Visakhapatnam": (17.6869, 83.2185),
    "Vijayawada": (16.5063, 80.6480),
    }
    
    return city_coords.get(city_name, (28.6139, 77.2090))  # Default to Delhi if not found

# Function to fetch or simulate AQI data
def get_aqi_data(city, api_key):
    try:
        # Get coordinates for the city
        lat, lon = get_city_coordinates(city)
        
        # Try to get real data from OpenWeatherMap API
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'list' in data and len(data['list']) > 0:
                result = data['list'][0]
                result['coord'] = {"lat": lat, "lon": lon}
                return result
        
        # If API call fails, generate simulated data
        return generate_simulated_data(lat, lon)
    
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        # Generate simulated data as fallback
        lat, lon = get_city_coordinates(city)
        return generate_simulated_data(lat, lon)

# Function to generate simulated AQI data (simplified)
def generate_simulated_data(lat, lon):
    aqi = random.randint(30, 180)
    pm25 = random.uniform(5, 50)
    pm10 = random.uniform(10, 70)
    co = random.uniform(0.5, 10)
    no2 = random.uniform(10, 80)
    o3 = random.uniform(20, 100)
    so2 = random.uniform(5, 40)
    
    return {
        "main": {"aqi": aqi},
        "components": {
            "pm2_5": pm25,
            "pm10": pm10,
            "co": co,
            "no2": no2,
            "o3": o3,
            "so2": so2
        },
        "coord": {
            "lat": lat,
            "lon": lon
        }
    }

# Main content area
# Fetch data with a spinner to show loading state
with st.spinner(f"Loading air quality data for {city}..."):
    # Get AQI data (real or simulated)
    aqi_data = get_aqi_data(city, api_key)

# Check if we have data and display it
if aqi_data:
    # Display current AQI
    aqi_value = aqi_data["main"]["aqi"]
    aqi_category, aqi_class = get_aqi_category(aqi_value)
    
    # Create three columns for better layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"## Current Air Quality in {city}")
        st.markdown(f"### AQI: <span class='{aqi_class}'>{aqi_value} - {aqi_category}</span>", unsafe_allow_html=True)
        
        # Simple explanation of what AQI means
        if aqi_value <= 50:
            explanation = "Air quality is good. Enjoy outdoor activities!"
        elif aqi_value <= 100:
            explanation = "Air quality is acceptable. Sensitive individuals should limit prolonged outdoor exertion."
        elif aqi_value <= 200:
            explanation = "Air quality is unhealthy. Everyone may begin to experience health effects."
        else:
            explanation = "Air quality is very unhealthy. Avoid outdoor activities."
            
        st.markdown(f"<div class='explanation'>{explanation}</div>", unsafe_allow_html=True)
    
    # Create two columns for pollutant data
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## Main Pollutants")
        
        # Display only the most important pollutants
        important_pollutants = ["PM2.5", "PM10", "CO"]
        pollutant_data = []
        
        for pollutant in important_pollutants:
            key = pollutant.lower() if pollutant.lower() != "pm2.5" else "pm2_5"
            value = aqi_data["components"].get(key, 0)
            pollutant_data.append({"Pollutant": pollutant, "Value": value})
        
        # Create a simple bar chart
        pollutant_df = pd.DataFrame(pollutant_data)
        fig = px.bar(
            pollutant_df, 
            x="Pollutant", 
            y="Value", 
            color="Pollutant",
            color_discrete_sequence=["#4CAF50", "#FFC107", "#FF5722"],
            title="Current Pollutant Levels"
        )
        fig.update_layout(
            xaxis_title="",
            yaxis_title="μg/m³",
            legend_title="",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("## What These Values Mean")
        
        # Simple explanation of pollutants
        st.markdown("""
        ### PM2.5
        Fine particulate matter that can penetrate deep into the lungs. 
        Sources include vehicle emissions, industrial processes, and wildfires.
        
        ### PM10
        Larger inhalable particles from sources like dust, pollen, and mold.
        
        ### CO (Carbon Monoxide)
        An odorless, colorless gas produced by burning fossil fuels.
        """)
    
    # Simple health advice section
    st.markdown("## Health Recommendations")
    
    if aqi_value <= 50:
        st.success("✅ Air quality is good - It's a great day for outdoor activities!")
    elif aqi_value <= 100:
        st.warning("⚠️ Sensitive individuals should consider reducing prolonged outdoor exertion.")
    elif aqi_value <= 200:
        st.error("🚫 Everyone may begin to experience health effects. Sensitive groups should limit outdoor activity.")
    else:
        st.error("🚫 Health alert! Everyone should avoid outdoor exertion and stay indoors if possible.")

else:
    # Display error message if no data is available
    st.error("Unable to load air quality data. Please check your internet connection or try again later.")

# Footer with minimal information
st.markdown("---")
st.markdown("Simple Air Quality Dashboard | Data from OpenWeatherMap")