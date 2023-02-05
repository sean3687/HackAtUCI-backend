import requests
from urllib.request import urlopen
import json

BASE_URL = "https://www.americancampus.com"
CURRENT_YEAR = 2023
COMMUNITIES = [
  "plaza-verde",
  "plaza-verde-2",
  "vista-del-campo",
  "vista-del-campo-norte",
  "camino-del-sol",
  "puerta-del-sol",
]

def getAPIURL(comm):
    searchUrl = "https://www.americancampus.com/student-apartments/ca/irvine/" + comm + "/floor-plans#/"
    response = requests.get(searchUrl)
    htmlString = response.text

    endpointURL = htmlString.split('id="endpointURL" value="')[1].split('">')[0]
    return BASE_URL + endpointURL

def getJSONdata(api_link):
    response = urlopen(api_link)
    return json.loads(response.read())