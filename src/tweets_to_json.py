import csv
import sys
import numpy as np
from numpy import genfromtxt

def main(file, out):
	tweets = np.array([])
	with open(file, 'r') as f:
		tweetreader = csv.reader(f)
		next(tweetreader, None)  # skip the headers
		tweets_doc = list(tweetreader)
		tweets = np.array(tweets_doc)
		
	with open(out, 'w') as f:
		coord_writer = csv.writer(f)
		coord_writer.writerow(['1', '0', 'time'])
		for tweet in tweets:
			coord_writer.writerow([tweet[5], tweet[6], tweet[1]])

if __name__ == "__main__":
	file = sys.argv[1]
	out = sys.argv[2]
	main(file, out)