import requests
import json
from flask import Flask, request, render_template
from pprint import pprint
import os
from werkzeug.utils import secure_filename

API_KEY = "2b108V22Bnpcm0ozunmOe5hUu"
PROJECT = "all"
api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"

app = Flask(__name__, static_url_path='/static')

upload_folder = os.path.join('static', 'uploads')
app.config['UPLOAD'] = upload_folder

@app.route('/Home.html')
def home():
    return render_template('Home.html')

@app.route('/AboutPage.html')
def about():
    return render_template('AboutPage.html')

@app.route('/HowToUse.html')
def howto():
    return render_template('HowToUse.html')

@app.route('/PlantNet_Project.html', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image = request.files['img']
        image_data = image.read()

        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD'], filename))
        img = os.path.join('uploads', filename)

        data = {
            'organs': ['auto']
        }

        files = [
            ('images', (image.filename, image_data))
        ]

        req = requests.Request('POST', url=api_endpoint, files=files, data=data)
        prepared = req.prepare()

        s = requests.Session()
        response = s.send(prepared)
        json_result = json.loads(response.text)

        if response.status_code == 200:
            Status = "Success"
        else:
            Status = "Else"

        Common_name = json_result['results'][0]['species']['commonNames']
        Scientific_name = json_result['results'][0]['species']['scientificNameWithoutAuthor']
        Score = round(float(json_result['results'][0]['score'])*100)

        Common_nameS=""

        for name in Common_name:
            Common_nameS=(f"{Common_nameS}, {name}")
        Common_nameS=(Common_nameS[1:])

        global FULL
        FULL = (f"Common Names:{Common_nameS}")
        PLANTING=("")

        f = open('SanCarlosPlants.json')

        data = json.load(f)
        
        line_count = 0
        for i in data:
            if i['Current Botanical Name'] == Scientific_name:
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

        return render_template("PlantNet_Project.html", text=FULL, img=img, planting=PLANTING)

    return render_template('PlantNet_Project.html')

if __name__ == '__main__':
    app.run(debug=False, port=8095)
