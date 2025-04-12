from flask import Flask, render_template, send_from_directory

app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend/templates")

@app.route("/api/data")
def get_data():
    return {"message": "Hello from Flask!"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route("/assets/<path:filename>")
def assets_files(filename):
    return send_from_directory("../frontend/assets", filename)

if __name__ == "__main__":
    app.run(port=5000, debug=True)