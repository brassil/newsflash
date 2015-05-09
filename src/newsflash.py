#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import csv
from collections import defaultdict
import pickle
from ast import literal_eval
import time

from tokenizer import Tokenizer
from seconds import seconds
from place import trending_location, get_corners

'''
does things

created 2015-05-06 02:20h
'''


class Newsflash:
	def __init__(self):
		self.tokenizer = Tokenizer()

		# just an inverse index, with list of tweet IDs per term
		# might be good to combine with ranks and add time/location s.t.
		# we're not looking up things as much.
		self.terms = defaultdict(list) 

		self.ranks = {} # contains ranking tuple per term
		self.tweets = {}
		self.sorted_terms = None


		self.first_tweet = None
		self.last_tweet = None


		self.urls = defaultdict(list)


class Tweet:
	def __init__(self, time, loc, text): # words
		self.time = time # float (I think), Unix time, seconds
		self.loc = loc # 2-tuple (lat,lon), each is a float
		# self.words = words # set of tokenized terms in the tweet
		self.text = text # raw text of the tweet


class Rank:
	def __init__(self, freq, dfreq, box, box_size, corners):
		self.freq = freq # number of tweets containing this term
		self.dfreq = dfreq # relative rate of related tweets (last 24h vs. overall)
		self.box = box # bounding box [[minlat, maxlat], [minlon,maxlon]]
		self.box_size = box_size # distance between two far corners of the bounding box

		# list of corners, progressively zooming in to display the process
		# of the trending_location function. each corner is a lisf of 4 
		# 2-tuples (lat,lon), with the order SW, NW, NE, SE
		# don't necessarily need this, progression of zooming in bounding box
		self.corners = corners






def remove_old(nf):
	'''
	remove all tweets older than X days
	'''
	about_a_week_ago = nf.tweets[nf.last_tweet].time - 86400*7

	for tid in nf.tweets:
		if nf.tweets[tid].time < about_a_week_ago:
			# remove tweet ID from all terms (inv index)
			for w in nf.tokenizer.tokenize(nf.tweets[tid].text):
				nf.terms[w].remove(tid)

			nf.tweets.pop(tid) # remove tweet entirely

	# update what the oldest tweet in teh collection is
	nf.first_tweet = min(nf.tweets, key=lambda tid: nf.tweets[tid].time)

	# NOT SURE IF WE SHOULD DO THIS NOW, it depends how often
	# we call remove_old and compute_rankings
	compute_rankings(nf) # recompute rankings now





def get_tweets_by_term(nf, term):
	if len(nf.ranks) == 0:
		e = 'ERROR - rankings have not been calculated yet'
		sys.stderr.write(e+'\n')
		return [e] # idk just something in a similar format

	return {'bounding_box' : get_corners(nf.ranks[term].box), 
			'tweets' : [{'location' : nf.tweets[tid].loc,
			'tid' : tid} for tid in nf.terms[term]]}






def find_related_tweets(nf, start_terms):
	'''
	takes in the top n terms and tries to find groups of related tweets
	at first we're using 100 but this can be changed

	YO THIS DOESN'T WORK. after only 3 iterations we've captured almost
	all the terms (i.e. most tweets have <3 degrees of separation)
	'''
	terms = set()
	tweets = set()


	new_terms = set(start_terms)
	new_tweets = set()


	for level in range(3):
		for term in new_terms:
			new_tweets = new_tweets.union(nf.terms[term])

		# only lookup terms in tweets we haven't already looked up
		new_tweets = new_tweets.difference(tweets)
		terms = terms.union(new_terms)
		new_terms = set()

		for tid in new_tweets:
			new_terms = new_terms.union(nf.tweets[tid].words)

		tweets = tweets.union(new_tweets)
		new_tweets = set()

	return terms




def parse_tweet(nf, t, from_file=False):
	'''
	takes in the tweet as a string. I'm thinking that initializing
	a new CSV reader for each tweet is prob inefficient but idk we'll see
	'''
	tid = t[0]

	# words = nf.tokenizer.tokenize(t[7])
	for word in nf.tokenizer.tokenize(t[7], True): #=================================== BIGRAMS INCLUDED
		nf.terms[word].append(tid) # add to inverse index

	# add URLs
	for url in (literal_eval(t[10]) if from_file else t[10]):
		nf.urls[url.lower()].append(tid) # ignore case

	nf.tweets[tid] = Tweet(seconds(t[1]), (float(t[5]), float(t[6])), t[7])

	return tid


'''
Take in the nf object and compute the rankings for all terms in the terms dictionary
Store each term's ranking in the nk.ranks attribute of the nf object
For each term, compute the recursive bounding boxes and store them as a parameter 
of the Ranks object, stored as the Value for the term (Key) in the nk.ranks dictionary
If the return_sorted argument is passed as true, sort the rankings 
and return the terms for the rankings, in order
Otherwise, return None
'''
def compute_rankings(nf):
	start = nf.tweets[nf.first_tweet].time
	end = nf.tweets[nf.last_tweet].time
	window = (end-start)/86400 # seconds per day = 86,400

	ranks = {}
	print 'tweet collection window = %f days' % window

	for term,tweets in nf.terms.items():
		freq = len(tweets)

		# now calculate the increase / rate of increase of freq somehow.
		# for now, I'll just compare freq in the last day to freq overall		
		today_tweets = 0 # number of tweets w/ this term in the last 24h
		for tid in tweets:
			if end - nf.tweets[tid].time < 86400: today_tweets += 1 # seconds per day = 86,400

		dfreq = today_tweets / (freq/window)

		# now calculate the geography thing
		points = [nf.tweets[tid].loc for tid in tweets]

		# if term == 'tbt':
		# 	box, box_size, num_points, corners = trending_location(points, True) # make corners=true otherwise corners will be empty
		# 	print corners
		# 	sys.exit()

		box, box_size, num_points, corners = trending_location(points, False) # make corners=true otherwise corners will be empty
		today_points_ratio = num_points / float(len(points))

		# note that not everything being returned by trending_location
		# is actually given to Rank or even used.
		nf.ranks[term] = Rank(freq, dfreq, box, box_size, corners)


	sorter = lambda x: nf.ranks[x].freq*(nf.ranks[x].dfreq**2) # *(1+x[1][3])
	nf.sorted_terms = list(reversed(sorted(nf.ranks.keys(), key=sorter)))

	# find_related_tweets(nf, [x for i,x in enumerate(sorted_rankings) if i<100])
	return nf.sorted_terms


def print_top_x_links(nf, x):
	print '\nTOP '+str(x)+' links'
	for url in list(reversed(sorted(nf.urls, key=lambda x: len(nf.urls[x]))))[:x]:
		print '%d \t %s' % (len(nf.urls[url]), url)

'''
INPUT: 
	all terms as String of term ranked
	desired number of top results, x
OUTPUT: 
	the top x terms, listed in order
	the bounding boxes, in decreasing size, for the top x terms
'''
def get_top_x_terms(sorted_terms, x, nf):
	#if the number of terms requested is greater than those available
	if x > len(sorted_terms): x = len(sorted_terms)

	topx = sorted_terms[:x]
	return (topx, [nf.ranks[term].corners for term in topx])


def train_nf(tweet_data_file, pickle_file=None):
	nf = Newsflash()
	# initialize things -- later we will read from tweets in real 
	# time but rn it's a static file
	with open(tweet_data_file) as f:
		r = csv.reader(f)
		next(r, None) # eliminate header row

		# need to catch first tweet for its timestamp
		nf.first_tweet = parse_tweet(nf, next(r, None), True)

		t = time.time()

		for row in r: nf.last_tweet = parse_tweet(nf, row, True)
	
	print 'train time: %.1fs' % (time.time() - t)

	if pickle_file:
		pickle.dump(nf, file(pickle_file, 'w'))
	
	return nf



def main(tweet_data_file, pickle_file=None):
	nf = train_nf(tweet_data_file, pickle_file)

	sorted_terms = compute_rankings(nf)
	top_20_terms, top_20_boxes = get_top_x_terms(sorted_terms, 20, nf)
	for term in top_20_terms:
		rank = nf.ranks[term]
		print '%s (%d, %f)\t%f' % (term, rank.freq, rank.dfreq, rank.box_size)
	print_top_x_links(nf, 10)




if __name__ == '__main__':
	if len(sys.argv) == 2:
		main(sys.argv[1])
	elif len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		sys.exit('Usage: ./newsflash.py <tweet_data_file> [<pickle_file>]')
