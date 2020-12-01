from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv

import os

load_dotenv('.env')

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Location(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    address = db.Column(db.Text)
    
    distancing_rating = db.Column(db.Float(1))
    distancing_num_ratings = db.Column(db.Integer, default=0)
    mask_rating = db.Column(db.Float(1))
    mask_num_ratings = db.Column(db.Integer, default=0)
    crowd_rating = db.Column(db.Float(1))
    crowd_num_ratings = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "{0}: {1}".format(self.id_, self.address)

@app.before_first_request
def init_db():
  db.create_all()

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/search")
def search():
  return render_template("search.html")

@app.route("/placesapi", methods=["POST"])
def handle_api():
    address_component = request.get_json()["address_components"]
    print(address_component)
    street_number = ""
    route = ""
    locality = ""
    state = ""
    country = ""
    postal_code = ""
    for component in address_component:
      if "street_number" in component["types"]:
        street_number = component["long_name"]
      elif "route" in component["types"]:
        route = component["long_name"]
      elif "locality" in component["types"]:
        locality = component["long_name"]
      elif "administrative_area_level_1" in component["types"]:
        state = component["long_name"]
      elif "country" in component["types"]:
        country = component["long_name"]
      elif "postal_code" in component["types"]:
        postal_code = component["long_name"]
    if street_number == "" and route == "":
      flash("1Please choose a valid location! Valid locations are businesses or exact addresses.")
      return redirect(url_for("search"))
    address = street_number + " " + route + ", " + locality + ", " + state + " " + postal_code
    matching_entry = Location.query.filter_by(address=address).first()
    if not matching_entry:
      new_location = Location(address=address)
      db.session.add(new_location)
      db.session.commit()
      print("New Location:", new_location)
      session["id_"] = new_location.id_
      return redirect(url_for("search"))
    session["id_"] = matching_entry.id_
    return redirect(url_for("search"))

@app.route("/gotoview")
def go_to_view():
  id_ = session.get("id_")
  if not id_:
    flash("1Please choose a valid location! Valid locations are businesses or exact addresses.")
    return redirect(url_for("search"))
  flash("0Successfully retreived ratings for the specified location!")
  return redirect(url_for("view"))

@app.route("/view", methods=["GET", "POST"])
def view():
  id_ = session.get("id_")
  if not id_:
    flash("1Please choose a valid location! Valid locations are businesses or exact addresses.")
    return redirect(url_for("search"))
  match = Location.query.filter_by(id_=id_).first()
  if request.method == "POST":
    distancing = request.form.get("distancing")
    mask = request.form.get("mask")
    crowd = request.form.get("crowd")
    if distancing:
      if match.distancing_rating:
        current_rating = (match.distancing_rating * match.distancing_num_ratings + int(distancing)) / (match.distancing_num_ratings + 1)
        match.distancing_rating = current_rating
      else:
        match.distancing_rating = distancing
      match.distancing_num_ratings += 1
    if mask:
      if match.mask_rating:
        current_rating = (match.mask_rating * match.mask_num_ratings + int(mask)) / (match.mask_num_ratings + 1)
        match.mask_rating = current_rating
      else:
        match.mask_rating = mask
      match.mask_num_ratings += 1
    if crowd:
      if match.crowd_rating:
        current_rating = (match.crowd_rating * match.crowd_num_ratings + int(crowd)) / (match.crowd_num_ratings + 1)
        match.crowd_rating = current_rating
      else:
        match.crowd_rating = crowd
      match.crowd_num_ratings += 1
    db.session.commit()
  return render_template(
    "view.html", 
    address=match.address, 
    distancing=match.distancing_rating, 
    distancing_cnt=match.distancing_num_ratings, 
    mask=match.mask_rating, 
    mask_cnt=match.mask_num_ratings, 
    crowd=match.crowd_rating, 
    crowd_cnt=match.crowd_num_ratings
  )