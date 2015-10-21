from bs4 import BeautifulSoup
import requests
from pprint import pprint
import json


def fetchPage():

	url = "http://www.yelp.com/locations"
	response = requests.get(url).text
	return response


def scrapeData():

	soup = BeautifulSoup(fetchPage(), 'html.parser')
	
scrapeData()
	
