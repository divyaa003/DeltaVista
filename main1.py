from flask import Flask, render_template, request, redirect, url_for
from tensorflow.keras.preprocessing import image
from keras.models import load_model
import matplotlib.pyplot as plt
import numpy as np
import os
import mysql.connector
import folium
import requests
import map

mydb = mysql.connector.connect(host="localhost", user="root", password="", database="delta")
mycursor = mydb.cursor()

UPLOAD_FOLDER = 'static/file/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "5b0d498b57a2899ac882b7f6b8544290"
temp_data=[]

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/loginpost', methods=['POST', 'GET'])
def userloginpost():
    global data1
    if request.method == 'POST':
        data1 = request.form.get('uname')
        data2 = request.form.get('password')
        
        print("Username:", data1)  # Debug statement
        print("Password:", data2)  # Debug statement

        if data2 is None:
            return render_template('login.html', msg='Password not provided')

        sql = "SELECT * FROM `users` WHERE `uname` = %s AND `password` = %s"
        val = (data1, data2)

        try:
            mycursor.execute(sql, val)
            account = mycursor.fetchone()  # Fetch one row

            if account:
                # Consume remaining results
                mycursor.fetchall()
                mydb.commit()
                return render_template('index1.html')
            else:
                return render_template('login.html', msg='Invalid username or password')
        except mysql.connector.Error as err:
            print("Error:", err)  # Debug statement
            return render_template('login.html', msg='An error occurred. Please try again.')

@app.route('/NewUser')
def newuser():
    return render_template('NewUser2.html')

@app.route('/reg', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        uname = request.form.get('uname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        password = request.form.get('psw')
        gender = request.form.get('gender')
        sql = "INSERT INTO users (name, uname, email , phone, age, password, gender) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (name, uname, email, phone, age, password, gender)
        mycursor.execute(sql, val)
        mydb.commit()
        return render_template('login.html')
    else:
        return render_template('NewUser2.html')

@app.route('/index1')
def index1():
    return render_template('index.html')

@app.route('/index2')
def index2():
    return render_template('index2.html')

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
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        classes=['fish market','flower','ganapathi vilas scl','kaasi vishwanathar temple','kalki park']
        # classes = ['bio fertility' , 'CSI Church','elephant','finlay scl','fish market','flower','ganapathi vilas scl','haridra nadhi','kaasi vishwanathar temple',' kalki park','katalai muttai','maiden colony','mannai narayanaswamy nagar','municipality','national scl','national scl ground','oil mill','old housing unit','pamani river','puthur','quaters','railway station','rajagopalaswamy temple','rukkumani kulam','saviour scl','Selliyamman Temple','silk','taluk office','thamarai kulam','vaithiya salai','vannan kuzham','veannai thali thiruvila','vennai thali mandapam','water tank'
        #            'Hostel','Finally Ground','Airavatheeswarar Temple Kumbakonam','Ayi Kulam Kumbakonam',' Ezhutharinathar Temple Innambur','Garuda sevai kumbakonam','Government Men College kumbakonam','government women college kumbakonam','Handloom Silk making kumbakonam','Krishna school fire accident kumbakonam','Kumbeshwarar Temple kumbakonam','Mahamaha kulam kumbakonam','MGR school kumbakonam','Nageshwarar Temple kumbakona','Navagraha Temple','Potramarai kulam Kumbakonam','Ramaswamy Temple Kumbakonam','sri vedanarayana perumal temple kumbakonam','Srinivasa Ramanujam House']
        desc={'fish market':'The Mannargudi fish market is located in Mannargudi, a town in the Thiruvarur district of Tamil Nadu, India. Mannargudi is known for its vibrant fish market, where a variety of fresh seafood is bought and sold daily. Fishermen bring in their catches from the nearby coastal areas, offering a wide range of fish, prawns, crabs, and other seafood to both locals and visitors',
              'flower':'Mannargudi is also renowned for its flower market, which is a significant hub for the trade of flowers in the region. The town is particularly famous for its production of jasmine flowers, which are highly prized for their fragrance and aesthetic appeal. The Mannargudi flower market sees a bustling activity, especially in the early morning hours when fresh blooms arrive from nearby flower farms and gardens.',
              'ganapathi vilas scl':' In Mannargudi, "Ganapathi Vilas" is a well-known vegetarian restaurant that serves South Indian cuisine. "SCL" could potentially stand for "South Indian Cuisine Lovers" or something similar, indicating a group or community related to South Indian food appreciation. Ganapathi Vilas is popular for its traditional Tamil Nadu dishes, including dosas, idlis, vadas, sambar, and various rice-based dishes like biryani and pongal.',
              'kaasi vishwanathar temple':'The Kaasi Viswanathar Temple is a renowned Hindu temple located in Mannargudi, Tamil Nadu, India. Dedicated to Lord Shiva, this temple is one of the oldest and most significant religious landmarks in the region. The temple is also known as the Mannargudi Rajagopalaswamy Temple, as it is home to deities of both Lord Shiva and Lord Vishnu.',
              'kalki park':'"Kalki Park" in Mannargudi, Tamil Nadu. However, it s possible that developments or new establishments have emerged since then. If "Kalki Park" is a recent addition, it might be a recreational area, park, or any other facility named after Kalki Krishnamurthy, the renowned Tamil writer and novelist. To get more accurate information about Kalki Park in Mannargudi, I suggest checking local directories, tourism websites, or contacting local authorities or residents in Mannargudi for the most up-to-date details.'}
        file1 = request.files['filename']
        imgfile = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(imgfile), exist_ok=True)
        
        file1.save(imgfile)
        #model = load_model('model.h5')
        model = load_model('keras_model.h5')
        # Load the labels
        # classes = open("labels.txt", "r").readlines()
        img_ = image.load_img(imgfile, target_size=(224, 224, 3))
        img_array = image.img_to_array(img_)
        img_processed = np.expand_dims(img_array, axis=0)
        img_processed /= 255.
        prediction = model.predict(img_processed)
        index = np.argmax(prediction)
        result = "Unknown"
        percentage = 0.0
        value="description not availble"

        if index < len(classes):
            result = str(classes[index]).title()
            value=desc.get(result.lower())
           
        image_url = url_for('static', filename='file/' + file1.filename)
        city="mannargudi"
        url = f"{BASE_URL}q={city}&appid={API_KEY}"
        response = requests.get(url)
    
        if response.status_code == 200:
            data = response.json()
            temp_data.append(data)
            temp_data1=f"{city:-^30}"+"\n"+f"Temperature: {round( data['main']['temp'] - 273.15, 2)}°C"+"\n"+f"Humidity: {data['main']['humidity']}%"+"\n"+f"Pressure: {data['main']['pressure']} hPa"+"\n"+f"Wind Speed: {data['wind']['speed']} m/s"+"\n"+f"Longitude and Latitude: {data['coord']['lon']}, {data['coord']['lat']}"+"\n"+f"Weather: {data['weather'][0]['main']}"+"\n"+f"Weather Description: {data['weather'][0]['description']}"
        print("map_res",temp_data1)

        return render_template('prediction_result1.html', msg=result,data=temp_data1 ,desc_msg =value, src=imgfile, view='style=display:block', view1='style=display:none')
    elif request.method == 'GET':
        return render_template('index.html')

@app.route('/prediction_result')
def prediction_result():
    result = request.args.get('result')
    image_url = request.args.get('image_url')
    
    # Assume 'result' contains the city name for which you want to display the weather map
    city = result
    
    # Generate weather map
    weather_map_path = generate_weather_map(city)
    
    if weather_map_path:
        # If weather map is generated successfully, render the template with both prediction result and weather map
        return render_template('prediction_result1.html', result=result, image_url=image_url, weather_map_path=weather_map_path)
    else:
        # If weather data is not available for the city, render the template with only prediction result
        return render_template('prediction_result1.html', result=result, image_url=image_url)

@app.route('/upload2', methods=['POST', 'GET'])
def upload2():
    if request.method == 'POST':
        classes = ['Airavatheeswarar Temple Kumbakonam', 'Ayi Kulam Kumbakonam', 'Ezhutharinathar Temple Innambur', 'Garuda sevai kumbakonam', 'Government Men s College kumbakonam', 'Government women s college kumbakonam', 'Handloom Silk making kumbakonam', 'Krishna school fire accident kumbakonam', 'Mahamaha kulam kumbakonam', 'Mgr school kumbakonam', 'Nageshwarar Temple kumbakonam', 'Potramarai kulam Kumbakonam', 'Ramaswamy Temple Kumbakonam', 'Srinivasa Ramanujam House']
        desc = {'Airavatheeswarar Temple Kumbakonam': 'The Airavatesvara Temple is indeed a notable Hindu temple located in the town of Darasuram near Kumbakonam in the South Indian state of Tamil Nadu. It s dedicated to Lord Shiva and is a UNESCO World Heritage Site, part of the Great Living Chola Temples. The temple is renowned for its architectural brilliance, intricate carvings, and rich cultural significance.Constructed by Rajaraja Chola II in the 12th century, the temple is a splendid example of Dravidian architecture. Its name is derived from the term "Airavata," which refers to the white elephant mount of Indra, the king of the gods in Hindu mythology.',
                'Ayi Kulam Kumbakonam': 'Ayi Kulam is a famous temple tank located in Kumbakonam, a town in the Indian state of Tamil Nadu. The tank is an integral part of the Sarangapani Temple complex, one of the prominent temples in Kumbakonam dedicated to the Hindu god Vishnu.The term Ayi Kulam translates to Mirror Pond in English. It is a large rectangular tank with steps leading down to the water, providing a place for devotees to take ritual baths before entering the temple. These temple tanks are not only significant for their religious importance but also serve as gathering places for festivals and ceremonies.Kumbakonam is renowned for its numerous temples and temple tanks, and Ayi Kulam is among the most visited ones due to its historical significance and architectural beauty.',
                'Ezhutharinathar Temple Innambur':'The Ezhutharinathar Temple is located in Innambur, a village in the Kumbakonam Taluk of Tamil Nadu, India. The temple is dedicated to Lord Shiva and is believed to be around 1,000 years old, reflecting the rich cultural and religious heritage of the region.The presiding deity of the temple is Lord Ezhutharinathar, a form of Lord Shiva. The name Ezhutharinathar translates to Lord of Writing or Lord of Letters, indicating the significance of education and knowledge associated with this deity.The temple architecture is typically South Indian, with intricate carvings and sculptures adorning its walls and pillars. Devotees visit the temple to seek blessings for education, knowledge, and wisdom.Innambur itself is a small village surrounded by agricultural fields, offering a peaceful ambiance to visitors. The Ezhutharinathar Temple stands as a symbol of spiritual and cultural heritage in the region, attracting devotees and tourists.',
                'Garuda Sevai Kumbakonam':'Garuda Sevai is a revered festival celebrated at various temples in Kumbakonam, Tamil Nadu, during the Tamil month of Vaikasi (May-June). Dedicated to Lord Vishnu and his mount Garuda, the festival entails the procession of Lord Vishnu s idol mounted on a majestic Garuda vahana, symbolizing the divine bond between the two. Adorned with intricate decorations, the Garuda vahana carries the deity through the streets, accompanied by enthusiastic chanting, hymns, and rituals performed by devotees. The festival holds deep significance in Hindu tradition, serving as a time for devotees to express their devotion and seek blessings while commemorating the glory of Lord Vishnu and his divine vehicle.',
                'Government Men S College Kumbakonam':'The Government Men s College in Kumbakonam, Tamil Nadu, stands as a beacon of higher education in the region, providing opportunities for academic excellence and personal growth to young men aspiring for a brighter future. Established with a commitment to impart quality education, the college offers a diverse range of undergraduate and postgraduate programs across various disciplines, fostering a conducive learning environment supported by experienced faculty and modern facilities. With its rich history and esteemed reputation, the Government Men s College plays a pivotal role in shaping the intellectual and professional landscape of Kumbakonam and nurturing the leaders of tomorrow.',
                'Government Women S College Kumbakonam':'The Government Women s College in Kumbakonam, Tamil Nadu, stands as a cornerstone of women s education in the region, dedicated to empowering and uplifting young women through quality higher education. Established with a vision of fostering academic excellence and holistic development, the college offers a wide array of undergraduate and postgraduate programs across various disciplines, catering to the diverse interests and aspirations of its students. With a focus on providing a nurturing and inclusive learning environment, the college boasts experienced faculty, state-of-the-art facilities, and a vibrant campus culture that encourages intellectual curiosity, leadership, and social responsibility. Committed to promoting gender equality and women s empowerment, the Government Women s College in Kumbakonam plays a pivotal role in shaping the future of its students and contributing to the socio-economic progress of the community.',
                'Handloom Silk Making Kumbakonam':'Kumbakonam, renowned for its cultural heritage and traditional crafts, has a significant presence in the handloom silk industry. The process of handloom silk making in Kumbakonam involves skilled artisans who meticulously weave silk threads into exquisite fabrics using traditional techniques passed down through generations. The region is particularly known for its production of silk sarees, known for their intricate designs, vibrant colors, and superior quality. Artisans in Kumbakonam often draw inspiration from local motifs, historical themes, and religious symbolism, infusing each saree with cultural significance and artistic beauty. Handloom silk making not only sustains livelihoods but also preserves age-old craftsmanship and contributes to the rich tapestry of India s textile heritage. Visitors to Kumbakonam often seek out these handloom silk products as prized souvenirs, appreciating the craftsmanship and cultural significance behind each piece.',
                'Krishna School Fire Accident Kumbakonam':'The Krishna English Medium School fire accident in Kumbakonam, which occurred on July 16, 2004, stands as one of the most tragic incidents in Indian history. The fire broke out in a thatched roof classroom of the primary section, quickly spreading due to the combustible materials used in the construction. The lack of proper fire safety measures, including emergency exits and fire extinguishing equipment, exacerbated the situation. Tragically, 94 children lost their lives in the fire, while many others sustained severe injuries. The incident sparked widespread outrage and led to calls for stricter enforcement of safety regulations in schools across the country. It also prompted significant changes in fire safety standards and regulations, highlighting the critical importance of ensuring the safety of educational institutions and the well-being of students.',
                'Mahamaha Kulam Kumbakonam':'Mahamaha Kulam, also known as Mahamaham Tank, stands as a revered site in Kumbakonam, Tamil Nadu, deeply entrenched in Hindu religious traditions. This expansive temple tank, believed to be around 2,000 years old, holds immense spiritual significance, particularly during the Mahamaham festival, celebrated once every 12 years. During this auspicious event, millions of devotees converge to take a ritual bath in the sacred waters of Mahamaha Kulam, seeking spiritual purification and the blessings of the divine. Surrounded by small temples dedicated to various deities, the tank serves as a focal point of religious devotion and cultural heritage, embodying the essence of Kumbakonam s rich religious legacy.',
                'Mgr School Kumbakonam':'The MGR School in Kumbakonam, named after the renowned Tamil actor and former Chief Minister of Tamil Nadu, M.G. Ramachandran, stands as a symbol of educational excellence and community development in the region. With a commitment to providing quality education to its students, the school offers a diverse range of academic programs and extracurricular activities, fostering holistic development and nurturing future leaders. The schools ethos is rooted in M.G. Ramachandrans vision of empowerment through education, aiming to instill values of integrity, discipline, and social responsibility in its students. Through its dedicated faculty, modern facilities, and innovative teaching methods, the MGR School plays a pivotal role in shaping the intellectual and moral fabric of Kumbakonam, empowering generations to achieve their fullest potential and contribute positively to society.',
                'Nageshwarar Temple Kumbakonam':'The Nageshwara Temple is a revered Hindu temple located in Kumbakonam, Tamil Nadu, dedicated to Lord Shiva. This ancient temple is renowned for its architectural grandeur and religious significance, attracting devotees from far and wide. The presiding deity of the temple is Lord Nageshwara, a form of Lord Shiva worshipped as the lord of serpents. The temple complex features intricately carved sculptures and towering gopurams (gateway towers), showcasing the rich craftsmanship of ancient Tamil architecture. Devotees visit the Nageshwara Temple to seek blessings for health, prosperity, and protection from snake-related afflictions, as snakes hold symbolic significance in Hindu mythology. The temple is also associated with various festivals and rituals celebrated throughout the year, adding to its cultural vibrancy and spiritual allure.',
                'Potramarai Kulam Kumbakonam':'Potramarai Kulam, also known as Porthamarai Kulam, is a sacred temple tank located in the heart of Kumbakonam, Tamil Nadu, India. The name "Potramarai" translates to "Golden Lotus," reflecting the serene beauty and spiritual significance of the tank. This historic tank is situated in the vicinity of the Adi Kumbeswarar Temple, one of the prominent Shiva temples in Kumbakonam. Potramarai Kulam is surrounded by small shrines dedicated to various deities, enhancing its religious ambiance. Devotees often visit the tank to perform rituals, offer prayers, and take ceremonial baths, especially during auspicious occasions and festivals. The tranquil atmosphere and picturesque surroundings of Potramarai Kulam make it a cherished destination for spiritual seekers and tourists alike, embodying the cultural richness and religious heritage of Kumbakonam.',
                'Ramaswamy Temple Kumbakonam':'The Ramaswamy Temple, also known as Sri Ramaswamy Temple, is a renowned Hindu temple located in Kumbakonam, Tamil Nadu, India. Dedicated to Lord Rama, an incarnation of the Hindu god Vishnu, this temple is a significant pilgrimage site for devotees of Lord Rama. The main deity of the temple is Lord Ramaswamy, accompanied by his consort, Goddess Sita, and his loyal devotee, Lord Hanuman. The temple architecture showcases intricate carvings and sculptures, depicting scenes from the epic Ramayana and other Hindu mythological stories. The Ramaswamy Temple is revered for its religious importance and cultural heritage, attracting devotees and tourists alike who come to seek blessings, offer prayers, and admire the spiritual ambiance of the sacred site.',
                'Srinivasa Ramanujam House':'Srinivasa Ramanujan, one of India s greatest mathematical geniuses, was born on December 22, 1887, in Erode, Tamil Nadu, India. However, he spent much of his formative years in Kumbakonam, where his family moved when he was a child. The exact location of Ramanujan s childhood home in Kumbakonam is not widely known. Ramanujan s house in Kumbakonam is not a tourist attraction and is not open to the public. However, there are efforts to preserve and commemorate his legacy in the region, including the SASTRA Ramanujan Prize, an award given annually by the Shanmugha Arts, Science, Technology & Research Academy (SASTRA) to mathematicians under 32 years of age.'}
        file1 = request.files['filename']
        imgfile = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(imgfile), exist_ok=True)
        
        file1.save(imgfile)
        #model = load_model('model.h5')
        model = load_model('keras_model1.h5')
        # Load the labels
        # classes = open("labels1.txt", "r").readlines()
        img_ = image.load_img(imgfile, target_size=(224, 224, 3))
        img_array = image.img_to_array(img_)
        img_processed = np.expand_dims(img_array, axis=0)
        img_processed /= 255.
        prediction = model.predict(img_processed)
        index = np.argmax(prediction)
        result = "Unknown"
        value = "Description not available"

        if index < len(classes):
            result = str(classes[index]).title()
            # Retrieve description from desc dictionary based on result
            value = desc.get(result, "Description not available")  # Get description or default message
            print(value)
        
        image_url = url_for('static', filename='file/' + file1.filename)
        city="kumbakonam"
        url = f"{BASE_URL}q={city}&appid={API_KEY}"
        response = requests.get(url)
    
        if response.status_code == 200:
            data = response.json()
            temp_data.append(data)
            temp_data1=f"{city:-^30}"+"\n"+f"Temperature: {round( data['main']['temp'] - 273.15, 2)}°C"+"\n"+f"Humidity: {data['main']['humidity']}%"+"\n"+f"Pressure: {data['main']['pressure']} hPa"+"\n"+f"Wind Speed: {data['wind']['speed']} m/s"+"\n"+f"Longitude and Latitude: {data['coord']['lon']}, {data['coord']['lat']}"+"\n"+f"Weather: {data['weather'][0]['main']}"+"\n"+f"Weather Description: {data['weather'][0]['description']}"
        print("map_res",temp_data1)
        return render_template('prediction_result.html', msg=result, desc_msg=value, src=imgfile, temp_msg=temp_data1, view='style=display:block', view1='style=display:none')
    elif request.method == 'GET':
        return render_template('index2.html')

@app.route('/prediction_result2')
def prediction_result2():
    result = request.args.get('result')
    image_url = request.args.get('image_url')
    return render_template('prediction_result.html', result=result, image_url=image_url)

# Weather map integration

BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "5b0d498b57a2899ac882b7f6b8544290"

def get_weather_data(city):
    url = f"{BASE_URL}q={city}&appid={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
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
        
        return lat, lon
    else:
        return None, None

def generate_weather_map(city):
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
        
        weather_map_path = f"static/weather_maps/weather_map_{city}.html"
        map.save(weather_map_path)
        return weather_map_path
    else:
        return None

@app.route('/weather_map/<city>')
def weather_map(city):
    weather_map_path = generate_weather_map(city)
    if weather_map_path:
        return render_template('map.html', weather_map_path=weather_map_path)
    else:
        return "Weather data for this city is not available."
@app.route('/map1')
def map1():
    return render_template("kumbakonam_map.html")
@app.route('/map2')
def map2():
    return render_template("mannargudi_map.html")

if __name__ == '__main__':
    app.run(debug=True, port=7000)
