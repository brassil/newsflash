#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import csv
from collections import defaultdict as ddict
from datetime import datetime
import time
from tokenizer import Tokenizer

'''
does things

created 2015-05-06 02:20h
'''
# punct = {'?','!','.',',','"','...',':','(',')'}
months = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
seconds_per_day = 24*60*60

punct = ''.join(chr(x) for x in range(33,48)+range(58,65)+range(91,97)+range(123,127))
stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
       'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
       'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
       'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
       'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
       'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
       'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and',
       'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at',
       'by', 'for', 'with', 'about', 'against', 'between', 'into',
       'through', 'during', 'before', 'after', 'above', 'below', 'to',
       'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
       'again', 'further', 'then', 'once', 'here', 'there', 'when',
       'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
       'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
       'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
       'just', 'don', 'should', 'now']

stopwords += ["i'm"]


# bounding box for continental US
SW = (24.9493, -125.0011)
NE = (49.5904, -66.9326)



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


def seconds(d):
	'''
	e.g. input d = Wed Apr 22 13:54:11 +0000 2015
	return Unix time seconds
	'''
	d = d.split()
	t = (int(x) for x in d[3].split(':'))

	# datetime obj: year, month num, day; asterisk unpacks tuple
	dt = datetime(int(d[5]), months[d[1]], int(d[2]), *t)

	return time.mktime(dt.timetuple())



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



def trending_location(points):
	'''
	ugh it's not gonna work bc what if a split happens through the middle
	of the cluster? well, at least if we do the entire united states,
	it's less likely to happen? nah it still is bad
	'''
	# format = [[latmin, latmax], [lngmin, lngmax]]
	box = [[SW[0], NE[0]], [SW[1], NE[1]]]
	i = 1 # split on longitude first (0 is lat)

	# only run while the bounding box is > 1 square mile
	while (box[0][1]-box[0][0])*(box[1][1]-box[1][0]) > .0001:
		# print the bounding box
		print [(box[0][0],box[1][0]),(box[0][1],box[1][1])]

		mid = box[i][0] + (box[i][1] - box[i][0]) / 2 

		# less than vs. greater than the mid point
		l = []
		g = []

		for x in points:
			if x[i] < mid:
				l.append(x)
			else:
				g.append(x)

		# now figure out which side has more and if it's a lot more
		# the 2* thing is just a basic idea, prob not what we should
		# use in the end. 
		if len(g) > 2*len(l):
			box[i][0] = mid
			i = (1 if i==0 else 0)
			points = g

		elif len(l) > 2*len(g):
			box[i][1] = mid
			i = (1 if i==0 else 0)
			points = l

		else:
			# it's not a significant change so end it
			break

	# you get here either if the bounding box has become too small,
	# or if we split the box and there was no significant change
	# in size between one and the other side
	return box, len(points)


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
		# all_points = [nf.tweets[tid][1] for tid in tweets]
		# box, num_points = trending_location(all_points)

		'''newyork
		SW corner: 40.63,-74.12
		NE corner: 40.94,-73.68
		'''
		# final_box_area = (box[0][1]-box[0][0]) * (box[1][1]-box[1][0])*3600
		# points_ratio = num_points / float(len(all_points))


		# nf.ranks[term] = (freq, dfreq, final_box_area, points_ratio)
		nf.ranks[term] = (freq,dfreq)


	sorter = lambda x: x[1][0]*(x[1][1]**2) #*(1+x[1][3])
	for term in list(reversed(sorted(nf.ranks.items(), key=sorter)))[:20]:
		all_points = [nf.tweets[tid][1] for tid in tweets]

		print term
		print "---finding bounding box---"
		box, num_points = trending_location(all_points)
		final_box_area = (box[0][1]-box[0][0]) * (box[1][1]-box[1][0])*3600
		points_ratio = num_points / float(len(all_points))
		print









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

	compute_rankings(end, window_in_days)
































if __name__ == '__main__':
	main(sys.argv[1])
