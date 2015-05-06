#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import csv
from collections import defaultdict as ddict
from datetime import datetime
import time

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


class Newsflash:
	def __init__(self):
		# just an inverse index, with list of tweet IDs per term
		# might be good to combine with ranks and add time/location s.t.
		# we're not looking up things as much.
		self.terms = ddict(list) 

		self.ranks = {} # contains ranking tuple per term
		self.tweets = {}

nf = Newsflash()


def reformat_word(word):
	'''
	might replace this w the tokenizer from classification
	'''

	word = word.lower() # convert to lowercase
	if word=='rt': return ''

	# ignore html escapes and urls
	if word.startswith('&') and word.endswith(';'): return ''
	if word.startswith('http'): return ''


	word = word.replace('—','-').replace('–','-') # normalize dashes
	word = word.replace('…','...') # normalize ellipsis
	word = ''.join(x for x in word if x not in punct) # remove punct
	if word in stopwords: return ''

	return word



def parse_tweet(tweet):
	'''
	takes in the tweet as a string. I'm thinking that initializing
	a new CSV reader for each tweet is prob inefficient but idk we'll see

	NOTE that I'm not checking whether a word is in 'stopwords' rn because
	I think that will be too time-intensive. We'll just throw them out later.
	I think this the best way to deal with it but not totally sure.
	'''
	tid = tweet[0]

	words = []
	for w in (reformat_word(x) for x in tweet[7].split()):
		if w != '':
			words.append(w) # add w to list of words in this tweet
			nf.terms[w].append(tid) # add tweet ID to inverse index for w


	# s is UTC seconds
	d = tweet[1].split()
	t = d[3].split(':')
	s = time.mktime(datetime(int(d[5]), months[d[1]], int(d[2]), int(t[0]), int(t[1]), int(t[2])).timetuple())


	# add tweet to tweets dict
	nf.tweets[tid] = [s, (float(tweet[5]),float(tweet[6])), words]

	return tid # maybe shouldn't return anything 



def compute_rankings(end, window):
	print 'end %f window %f' % (end, window)

	for term,tweets in nf.terms.items():
		freq = len(tweets)

		# now calculate the increase / rate of increase of freq somehow.
		# for now, I'll just compare freq in the last day to freq overall
		today_tweets = 0 # number of tweets w/ this term in the last 24h
		for tid in tweets:
			if end - nf.tweets[tid][0] < seconds_per_day: today_tweets += 1

		dfreq = (today_tweets) / (freq/window)

		# now calculate the geography thing



		# finally, update the ranking. for now, without geography,
		# I'm just going to do weight the freq by dfreq (i.e. weight
		# by how much it's being talked about in the last day)
		nf.ranks[term] = (freq,dfreq)

	for term in list(reversed(sorted(nf.ranks.items(), key=lambda x: x[1][0]*x[1][1])))[:20]:
		print term









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
