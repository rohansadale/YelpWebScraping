from nltk import word_tokenize
import string

reviews = []
f1 = open('output.txt')
for line in f1:
	restaurant, review, rating = line.rstrip().split('\t')
	if rating in ['1.0', '2.0', '3.0']:
		reviews.append(review)

dictionary = ['suggestion', 'suggest', 'should', 'improve', 'improvement','future','hope','wish']

punctuations = list(string.punctuation)


for review in reviews:
	tokens = word_tokenize(review)
	words = [w.lower() for w in tokens]
	words = [w for w in words if w not in punctuations]
	result = 0
	for target in dictionary:
		if target in words:
			result = 1
	print result
