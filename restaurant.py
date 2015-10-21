import argparse
import pprint
import json
import sys
import urllib
import urllib2
import oauth2
import config


#Global Variables Declaration
API_HOST	= "api.yelp.com"
SEARCH_PATH	= "/v2/search/"
BUSINESS_PATH	= "/v2/business/"
SEARCH_LIMIT 	= 20
OFFSET_LIMIT	= 0
MAX_LIMIT	= 60

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


def search(location):
	urlParams = {
			'location'	: location,
			'limit'		: SEARCH_LIMIT,
			'offset'	: OFFSET_LIMIT
		}
		
	return request(API_HOST, SEARCH_PATH, urlParams)


def queryApi(location):
	restaurantData = []
	global OFFSET_LIMIT
	while OFFSET_LIMIT < MAX_LIMIT:
		response = search(location)
		allRestaurantData = response['businesses']
		for restaurant in allRestaurantData:
#			tempData['name'] = restaurant['name']
#			tempData['review_count'] = restaurant['review_count']
		 	restaurantData.append(restaurant['name'])
		OFFSET_LIMIT += 20 
#	pprint.pprint(restaurantData, indent = 2)

def main():
	parser = argparse.ArgumentParser();
	parser.add_argument('-l', '--location', dest='location', type=str, help='Name of City')
	inputValues = parser.parse_args()

	try:
		queryApi(inputValues.location)
	except urllib2.HTTPError as error:
		sys.exit('Encountered HTTP error {0}. Abort Program.'.format(error.code))		
		

if __name__ == '__main__':
	main()
