import requests
import folium
import sys

BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "5b0d498b57a2899ac882b7f6b8544290"
temp_data=[]

def get_weather_data(city):
    url = f"{BASE_URL}q={city}&appid={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        temp_data.append(data)
        

        main = data['main']
        coord = data['coord']
        wind = data['wind']
        temperature = main['temp'] - 273.15
        humidity = main['humidity']
        pressure = main['pressure']
        wind_speed = wind['speed']
        report = data['weather']
        lon = coord['lon']
        lat = coord['lat']
        
        print(f"{city:-^30}")
        print(f"Temperature: {round(temperature, 2)}°C")
        print(f"Humidity: {humidity}%")
        print(f"Pressure: {pressure} hPa")
        print(f"Wind Speed: {wind_speed} m/s")
        print(f"Longitude and Latitude: {lon}, {lat}")
        print(f"Weather: {report[0]['main']}")
        print(f"Weather Description: {report[0]['description']}")
        
        return lat, lon
    else:
        print("Error in the HTTP request")
        return None, None

def main(city):
    print(city)
    #city = input("Enter City: ")
    city=city
    lat, lon = get_weather_data(city)
    
    if lat is not None and lon is not None:
        map = folium.Map(location=[lat, lon], zoom_start=8)
        
        folium.CircleMarker(    
            location=[lat, lon],
            radius=30,
            popup=city,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc",
        ).add_to(map)
        
        map.save("weather_map.html")
        print("Map saved as weather_map.html")
    return temp_data

#if __name__ == "__main__":
    #main()
