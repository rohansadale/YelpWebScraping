'''
# Add YelpAPI key in config.py file
# Add Neighbourhood names in Cities.txt file. 
	Sample :  
		CityName1|Neighbourhood1
		CityName1|Neighbourhood2
		CityName2|Neighbourhood1
		...
		...
# Output file formed as CityName1.csv, CityName2.csv, ...
# Usage:  python  restaurant.py
'''


import argparse
from pprint import pprint
import json
import sys
import urllib
import urllib2
import oauth2
import config
import csv
import time
import getlocation

#Global Variables Declaration
API_HOST	= "api.yelp.com"
SEARCH_PATH	= "/v2/search"
BUSINESS_PATH	= "/v2/business/"
SEARCH_LIMIT 	= 20
OFFSET_LIMIT	= 0
SORT_TYPE	= 2
MAX_LIMIT	= 100

CONSUMER_KEY	= config.consumerKey
CONSUMER_SECRET	= config.consumerSecret
TOKEN		= config.token
TOKEN_SECRET	= config.tokenSecret 


def request(host, path, urlParams=None):
	urlParams = urlParams or {}
	url = 'https://{0}{1}'.format(host, path)
	consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
	oauthRequest = oauth2.Request(method="GET", url=url, parameters=urlParams)
	oauthRequest.update(
        	{
	            'oauth_nonce': oauth2.generate_nonce(),
	            'oauth_timestamp': oauth2.generate_timestamp(),
        	    'oauth_token': TOKEN,
	            'oauth_consumer_key': CONSUMER_KEY
	        }
    	)
	token = oauth2.Token(TOKEN, TOKEN_SECRET)
	oauthRequest.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
	signedUrl = oauthRequest.to_url()
	conn = urllib2.urlopen(signedUrl, None)
	
	try:
		response = json.loads(conn.read())
	finally:
		conn.close()
	
	return response	


def search(location, longitude, latitude):

	urlParams = {
			'location'	: location,
			'cll'		: str(latitude) + ', ' + str(longitude),
			'term'		: 'restaurants',
			'limit'		: SEARCH_LIMIT,
			'offset'	: OFFSET_LIMIT,
			'sort'		: SORT_TYPE
		}
	return request(API_HOST, SEARCH_PATH, urlParams)
	

def writeData(location, dataCategory, dataCategoryType):
	if dataCategoryType == 'restaurants': 
		with open(location + '_Restaurants.csv', 'a') as f:
			fieldNames = ['ID', 'NAME', 'REVIEW_COUNT', 'RATING', 'LONGITUDE', 'LATITUDE', 'CITY', 'STATE', 'ZIP', 'COUNTRY', 'CATEGORY']	
			writer = csv.DictWriter(f, fieldnames=fieldNames, delimiter='|')
			writer.writerows(dataCategory)
	elif dataCategoryType == 'categories':
		with open(location + '_Category.csv', 'a') as f:
			fieldNames = ['RESTAURANT_ID', 'CATEGORY']
			writer = csv.DictWriter(f, fieldnames=fieldNames, delimiter='|')
			writer.writerows(dataCategory)
	
def getallNeighbourhoodData():
	neighbourhood = {}
	with open('Cities.txt', 'r') as f:
        	areas = f.readlines()

	for area in areas:
	        area = area.strip('\n').split('|')
	        if area[0] not in neighbourhood.keys():
	                neighbourhood[area[0]] = list()
	                neighbourhood[area[0]].append(area[1])
	        else:
	                neighbourhood[area[0]].append(area[1])
	return neighbourhood


def queryApi(city, neighbourhood = ''):
	restaurantData = []
	categoryData = []
	tempRestaurantData = {}
	tempCategoryData = {}
	global OFFSET_LIMIT
	global MAX_LIMIT
	location = neighbourhood + ', ' + city
        longitude, latitude = getlocation.getCoordinates(location)
	print location, longitude, latitude

	while OFFSET_LIMIT < MAX_LIMIT:
		response = search(location, longitude, latitude)
		MAX_LIMIT = response['total']

		allRestaurantData = response['businesses']
		if len(allRestaurantData) > 0:
			for restaurant in allRestaurantData:
				tempRestaurantData['ID']		= restaurant['id'].encode('ascii', 'ignore')
				tempRestaurantData['NAME']		= restaurant['name'].encode('ascii', 'ignore')
				tempRestaurantData['REVIEW_COUNT']	= restaurant['review_count']
				tempRestaurantData['RATING']		= restaurant['rating']
				if restaurant['location'].get('coordinate'):
					tempRestaurantData['LONGITUDE']		= restaurant['location']['coordinate']['longitude']
					tempRestaurantData['LATITUDE']		= restaurant['location']['coordinate']['latitude']
				else:
	                                tempRestaurantData['LONGITUDE']         = 0.0
        	                        tempRestaurantData['LATITUDE']          = 0.0
				tempRestaurantData['CITY']		= restaurant['location']['city']
				tempRestaurantData['STATE']		= restaurant['location']['state_code']
				tempRestaurantData['ZIP']		= restaurant['location']['postal_code'] if restaurant['location'].get('postal_code') else 99999
				tempRestaurantData['COUNTRY']		= restaurant['location']['country_code']
				
				tempRestaurantData['CATEGORY']		= ''	
				if restaurant.get('categories'):
					for category in restaurant['categories']:
#						tempCategoryData['RESTAURANT_ID']	= restaurant['id'].encode('ascii', 'ignore') 
#						tempCategoryData['CATEGORY']	= category[1].encode('ascii', 'ignore')
#						categoryData.append(tempCategoryData)
#						tempCategoryData = {}
						categoryData.append(category[1].encode('ascii', 'ignore'))					
					
					tempRestaurantData['CATEGORY'] = ",".join(categoryData)
					categoryData = []

			 	restaurantData.append(tempRestaurantData)
				tempRestaurantData = {}
	
			time.sleep(4)
			OFFSET_LIMIT += 20
		
	print 'Writing {0} records'.format(OFFSET_LIMIT)
	writeData(city, restaurantData, 'restaurants')
	OFFSET_LIMIT = 0

def main():
	parser = argparse.ArgumentParser();
	parser.add_argument('-l', '--location', dest='location', type=str, help='Name of City')
	inputValues = parser.parse_args()

	allCities = getallNeighbourhoodData()
	for city, neighbourhoods in allCities.items():
		for neighbourhood in neighbourhoods:			
		        try:
				queryApi(city, neighbourhood)
			except urllib2.HTTPError as error:
		                sys.exit('Encountered HTTP error {0}. Abort Program.'.format(error.code))
		queryApi(city)

		
if __name__ == '__main__':
	main()
