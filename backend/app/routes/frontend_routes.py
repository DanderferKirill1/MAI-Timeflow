from flask import Blueprint, render_template, send_from_directory

frontend_blueprint = Blueprint('frontend', __name__)


@frontend_blueprint.route('/static/<path:filename>', methods=['GET'])
def static_files(filename):
    return send_from_directory("../../public/static", filename)


@frontend_blueprint.route('/assets/<path:filename>', methods=['GET'])
def assets_files(filename):
    return send_from_directory("../../public/assets", filename)


@frontend_blueprint.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@frontend_blueprint.route("/index2", methods=["GET"])
def index_2():
    return render_template("index2.html")


@frontend_blueprint.route("/index3", methods=["GET"])
def index_3():
    return render_template("index3.html")


@frontend_blueprint.route("/calendar", methods=["GET"])
def calendar():
    return render_template("calendar.html")


@frontend_blueprint.route("/noti", methods=["GET"])
def noti():
    return render_template("noti.html")


@frontend_blueprint.route("/safety", methods=["GET"])
def safety():
    return render_template("safety.html")


@frontend_blueprint.route("/settings", methods=["GET"])
def settings():
    return render_template("settings.html")
