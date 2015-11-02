import sys
from bs4 import BeautifulSoup
import requests
import config
import argparse
import getlocation
import urllib
import urllib2
import oauth2
import config
import json
from pprint import pprint
import re
from nltk import word_tokenize
import string

reload(sys)
#sys.setdefaultencoding("utf-8")

API_HOST	= "api.yelp.com"
SEARCH_PATH	= "/v2/search"

# Yelp API Keys from config file
CONSUMER_KEY	= config.consumerKey
CONSUMER_SECRET	= config.consumerSecret
TOKEN		= config.token
TOKEN_SECRET	= config.tokenSecret 

# Request and response from Yelp API
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

# Declare search parameters to be passed to API
def search(location, term, category):

	# Get longitude and latitude from Google Geocoding API V3 
	longitude, latitude = getlocation.getCoordinates(location)
	urlParams = {
			'location'		: location,
			'cll'			: str(latitude) + ', ' + str(longitude),
			'term'			: term,
			'limit'			: 20,
			'sort'			: 2,
			'category_filter'	: category
			}
	return request(API_HOST, SEARCH_PATH, urlParams)

	
def scrapeWeb(top20Restaurants):
	allReviews = {}
	for restaurant in top20Restaurants:
		allReviews[restaurant] = []
		NumReview = top20Restaurants[restaurant][1]
		pageCount = 0
		while NumReview > 0:
			url = 'http://www.yelp.com/biz/' + restaurant + '?start=' + str(pageCount)	
			html = requests.get(url).text
			soup = BeautifulSoup(html, 'html.parser')
			numberofEnglishReviews = re.sub('\D',r'',soup.find('span', class_='tab-link_count').text)
			reviews = soup.findAll('div', {'class' : 'review-content'})	
			for review in reviews:
				content = " ".join(review.find('p').strings)
				rating = review.find('meta', itemprop = 'ratingValue')['content']
				allReviews[restaurant].append([content, rating])

			NumReview -= len(reviews)
			pageCount += len(reviews)
			if int(top20Restaurants[restaurant][1]) - int(numberofEnglishReviews) == NumReview:
				break


	reviewData = []
#	fw = open('reviewData','wb')
	for restaurant in top20Restaurants:
		print restaurant
		for review, rating in allReviews[restaurant]:
			reviewData.append([restaurant, review, rating])
#			fw.write(restaurant.encode('ascii', 'ignore') + '\t' + review.encode('ascii', 'ignore') + '\t' + rating + '\n')
#	fw.close()
	return reviewData

def reviewFilter(reviewData):
	filteredReviews = []
	dictionary = ['suggestion', 'suggest', 'should', 'improve', 'improvement','future','hope','wish']
	punctuations = list(string.punctuation)
	f1 = open('reviewData')
#	for line in f1:
#		restaurant, review, rating = line.rstrip().split('\t')
	for restaurant, review, rating in reviewData:
		if rating in ['1.0', '2.0', '3.0']:
			tokens = word_tokenize(review)
			words = [w.lower() for w in tokens]
			words = [w for w in words if w not in punctuations]
			result = 0
			for target in dictionary:
				if target in words:
					result = 1
					filteredReviews.append([restaurant, review])
	
	f = open('reviewData','wb')
	for restaurant, review in filteredReviews:
		f.write(restaurant.encode('ascii', 'ignore') + '|' + review.encode('ascii', 'ignore') + '\n')
	f.close()
	

def main():
	parser = argparse.ArgumentParser(description='Scrape Reviews through Yelp API and Web');
	parser.add_argument('-l', '--location', dest='location', type=str, help='Location where you want to search reviews', required=True)
	parser.add_argument('-c', '--category', dest='category', type=str, help='Category for the reviews. eg. chinese, indian, etc. ', required=True)
	parser.add_argument('-t', '--term', dest='term', type=str, help='Search by restaurant, bar, etc ', required=True)
	inputValues = parser.parse_args()

	response = search(inputValues.location, inputValues.term, inputValues.category)
        top20Restaurants = {}
	if response.get('businesses'):
		for restaurant in response['businesses']:
		        top20Restaurants[restaurant['id']] = [restaurant['rating'], restaurant['review_count']]

	reviewData = scrapeWeb(top20Restaurants)
	reviewFilter(reviewData)

if __name__ == '__main__':
	main()
