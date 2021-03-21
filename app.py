from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars


app = Flask(__name__)

mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")

@app.route("/")
def home():

    mongo_data = mongo.db.mars_coll.find_one()

    return render_template("index.html", mars_coll = mongo_data)

@app.route("/scrape")
def scrape():

    data_dict = scrape_mars.scrape()
    
    mongo.db.mars_coll.update_many({}, data_dict, upsert=True)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)