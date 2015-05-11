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
	def __init__(self, ngrams=1):
		self.tokenizer = Tokenizer(ngrams)
		self.urls = defaultdict(list) # inverse index per URL
		self.terms = defaultdict(list) # inverse index per term (ngram)
		self.tweets = {} # Tweet object per tweet ID
		self.ranks = {} # Rank object per term
		self.sorted_terms = None # term list sorted by decreasing rank

		# first and last (chronological) tweet IDs in the collection
		self.first_tweet = None
		self.last_tweet = None


class Tweet:
	def __init__(self, time, loc, text): # words
		self.time = time # float, Unix time, seconds
		self.loc = loc # 2-tuple (lat,lon), each is a float
		self.text = text # raw text of the tweet
		# self.words = words # set of tokenized terms in the tweet--DEPRECATED


class Rank:
	def __init__(self, freq, dfreq, box, box_size, corners):
		self.freq = freq # absolute term frequency
		self.dfreq = dfreq # term Acceleration
		self.box = box # entropic bounding box [[S, N], [W, E]]
		self.box_size = box_size # SW->NE bounding box distance, mi

		'''FOR TROUBLESHOOTING AND DEMONSTRATIVE PURPOSES ONLY
		list of corners, showing the current bounding box state at each 
		iteration of place.trending_location() as it zooms the box. Can be used
		to visualize the function's process. Each corner is itself a list of 4 
		2-tuples (lat,lon), with the order (SW, NW, NE, SE).
		'''
		self.corners = corners



def remove_old(nf):
	'''
	Remove all tweets older than X days. It's kinda slow because
	it needs to re-tokenize the text in order to find the tid in the
	inverse index (but it's faster than searching through the entire
	inverse index and removing all instances of the tid), but the tradeoff
	is space-efficiency (i.e. you don't have to store that information).
	Since this function won't be called very often, it's better to optimize
	for space bc its amortized runtime is negligible.
	'''
	about_a_week_ago = nf.tweets[nf.last_tweet].time - 86400*7

	for tid in nf.tweets:
		if nf.tweets[tid].time < about_a_week_ago:
			# remove tweet ID from all terms (inv index)
			for w in nf.tokenizer.tokenize(nf.tweets[tid].text):
				nf.terms[w].remove(tid)

			nf.tweets.pop(tid) # remove tweet entirely

	# update the oldest tweet in the collection
	nf.first_tweet = min(nf.tweets, key=lambda tid: nf.tweets[tid].time)

	# compute_rankings(nf) # recompute rankings now, if desired for testing





def get_tweets_by_term(nf, term):
	'''
	INPUT: a term in the collection
	OUTPUT:
		- entropic bounding box for the term as a tuple of corners (SW,NW,NE,SE)
		- list of (location, tweet ID) tuples for all tweets containing the term
	'''
	if len(nf.ranks) == 0:
		e = 'error: rankings have not been calculated yet'
		sys.stderr.write(e+'\n')
		return [e]

	return {'bounding_box' : get_corners(nf.ranks[term].box), 
			'tweets' : [{'location' : nf.tweets[tid].loc, 'tid' : tid} 
				for tid in nf.terms[term]]}



def parse_tweet(nf, t, from_file=False):
	'''
	parses a Tweet in either of the following forms:
		- output from app.parse_streaming_tweet(); from_file=False
		- line from a CSV file (parsed using csv.reader); from_file=True
	
	Performs a number of tokenizing, cleaning, parsing, and stemming operations
	on the Tweet (see tokenizer.py), adds it to the nf collection, and returns 
	the tweet ID.
	'''
	tid = t[0]

	# terms = nf.tokenizer.tokenize(t[7]) # store set of terms --DEPRECATED
	for term in nf.tokenizer.tokenize(t[7]):
		nf.terms[term].append(tid) # add to inverse index

	# add URLs that have been previously scraped & cleaned
	for url in (literal_eval(t[10]) if from_file else t[10]):
		nf.urls[url.lower()].append(tid) # ignore case

	nf.tweets[tid] = Tweet(seconds(t[1]), (float(t[5]), float(t[6])), t[7])

	return tid



def acceleration(tweet_times, freq, start, end, window):
	'''
	original function, 24h acceleration

	Could plot the last X 6 or 12 hr periods?
	tbh 24h is better because it includes a full cycle of day/night
	'''
	today_tweets = 0 # number of tweets w/ this term in the last 24h
	for t in tweet_times:
		if end - t < 86400:
			today_tweets += 1  # seconds per day = 86,400

	dfreq = today_tweets / (freq/window)


	return dfreq





def compute_rankings(nf):
	'''
	Update term rank data: calculate frequency, acceleration, and entropic 
	bounding box. Rank terms using a combined metric.

	OUTPUT: List of all terms in the collection, sorted by rank.
	'''
	start = nf.tweets[nf.first_tweet].time
	end = nf.tweets[nf.last_tweet].time
	window = (end-start)/86400 # seconds per day = 86,400

	ranks = {}
	print 'Computing term ranks'
	print ' -- tweet collection window = %.1f days' % window

	t = time.time()

	for term,tweets in nf.terms.items():
		freq = len(tweets)
		if freq < 50: continue # ignore terms with less than 50 tweets
		
		dfreq = acceleration((nf.tweets[tid].time for tid in tweets), 
			freq, start, end, window)

		# now calculate the bounding box
		points = [nf.tweets[tid].loc for tid in tweets]
		box, box_size, num_points, corners = trending_location(points)
		today_points_ratio = num_points / float(len(points))

		# note that not everything being returned by trending_location
		# is actually given to Rank or even used.
		nf.ranks[term] = Rank(freq, dfreq, box, box_size, corners)

	sorter = lambda x: nf.ranks[x].freq*(nf.ranks[x].dfreq**3) # *(1+x[1][3])
	nf.sorted_terms = list(reversed(sorted(nf.ranks.keys(), key=sorter)))

	print 'Computed rankings in %.1fs' % (time.time() - t)
	return nf.sorted_terms


def print_top_x_links(nf, x):
	print '\nTOP %d links' % x
	for url in list(reversed(sorted(nf.urls, key=lambda x: len(nf.urls[x]))))[:x]:
		print '%d \t %s' % (len(nf.urls[url]), url)


def get_top_x_terms(sorted_terms, x, nf):
	'''
	INPUT: 
		List of all terms (sorted by decreasing rank)
		desired number of top results, x
	OUTPUT: 
		the top x terms, listed in order
		the bounding boxes, in decreasing size, for the top x terms
	'''
	topx = sorted_terms[:x] # if len > x, it will just print the whole list
	return (topx, [nf.ranks[term].corners for term in topx])


def train_nf(tweet_data_file, ngrams=1):
	'''
	initialize nf object -- later we will read from tweets
	in real time but start by populating with a static file.

	'''
	t = time.time()
	print 'training Newsflash object'
	print ' -- maximum ngram = %d' % ngrams
	nf = Newsflash(ngrams)

	# with open(tweet_data_file) as f:
	# 	r = csv.reader(f)
	# 	next(r, None) # eliminate header row
	# 	nf.first_tweet = parse_tweet(nf, next(r, None), True)
	# 	for row in r: nf.last_tweet = parse_tweet(nf, row, True)


	# version that includes progress info
	with open(tweet_data_file,'rU') as f:
		n = sum(1 for _ in f) - 1
		print ' -- %d training tweets' % n
		n /= 100 # convert it to a percent ---- can change this for diff print intervals
		f.seek(0)

		r = csv.reader(f)
		next(r, None) # eliminate header row
		nf.first_tweet = parse_tweet(nf, next(r, None), True)
		
		i = 1 # number of tweets parsed
		p = 0 # percent complete
		for row in r:	
			nf.last_tweet = parse_tweet(nf, row, True)
			i += 1
			if i % n == 0:
				p += 1
				sys.stdout.write(' -- %d%% complete   \r' % p)
				sys.stdout.flush()
	
	print 'train time: %.1fs             ' % (time.time() - t)
	return nf




def main(tweet_data_file, ngrams=1): # pickle_file=None):
	'''
	Option to pickle the resulting nf object for later use
	'''
	nf = train_nf(tweet_data_file, ngrams) #, pickle_file)
	# if pickle_file: pickle.dump(nf, file(pickle_file, 'w'))

	sorted_terms = compute_rankings(nf)
	
	top_30_terms, _ = get_top_x_terms(sorted_terms, 30, nf)
	for term in top_30_terms:
		rank = nf.ranks[term]
		print '%s (%d, %f)\t%f' % (term, rank.freq, rank.dfreq, rank.box_size)
	
	print_top_x_links(nf, 10)



if __name__ == '__main__':
	if len(sys.argv)<2 or len(sys.argv)>3:
		sys.exit('usage: python newsflash.py <tweet_data_file> [<ngrams>]')


	if not os.path.isfile(sys.argv[1]):
		sys.exit('error: could not find a file at %s' % sys.argv[1])

	if len(sys.argv) == 2:
		main(sys.argv[1], 1) # only unigrams by default
	
	else:
		try:
			# make sure ngrams input is a valid integer in a valid range
			ngrams = int(sys.argv[2])
			if ngrams >= 1 and ngrams <= 5: 
				main(sys.argv[1], ngrams)
			else:
				sys.exit('error: ngrams input must be a valid integer in [1,5]')
		except:
			sys.exit('error: ngrams input must be a valid integer in [1,5]')




