import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import threading
import time

import oauth2 as oauth
import urllib2 as urllib
import json
import sys
import csv
import re
import os
import argparse

import newsflash as nf


clients = []
'''
TWITTER
'''

# See Assignment 1 instructions for how to get these credentials
access_token_key = "602261126-aEYMLujye1c9wBgWma3iEFCXLLsVHjYPyKp5oxxM"
access_token_secret = "5q1T16Y2cnqj3MBp9T5t0nHsw9L8mirgUcbLBwYjauHN7"

consumer_key = "vuTIHbQAQLeMKtq4XlEKAeik9"
consumer_secret = "rLDfV62htmmn02uNcNhxBZhQiMlGYpp4lBQyT569j1vmQhnVTr"

_debug = 0

oauth_token	= oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
http_method = "GET"

is_trained = False
threads = []

nf_obj = None

http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''
def twitterreq(url, method, parameters):
	req = oauth.Request.from_consumer_and_token(oauth_consumer,
		token=oauth_token, http_method=http_method, http_url=url, 
		parameters=parameters)

	req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

	headers = req.to_header()

	if http_method == "POST":
		encoded_post_data = req.to_postdata()
	else:
		encoded_post_data = None
		url = req.to_url()

	opener = urllib.OpenerDirector()
	opener.add_handler(http_handler)
	opener.add_handler(https_handler)

	response = opener.open(url, encoded_post_data)

	return response




def parse_streaming_tweet(t):
	'''
	For API call, main documentation here:
	https://dev.twitter.com/streaming/reference/post/statuses/filter
	'''
	# don't freak out if JSON conversion fails
	try: t = json.loads(t)
	except: return None

	# don't use if it's not a tweet
	if 'text' not in t.keys(): return None

	# don't use if it doesn't have location
	if t['coordinates'] is None: return None

	# include place if it's available
	if t['place'] is None: place = ''
	else: place = t['place']['full_name'].encode('utf-8')

	# get all the shet
	lng,lat = t['coordinates']['coordinates']
	date = t['created_at'].encode('utf-8')
	tweet_id = t['id_str'].encode('utf-8')
	user_id = t['user']['id_str'].encode('utf-8')
	followers = t['user']['followers_count']
	text = t['text'].encode('utf-8')
	source = re.split('>|<',t['source'].encode('utf-8'))[2]


	# get entity information
	hashtags = t['entities']['hashtags']
	urls = [url['expanded_url'].encode('utf-8') for url in t['entities']['urls']]

	# add the retweeted tweet if this is a retweet
	original = None
	retweet_id = ''
	if 'retweeted_status' in t.keys():
		# this tweet is a retweet
		retweet_id = t['retweeted_status']['id_str'].encode('utf-8')
		original = parse_streaming_tweet(t['retweeted_status'])

	return [tweet_id,date,user_id,followers,place,
			lat,lng,text,source,hashtags,urls,retweet_id], original


def stream_stats(nf_obj):
	sorted_terms = nf_obj.sorted_terms
	top_30_terms, top_30_boxes = nf.get_top_x_terms(sorted_terms, 30, nf_obj)
	stat_data = {'type' : 'top_term_stats', 'stats' : []}
	for term_ind in range(0,len(top_30_terms)):
		term = top_30_terms[term_ind]
		rank = nf_obj.ranks[term]
		stat_data['stats'].append({'term' : term, 'freq' : rank.freq, 
			'dfreq' : rank.dfreq, 'box_size' : rank.box_size, 
			'boxes' : top_30_boxes[term_ind], 
			'tweets' : nf.get_tweets_by_term(nf_obj, term)})
	top_10_links = list(reversed(sorted(nf_obj.urls, 
		key=lambda x: len(nf_obj.urls[x]))))[:10]
	link_data = {'type' : 'top_links', 'links' : [url for url in top_10_links]}
	for client in clients:
		client.write_message(json.dumps(stat_data))
		client.write_message(json.dumps(link_data))


def retrieve_tweets_with_newsflash(nf_obj, source, update_interval):
	thread = threading.current_thread()
	count = 0
	print 'Streaming live Twitter data'
	for tweet in source:
		if thread.stop:
			threads.remove(thread)
			break
		
		# NOTE THAT THIS IGNORES THE ORIGINAL TWEET
		# IN THE CASE OF RETWEETS. this is okay, for now.
		t = parse_streaming_tweet(tweet)
		if t is not None:
			t = t[0]
			count += 1
			sys.stdout.write(' Parsing tweet %d    \r' % (count))
			sys.stdout.flush()

			tweet_json = json.dumps({'type' : 'tweet', 
				'tweet' : {'latitude' : t[5], 
				'longitude' : t[6], 'tid': t[0],
				'text' : t[7]}})

			# now add it to the Newsflash object
			nf.parse_tweet(nf_obj, t)

			for client in clients:
				client.write_message(tweet_json)

			if count == update_interval:
				sys.stdout.write('Recomputing rankings\n')
				count = 0
				nf.compute_rankings(nf_obj)
				stream_stats(nf_obj)
				sys.stdout.write('\n')




def run_newsflash(existing_tweet_corpus, lang, bounding_box, ngrams, update_interval):
	'''
	Get tweets from a file and then stream the API

	chose bounding box by picking points on google maps and then 
	rounding them out

	For Manhattan:
	SW corner: 40.63,-74.12
	NE corner: 40.94,-73.68
	Thus, input bounding_box should be "-74.12,40.63,-73.68,40.94"
	'''
	global nf_obj
	global is_trained

	url = 'https://stream.twitter.com/1.1/statuses/filter.json'
	params = '?language=%s&locations=%s' % (lang, bounding_box)

	nf_obj = nf.train_nf(existing_tweet_corpus, clients, ngrams)
	nf.compute_rankings(nf_obj)
	
	is_trained = True
	for client in clients:
		client.write_message(json.dumps({'type' : 'status', 'status': True }))
	
	stream_stats(nf_obj) # push preliminary (pre-stream) rankings
	
	source = twitterreq((url+params), 'GET', [])
	retrieve_tweets_with_newsflash(nf_obj, source, update_interval)


'''
ASYNCHRONOUS POLLING
'''

class WSHandler(tornado.websocket.WebSocketHandler):

	def check_origin(self, origin):
		return True

	def open(self):
		global clients
		global nf_obj
		global is_trained
		# print 'New connection' ----- interferes with printing percent complete
		clients.append(self)
		if is_trained:
			stream_stats(nf_obj)
		else:
			self.write_message(json.dumps({'type':'status', 'status':False }))
	
	def on_message(self, message):
		data = json.loads(message.encode('utf-8'))
		if (data['type'] == 'get_tweet_text'):
			self.write_message(json.dumps({'type' : 'tweet_text',
				'tweet_text' : nf_obj.tweets[data['tid']].text }))


	def on_close(self):
		global threads
		clients.remove(self)
		# print 'Connection closed'



application = tornado.web.Application([(r'/ws', WSHandler),])

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--tweet_file', required=True, help='Path to a '
		'CSV file containing existing tweet data on which to train the '
		'Newsflash model before live streaming begins.')
	parser.add_argument('-n', '--ngrams_max', required=False, type=int, 
		default=1, help='Maximum ngrams to parse from tweet text, e.g. for n=2,'
		' Newsflash collects unigrams and bigrams. Default=1 (unigrams only).')
	parser.add_argument('-l', '--lang', required=False, default='en',
		help='Tweet language (two-letter code). Default = en (English).')
	parser.add_argument('-i', '--update_interval', required=False, type=int,
		default=50, help='Number of Tweets to stream before recomputing term '
		'ranks. Default = 50.')
	location = parser.add_mutually_exclusive_group(required=True)
	location.add_argument('-m', '--manhattan', action='store_true', 
		help='Set Tweet bounding box to the greater Manhattan area.')
	location.add_argument('-u', '--united_states', action='store_true',
		help='Set Tweet bounding box to the coninental United States.')
	location.add_argument('-b', '--bounding_box', type=float, nargs='+',
		help='Custom bounding box. Enter coordinates in the following order: '
		'SW corner long, SW corner lat, NE corner long, NE corner lat.')
	opts = parser.parse_args()

	if not os.path.isfile(opts.tweet_file):
		sys.exit('error: could not find a data file at %s' % opts.tweet_file)
	if opts.ngrams_max < 1 or opts.ngrams_max > 5:
		sys.exit('error: ngrams input must be a valid integer in [1,5]')
	if opts.lang and len(opts.lang) != 2:
		sys.exit('error: Tweet language must be a two-letter language code')

	if opts.manhattan:
		bounding_box = (-74.12, 40.63, -73.68, 40.94)
	elif opts.united_states:
		bounding_box = (-125.00, 24.94, -66.93, 49.59)
	else:
		if len(opts.bounding_box) != 4:
			sys.exit('error: 4 coordinates are needed to create bounding box')
		else:
			bounding_box = opts.bounding_box
	bounding_box = ','.join(str(x) for x in bounding_box)

	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
	try:
		# orig: (target=stream_tweets, args=('newsflash',train_file,directory))
		t = threading.Thread(target=run_newsflash, 
							 args=(opts.tweet_file, opts.lang, 
							 	bounding_box, opts.ngrams_max, 
							 	opts.update_interval))
		threading.Thread.stop = False
		t.start()
		t.stop = False
		threads.append(t)
		tornado.ioloop.IOLoop.instance().start()
	except KeyboardInterrupt:
		for thread in threads:
			thread.stop = True
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
