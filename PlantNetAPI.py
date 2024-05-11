# necessary modules imported
import requests
import json
from flask import Flask, request, render_template
from pprint import pprint
import os
from werkzeug.utils import secure_filename
import webbrowser
import creds

# API setup
PROJECT = "all"
api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={creds.API_KEY}"


# Flask app set up
app = Flask(__name__, static_url_path='/static')

# Upload folder setup
upload_folder = os.path.join('static', 'uploads')
app.config['UPLOAD'] = upload_folder

# Automatically open page in browser upon project running
webbrowser.open('http://127.0.0.1:8095/PlantNet_Project.html')

# Webpages and directories setup up        # -- These side comments apply to similar functions below --
@app.route('/Home.html')                   # Define webpage path
def home():
    return render_template('Home.html')    # Displays HTML display on page

@app.route('/AboutPage.html')
def about():
    return render_template('AboutPage.html')

@app.route('/HowToUse.html')
def howto():
    return render_template('HowToUse.html')

@app.route('/PlantNet_Project.html', methods=['GET', 'POST'])
def index():                                                # This is the primary functionality of the program
    if request.method == 'POST':                            # Upon submission from HTML page, method, image is released through 'POST'
        image = request.files['img']                        # Inputted image saved in HTML under ID of 'img', request image data
        image_data = image.read()

        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD'], filename))
        img = os.path.join('uploads', filename)

        data = {                                            # This is essentially just sets the API identification to automatically -
                                                            # identify what part of the plant it is looking at
            'organs': ['auto']
        }

        files = [
            ('images', (image.filename, image_data))
        ]

        req = requests.Request('POST', url=api_endpoint, files=files, data=data)    # Prepare necesary data for API functionality
        prepared = req.prepare()                                                    # Save as a prepared variable

        s = requests.Session()                              # Begin request session
        response = s.send(prepared)                         # Send request via POST
        json_result = json.loads(response.text)             # Load returned API json

        if response.status_code == 200:                     # Check for successful identification response
            Status = "Success"
        else:
            Status = "Else"

        Common_name = json_result['results'][0]['species']['commonNames']                           # -- Separate important data from json --
        Scientific_name = json_result['results'][0]['species']['scientificNameWithoutAuthor']
        Score = round(float(json_result['results'][0]['score'])*100)

        Common_nameS=""                                     # Variable for multiple common names

        for name in Common_name:                            # -- Add all common names from json to separate variable --
            Common_nameS=(f"{Common_nameS}, {name}")
        Common_nameS=(Common_nameS[1:])

        global FULL                                         # -- Save common names to a global variable to go on returned upload page --
        FULL = (f"Common Names:{Common_nameS}")
        PLANTING=("")

        f = open('SanCarlosPlants.json')                    # Open and load San Carlos plant json data file

        data = json.load(f)
        
        line_count = 0
        for i in data:                                              # -- All this checks for and separates data if the plant is included in the json file.
            if i['Current Botanical Name'] == Scientific_name:      #    It separates, reformats, and adds the necesary data to the 'FULL' variable --
                for d in i:
                    if line_count < 9:
                        if i[d]=="":
                            linkage = "N/A"
                        else:
                            linkage = i[d]
                            linkage = linkage.replace(",", ", ")
                        new_text = (f"{d}: {linkage}")
                        FULL = (f"{FULL}\n{new_text}")
                        line_count += 1
                    else:
                        linkage = i[d]
                        if i[d]=="":
                            linkage = "N/A"
                        linkage = linkage.replace(",", ", ")
                        new_text = (f"{d}: {linkage}")
                        PLANTING = (f"{PLANTING}{new_text}\n")
                        line_count += 1
                PLANTING=(f"{PLANTING}\n\n")

        f.close()

        return render_template("PlantNet_Project.html", text=FULL, img=img, planting=PLANTING)      # Refresh/render page with added information

    return render_template('PlantNet_Project.html')      # Displays updated upload page

if __name__ == '__main__':                               # Runs server in port 8095 (used that port for uniqueness and during bug fixing)
    app.run(debug=False, port=8095)