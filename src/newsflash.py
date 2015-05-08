#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import csv
from collections import defaultdict
import pickle

from tokenizer import Tokenizer
from seconds import seconds
from place import trending_location, get_corners

'''
does things

created 2015-05-06 02:20h
'''


class Newsflash:
	def __init__(self):
		# just an inverse index, with list of tweet IDs per term
		# might be good to combine with ranks and add time/location s.t.
		# we're not looking up things as much.
		self.terms = defaultdict(list) 

		self.ranks = {} # contains ranking tuple per term
		self.tweets = {}


		self.first_tweet = None
		self.last_tweet = None


def remove_old(nf):
	'''
	remove all tweets older than X days?
	'''
	pass



def get_tweets_by_term(nf, term):
	'''
	returns a 2-tuple with the following two elements:
	- box = bounding box for this term. box is a list of 2-tuples, where each
			2-tuple is (lat,lon) for the SW, NW, NE, and SE corners (in that
			order, s.t. the list has length 4)
	- tweets = list of tweets containing term. Each element in the list is a
			   2-tuple, with elements (location, text). location is a 2-tuple 
			   (lat,lon); text is a str with the text of the tweet.
	'''

	if len(nf.ranks) == 0:
		e = 'ERROR - rankings have not been calculated yet'
		sys.stderr.write(e+'\n')
		return [e]

	# nf.ranks[term] = (freq, dfreq, box, size, corners)
	box = get_corners(nf.ranks[term][2])
	tweets = []
	for tid in nf.terms[term]:
		t = nf.tweets[tid]
		tweets.append(t[1],t[3])

	return (box, tweets)




def find_related_tweets(nf, terms):
	'''
	takes in the top n terms and tries to find groups of related tweets
	at first we're using 100 but this can be changed
	'''
	level = 10 # go 10 deep before we stop

	explored_tweets = []








def parse_tweet(nf, tokenizer, t):
	'''
	takes in the tweet as a string. I'm thinking that initializing
	a new CSV reader for each tweet is prob inefficient but idk we'll see
	'''
	tid = t[0]

	words = tokenizer.tokenize(t[7])
	for word in words: nf.terms[word].append(tid) # add to inverse index

	
	# loc = np.array((t[5],t[6]), dtype=float)
	loc = (float(t[5]), float(t[6]))
	nf.tweets[tid] = (seconds(t[1]), loc, words, t[7])
	# nf.tweets[tid] = (seconds(t[1]), loc) # don't include tweet text content in the tweets dict

	return tid # maybe shouldn't return anything but for now it's necessary



def compute_rankings(nf):
	start = nf.tweets[nf.first_tweet][0]
	end = nf.tweets[nf.last_tweet][0]
	window = (end-start)/86400 # seconds per day = 86,400

	print 'tweet collection window = %f days' % window

	for term,tweets in nf.terms.items():
		freq = len(tweets)

		# now calculate the increase / rate of increase of freq somehow.
		# for now, I'll just compare freq in the last day to freq overall
		today_tweets = 0 # number of tweets w/ this term in the last 24h
		for tid in tweets:
			if end - nf.tweets[tid][0] < 86400: today_tweets += 1 # seconds per day = 86,400

		dfreq = today_tweets / (freq/window)

		# now calculate the geography thing
		all_points = [nf.tweets[tid][1] for tid in tweets]
		box, size, num_points, corners = trending_location(all_points)
		today_points_ratio = num_points / float(len(all_points))
		

		# size is the distance between two corners of the box
		nf.ranks[term] = (freq, dfreq, box, size, corners)


	sorter = lambda x: x[1][0]*(x[1][1]**2) # *(1+x[1][3])
	sorted_rankings = list(reversed(sorted(nf.ranks.items(), key=sorter)))

	find_related_tweets(nf, [x[0] for i,x in enumerate(sorted_rankings) if i<100])

	# code for the visual bounding box animation
	top_20 = sorted_rankings[:20]
	top_corners = []
	for term in top_20:
		top_corners.append(term[4]) # 5th index is corners
		print str(term)+'\t%f' % term[3] # 4th index is size

	return (top_20, top_corners)



def get_top_terms_boxes(tweet_data_file, pickle_file=None):
	nf = Newsflash()
	tokenizer = Tokenizer()

	# initialize things -- later we will read from tweets in real 
	# time but rn it's a static file
	with open(tweet_data_file) as f:
		r = csv.reader(f)
		next(r, None) # eliminate header row

		# need to catch first tweet for its timestamp
		nf.first_tweet = parse_tweet(nf, tokenizer, next(r, None))

		for row in r: nf.last_tweet = parse_tweet(nf, tokenizer, row)

	top_20, top_corners = compute_rankings(nf)

	if pickle_file:
		pickle.dump(nf, file(pickle_file, 'w'))

	return (top_20, top_corners)


def main(tweet_data_file, pickle_file=None):
	get_top_terms_boxes(tweet_data_file, pickle_file)


if __name__ == '__main__':
	if len(sys.argv) == 2:
		main(sys.argv[1])
	elif len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		sys.exit('Usage: ./newsflash.py <tweet_data_file> [<pickle_file>]')

