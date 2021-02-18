import flask
from tinydb import TinyDB, Query
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import os

app = flask.Flask(__name__, template_folder='')
app.config["DEBUG"] = False
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/', methods=['GET'])
@cross_origin()
def home():
    return "<h1>225 Dashboard API</h1>"

# A route to return all of the available entries in our catalog.
@app.route('/api/v1/log/all', methods=['GET'])
@cross_origin()
def api_log_all():
    db = TinyDB('../log_list.json')
    table = db.table('history')
    return jsonify(table.all())

@app.route('/api/v1/log/last', methods=['GET'])
@cross_origin()
def api_log_last():
    db = TinyDB('../log_list.json')
    table = db.table('history')
    ordered = sorted(table.all(), key=lambda k: k['timestamp'])
    return jsonify(ordered[-1])

@app.route('/api/v1/log', methods=['GET'])
@cross_origin()
def api_log_filter():
    db = TinyDB('../log_list.json')
    table = db.table('history')
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
        User = Query()
        results = table.get(doc_id=id)
    elif 'name' in request.args:
        name = str(request.args['name'])
        User = Query()
        results = table.search(User.name == name)
    else:
        return "Error: No id field provided. Please specify an id."

    return jsonify(results)

@app.errorhandler(404)
@cross_origin()
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()