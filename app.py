### my first api call and flask app!

import urllib.request
import json
import requests
from helpers import metforecast, weathertext, nrwapialertrequest, nrwapilevelrequest, news, severeweather
from datetime import datetime
from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup

app = Flask(__name__, static_url_path='/static')

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["TESTING"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

# implement a function to pull weather warnings into this.
# Implement a function to pull together the MWIS page https://www.mwis.org.uk/forecasts/english-and-welsh/snowdonia-national-park/text
# Implement a function to pull the river level warnings and height information.
# Implement a function to pull the snowdon webcam from https://www.snowdonia.gov.wales/visiting/local-information/webcams

@app.route('/')
def summary():

    #POPULATE CURRENT WEATHER TILE
    #calls the weathetext function which pulls text forecast from metoffice api
    weather = weathertext().get("Days").get("Day")[0]
    #checks the length of the weather summary and cuts it down if it is >150 characters
    if len(weather.get("Weather")) > 300:
        weathertextupdate = {"Weather": weather.get("Weather")[:299] + "..."}
        weather.update(weathertextupdate)
    #calls the full metweather info for use in the tile
    metweatherinfo = metforecast()
    
    
    #obtains the current conditions from the metforecast function return    
    currentconditions = metweatherinfo[0].get("Rep")[0].get("W")
    currenttemp = metweatherinfo[0].get("Rep")[0].get("T")
    currentwind = metweatherinfo[0].get("Rep")[0].get("W")
    currentgusts = metweatherinfo[0].get("Rep")[0].get("G")
    
    #POPULATE RIVEL LEVELS TILE
    floodrisk = nrwapialertrequest()
    level = nrwapilevelrequest()
    
    if level[0].get("latestValue") < 1:
        level[0]["latestValue"] = "Medium"
    elif level[0].get("latestValue") > 2:
        level[0]["latestValue"] = "Very High"
    else:
        level[0]["latestValue"] = "High"
        

    #POPULATE NEWS SUMMARY TILE
    newsfeed = news()

    #leaves three top news stories
    del newsfeed[7:]
    del newsfeed[:2]

    #POPULATEWEATHER ALERT LEVELS TILE
    weatheralerts = severeweather()

    return render_template("index.html", weather=weather, floodrisk=floodrisk, level=level, newsfeed=newsfeed, weatheralerts=weatheralerts, currentconditions=currentconditions, currenttemp=currenttemp, currentwind=currentwind, currentgusts=currentgusts)

    
@app.route('/mountain')
def mountain():
    mountainforecast = weathertext()
    if datetime.now().hour > 18:
        navlist = ["Tomorrow", "The Day After", "The Day After That!"]
    else:
        navlist = ["Today", "Tomorrow", "The Day After Tomorrow"]

    print(datetime.now().hour)
    
    return render_template("mountainweather.html", mountainforecast=mountainforecast, navlist=navlist)

@app.route('/metweather')
def metweather():

    weather = metforecast()
    for item in weather:
        datestr = item.get("value")
        datestr = datestr[:-1]
        datetime_obj = datetime.strptime(datestr, "%Y-%m-%d")
        item["value"] = datetime_obj.strftime("%A")
    
    return render_template("metforecast.html", rawdata=weather)