from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit")
def submit():
    return render_template("submit.html")

@app.route("/view")
def view():
    return render_template("view.html")