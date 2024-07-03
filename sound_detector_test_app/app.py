from flask import Flask, render_template
from flask_sock import Sock
from sed_extractor import NDISEDExtractor
from ndi_interface import ndi_finder

app = Flask(__name__)
sock = Sock(app)
sed_extractor = None


    


@app.route('/')
def index():
    global sed_extractor
    finder = ndi_finder.NDIFinder()
    found = False
    while not found:
        sources = finder.get_ndi_sources()
        for i in sources:
            if "NDI PANNS" in i.ndi_name:
                print("Found PANNS module")
                sed_extractor = NDISEDExtractor(i)
                found = True
                break

    sed_extractor.start()

    return render_template('index.html')

@sock.route('/prediction')
def echo(ws):
    global sed_extractor
    while True:
        ws.send(sed_extractor.get_prediction())

if __name__ == '__main__':
    app.run(debug=True, port=5002)