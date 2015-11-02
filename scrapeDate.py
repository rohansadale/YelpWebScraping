import sys
from bs4 import BeautifulSoup
import requests
from pprint import pprint
import time
import argparse

reload(sys)
sys.setdefaultencoding("utf-8")



def scrapeDate(restaurantIDs):
	reviewStartDates= []
	count = 0

	for restaurantID in restaurantIDs:
		url = 'http://www.yelp.com/biz/' + restaurantID + '?sort_by=date_asc'
		html = requests.get(url).text
		soup = BeautifulSoup(html,'html.parser')
		reviews = soup.findAll('div', {'class' : 'review-content'})
		if len(reviews) != 0:
			date = reviews[0].find('meta',  itemprop = 'datePublished')['content']
		else:
			date = '99999'
		reviewStartDates.append(restaurantID + '|' + date)
		count += 1
		print restaurantID	
		if count%20 == 0:
			time.sleep(4)
	return reviewStartDates


if __name__ == '__main__':
	parser = argparse.ArgumentParser();
	parser.add_argument('-f', '--fileName', dest='fileName', type=str, help='input file with restaurantIDs', required=True)
	inputValues = parser.parse_args()

	restaurantIDs = []
	with open(inputValues.fileName) as f:
		restaurantIDs = f.read().splitlines()

	reviewStartDates = scrapeDate(restaurantIDs)
	
	with open('output/firstReviewDate.csv', 'wb') as f:
		for item in reviewStartDates:
			f.write(item + '\n')
