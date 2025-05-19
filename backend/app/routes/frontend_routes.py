from flask import Blueprint, render_template, send_from_directory

frontend_blueprint = Blueprint('frontend', __name__)

@frontend_blueprint.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@frontend_blueprint.route('/static/<path:filename>', methods=['GET'])
def static_files(filename):
    return send_from_directory("../../public/static", filename)

@frontend_blueprint.route('/assets/<path:filename>', methods=['GET'])
def assets_files(filename):
    return send_from_directory("../../public/assets", filename)