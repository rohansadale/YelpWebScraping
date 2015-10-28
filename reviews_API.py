import yelp
import sys
from bs4 import BeautifulSoup
import requests

reload(sys)
sys.setdefaultencoding("utf-8")


CONSUMER_KEY = 'fjsrpoOFALWvCQydOw6FyA'
CONSUMER_SECRET = 'oUrEbZtfjGBk5travjL47n4Gcd4'
TOKEN = 'COLiP9mPx2mzYxlgeWo4UNz420tcAwah'
TOKEN_SECRET = 'noStqU0FQ8Glzg0V7VEW2GDpatw'

yelp_api = yelp.Api(consumer_key=CONSUMER_KEY,
                    consumer_secret=CONSUMER_SECRET,
                    access_token_key=TOKEN,
                    access_token_secret=TOKEN_SECRET)

top20Chinese = yelp_api.Search(term="restaurant", location="Minneapolis", sort = 2, limit = 20, category_filter = 'chinese')

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
