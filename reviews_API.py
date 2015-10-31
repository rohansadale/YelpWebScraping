import yelp
import sys
from bs4 import BeautifulSoup
import requests
import config

reload(sys)
sys.setdefaultencoding("utf-8")


yelp_api = yelp.Api(consumer_key=config.CONSUMER_KEY,
                    consumer_secret=config.CONSUMER_SECRET,
                    access_token_key=config.TOKEN,
                    access_token_secret=config.TOKEN_SECRET)

location_city = "Minneapolis"
category = 'chinese'
term = "restaurant"

top20Chinese = yelp_api.Search(term=term, location=location_city, sort = 2, limit = 20, category_filter = category)

top20Restaurants = dict()
for restaurant in top20Chinese.businesses:
	top20Restaurants[restaurant.id] = [restaurant.rating, restaurant.review_count]

allReviews = dict()
for restaurant in top20Restaurants:
#for restaurant in ['tea-house-chinese-restaurant-minneapolis']:
	allReviews[restaurant] = []
	NumReview = top20Restaurants[restaurant][1]
	pageCount = 0
	while NumReview > 0:
		url = 'http://www.yelp.com/biz/' + restaurant + '?start=' + str(pageCount)
		html = requests.get(url).text
		soup = BeautifulSoup(html)
		reviews = soup.findAll('div', {'class' : 'review-content'})
		
		for review in reviews:
			content = " ".join(review.find('p').strings)
			rating = review.find('meta', itemprop = 'ratingValue')['content']
			allReviews[restaurant].append([content, rating])

		NumReview -= len(reviews)
		pageCount += len(reviews)

fw = open('output.txt','w')
for restaurant in top20Restaurants:
	for review, rating in allReviews[restaurant]:
		fw.write(restaurant + '\t' + review + '\t' + rating + '\n')
fw.close()
