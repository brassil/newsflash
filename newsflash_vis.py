#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import csv
from collections import defaultdict as ddict

from tokenizer import Tokenizer
from seconds import seconds
from place import trending_location

'''
does things

created 2015-05-06 02:20h
'''




seconds_per_day = 24*60*60


class Newsflash:
	def __init__(self):
		# just an inverse index, with list of tweet IDs per term
		# might be good to combine with ranks and add time/location s.t.
		# we're not looking up things as much.
		self.terms = ddict(list) 

		self.ranks = {} # contains ranking tuple per term
		self.tweets = {}

nf = Newsflash()
tokenizer = Tokenizer()





def parse_tweet(t):
	'''
	takes in the tweet as a string. I'm thinking that initializing
	a new CSV reader for each tweet is prob inefficient but idk we'll see
	'''
	tid = t[0]

	words = tokenizer.tokenize(t[7])
	for word in words: nf.terms[word].append(tid) # add to inverse index

	
	# loc = np.array((t[5],t[6]), dtype=float)
	loc = (float(t[5]), float(t[6]))
	nf.tweets[tid] = [seconds(t[1]), loc, words]

	return tid # maybe shouldn't return anything but for now it's necessary



def compute_rankings(end, window):
	print 'end %f window %f' % (end, window)

	for term,tweets in nf.terms.items():
		freq = len(tweets)

		# now calculate the increase / rate of increase of freq somehow.
		# for now, I'll just compare freq in the last day to freq overall
		today_tweets = 0 # number of tweets w/ this term in the last 24h
		for tid in tweets:
			if end - nf.tweets[tid][0] < seconds_per_day: today_tweets += 1

		dfreq = today_tweets / (freq/window)

		# now calculate the geography thing
		all_points = [nf.tweets[tid][1] for tid in tweets]
		box, size, num_points = trending_location(all_points)
		points_ratio = num_points / float(len(all_points))

		# size is the distance between two corners of the box
		# --- remove size and points ratio --- nf.ranks[term] = (freq, dfreq, size, points_ratio)
		nf.ranks[term] = (freq, dfreq)


	sorter = lambda x: x[1][0]*(x[1][1]**2) # *(1+x[1][3])
	return list(reversed(sorted(nf.ranks.items(), key=sorter)))[:20]



def main(tweet_data_file):
	# initialize things -- later we will read from tweets in real 
	# time but rn it's a static file
	with open(tweet_data_file) as f:
		r = csv.reader(f)
		next(r, None) # eliminate header row
		first_tweet = parse_tweet(next(r, None)) # catch first tweet so you can get its timestamp

		last_tweet = None
		for row in r: last_tweet = parse_tweet(row)


	# define time window (it should be dynamic but not rn)
	start = nf.tweets[first_tweet][0]
	end = nf.tweets[last_tweet][0]
	window_in_days = (end-start)/3600/24

	top_20 = compute_rankings(end, window_in_days)
	for term in top_20:
		all_points = [nf.tweets[tid][1] for tid in tweets]
		box, size, num_points, all_boxes = trending_location(all_points)
			for box in all_boxes:
				#do shit here with the boxes (like stream to vis)
		points_ratio = num_points / float(len(all_points))
















if __name__ == '__main__':
	main(sys.argv[1])
