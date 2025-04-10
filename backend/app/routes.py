from flask import jsonify
from . import api_blueprint

@api_blueprint.route("/data")
def get_data():
    return jsonify({"message": "Hello from Flask!"})