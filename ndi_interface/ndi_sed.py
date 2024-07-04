from flask import Flask, jsonify, request
from ndi_panns import NDIPanns
from ndi_interface import ndi_finder

app = Flask(__name__)

panns_node = None

finder = ndi_finder.NDIFinder()

ndi_sources = finder.get_ndi_sources()

@app.route('/sources', methods=['GET'])
def get_sources():
    return jsonify(sources=[source.ndi_name for source in ndi_sources])

@app.route('/refresh_sources', methods=['POST'])
def refresh_sources():
    global ndi_sources
    ndi_sources = finder.get_ndi_sources()
    return jsonify(sources=[source.ndi_name for source in ndi_sources])

@app.route('/start', methods=['POST'])
def start():
    global panns_node
    if panns_node is None:
        data = request.json
        source_name = data.get('source')
        for i in ndi_sources:
            if i.ndi_name == source_name:
                source_name = i
                break
            else:
                return jsonify(message='Source not found'), 404
        panns_node = NDIPanns(source_name)
        panns_node.start()
        return jsonify(message='PANNs started')
    else:
        return jsonify(message='PANNs already started'), 409

@app.route('/stop', methods=['POST'])
def stop():
    global panns_node
    if panns_node is not None:
        panns_node.stop()
        panns_node.cleanup()
        panns_node = None
    return jsonify(message='PANNS stopped')

@app.route('/prediction', methods=['GET'])
def prediction():
    global panns_node
    if panns_node is not None:
        return jsonify(prediction=panns_node.get_prediction())
    else:
        return jsonify(error='PANNs not started'), 409

if __name__ == '__main__':
    app.run(debug=True, port=5001)