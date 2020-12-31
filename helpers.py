import json
import requests
import http.client, urllib.request, urllib.parse, urllib.error, base64
from bs4 import BeautifulSoup
from flask import redirect, render_template, request
from datetime import datetime
import os

# extracts API keys from local variable configuration
METOFFICE_API = os.environ.get('METOFFICE_API')
NRW_API_SUBSCRIPTIONKEY = os.environ.get('NRW_API_SUBSCRIPTIONKEY')
NRW_API_SUBSCRIPTIONKEY_2 = os.environ.get('NRW_API_SUBSCRIPTIONKEY_2')
OPENWEATHER_API = os.environ.get('OPENWEATHER_API')

def weathertext():
    
    #the location list can be obtained from here = 
    # url = f'http://datapoint.metoffice.gov.uk/public/data/txt/wxfcs/mountainarea/json/sitelist?key={METOFFICE_API}'

    # API request url for national park text forecast
    url = f'http://datapoint.metoffice.gov.uk/public/data/txt/wxfcs/mountainarea/json/Snowdonia?key={METOFFICE_API}'

    response = urllib.request.urlopen(url)
    data = response.read()
    rawdata = json.loads(data)

    return rawdata.get("Report")
    

def metforecast():
    
    #the location list can be obtained from here = f"http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/datatype/sitelist?key={METOFFICE_API}"

    url = f'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/350661?res=3hourly&key={METOFFICE_API}'
    
    '''calls weather from metoffice datapoint API'''
    response = urllib.request.urlopen(url)
    data = response.read()
    rawdata = json.loads(data)
    importantbits = rawdata.get("SiteRep").get("DV").get("Location").get("Period")

    #clean the report of out of date info
    #remove out of date information from the api call (e.g. times already passed)
    #while the date now is more than the date in the first report, pop the first record.  
    checkactive = True
    while checkactive == True: 
        datestr = importantbits[0].get("value")
        datestr = datestr[:-1]
        datetime_obj = datetime.strptime(datestr, "%Y-%m-%d")
        if datetime_obj.day < datetime.now().day:
            importantbits.pop(0)
        else:
            checkactive = False

    #while the time now is more than 179 mins behind the timecode in the first report, pop first report.  
    while int(importantbits[0].get("Rep")[0].get("$")) < ((datetime.now().hour * 60) - 179):
        importantbits[0].get("Rep").pop(0) 

    return importantbits


def nrwapialertrequest():

    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': NRW_API_SUBSCRIPTIONKEY,
    }

    params = urllib.parse.urlencode({
    })

    try:
        conn = http.client.HTTPSConnection('api.naturalresources.wales')
        conn.request("GET", "/floodwarnings/v3/distance/5000/latlon/53.036888/-4.047120?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        rawdata = json.loads(data)
        conn.close()

    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    # this accounts for cases where no alerts are returned from api 
    if len(rawdata.get('features')) == 0:
        rawdata["SEVERITY"]="No warnings or alerts"
        rawdata["RIM_ENGLISH"]=""
        return rawdata
    else:
        return rawdata.get('features')[0].get('properties')
        

def nrwapilevelrequest():
    headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': NRW_API_SUBSCRIPTIONKEY_2,
    }

    params = urllib.parse.urlencode({
    })

    try:
        conn = http.client.HTTPSConnection('api.naturalresources.wales')
        conn.request("GET", "/rivers-and-seas/v1/api/StationData/byLocation?distance=5000&lat=53.036888&lon=-4.047120&%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        rawdata = json.loads(data)
        conn.close()


    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    return rawdata[1].get("parameters")


def news():

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
    url = "http://feeds.bbci.co.uk/news/rss.xml?edition=uk"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    wanted = soup.find_all('title')
    return wanted


def severeweather():
    url = f'https://api.openweathermap.org/data/2.5/onecall?lat=53.036888&lon=-4.047120&exclude=hourly,daily&appid={OPENWEATHER_API}'

    response = urllib.request.urlopen(url)
    data = response.read()
    rawdata = json.loads(data)
    if rawdata.get("alerts"):
        return rawdata.get("alerts")
    else:
        return []