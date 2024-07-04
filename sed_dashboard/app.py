from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    sed_status = False
    is_connected = False
    cur_prediction = None
    try:
        ndi_sources = requests.get('http://sed-backend:5000/sources')
        ndi_sources.json()
        sed_status = True
        prediction_req = requests.get('http://sed-backend:5000/prediction')
        if prediction_req.status_code == 200:
            is_connected = True
            cur_prediction = prediction_req.json()["prediction"]
        else:
            cur_prediction = None

        ndi_sources = ndi_sources.json()["sources"]

    except requests.exceptions.RequestException as e:
        print(e)
        ndi_sources = []
    if request.method == 'POST':
        if request.form.get("submit_btn") == "connect":
            ndi_source = request.form.get("selected_source")
            resp = requests.post('http://sed-backend:5000/start', json = {"source": ndi_source})
        elif request.form.get("submit_btn") == "disconnect":
            resp = requests.post('http://sed-backend:5000/stop')

    return render_template('index.html', sources = ndi_sources, panns_found = sed_status, prediction = cur_prediction, connected = is_connected)