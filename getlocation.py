import urllib
import json

googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'

def getCoordinates(address):
    address = address.encode('utf-8')
    params = {
        'address': address,
    }
    url = googleGeocodeUrl + urllib.urlencode(params)
    json_response = urllib.urlopen(url)
    response = json.loads(json_response.read())
    if response['results']:
        location = response['results'][0]['geometry']['location']
        latitude, longitude = location['lat'], location['lng']
    else:
        latitude, longitude = None, None
    return latitude, longitude

