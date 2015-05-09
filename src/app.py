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
isFirst = True

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

directory = "/"
train_file = 'us_tweets.txt'

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

#once source is defined in the stream_tweets thread, iterate over the source and stream them
def retrieve_tweets(source, mode):
	thread = threading.current_thread()
	for tweet in source:
		if thread.stop:
			threads.remove(thread)
			break
		tweets_info = None
		if (mode == 'live'):
			tweets_info = parse_streaming_tweet(tweet)
		if (mode == 'file'):
			tweets_info = [tweet]

		if tweets_info is not None:
			print {'type' : 'tweet', 'tweet' : {'latitude' : tweets_info[0][5], 
					'longitude' : tweets_info[0][6], 'tweet' : tweets_info[0][7], 
					'time' : tweets_info[0][1], 'location': tweets_info[0][4]}}
			if mode == 'file':time.sleep(2)
			for client in clients:
				client.write_message(json.dumps({'type' : 'tweet', 
					'tweet' : {'latitude' : tweets_info[0][5], 
					'longitude' : tweets_info[0][6], 'tweet' : tweets_info[0][7], 
					'time' : tweets_info[0][1], 'location': tweets_info[0][4]}}))


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
	top_10_links = list(reversed(sorted(nf_obj.urls, key=lambda x: len(nf_obj.urls[x]))))[:10]
	link_data = {'type' : 'top_links', 'links' : [link for link in top_10_links]}
	for client in clients:
		client.write_message(json.dumps(stat_data))
		client.write_message(json.dumps(link_data))


def retreive_tweets_with_newsflash(nf_obj, source, update):
	thread = threading.current_thread()
	count = 0
	print "Retrieving from source:"
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

			if count == update:
				sys.stdout.write('Recomputing rankings\n')
				count = 0
				nf.compute_rankings(nf_obj)
				stream_stats(nf_obj)
				sys.stdout.write('\n')



def analyze_file(data_file, directory):
	nf_obj = nf.train_nf(directory+data_file)
	sorted_terms = nf.compute_rankings(nf_obj)
	top_20_terms, top_20_boxes = nf.get_top_x_terms(sorted_terms, 20, nf_obj)
	stat_data = {'type' : 'top_term_stats', 'stats' : []}
	for term_ind in range(0,len(top_20_terms)):
		term = top_20_terms[term_ind]
		rank = nf_obj.ranks[term]
		stat_data['stats'].append({'term' : term, 'freq' : rank.freq, 
			'dfreq' : rank.dfreq, 'box_size' : rank.box_size, 
			'boxes' : top_20_boxes[term_ind], 
			'tweets' : nf.get_tweets_by_term(nf_obj, term)})
	top_10_links = list(reversed(sorted(nf_obj.urls, key=lambda x: len(nf_obj.urls[x]))))[:10]
	link_data = {'type' : 'top_links', 'links' : [link for link in top_10_links]}
	for client in clients:
		print stat_data
		print link_data
		client.write_message(json.dumps(stat_data))
		client.write_message(json.dumps(link_data))


def stream_tweets(mode='live', data_file=None, data_dir=None):
	'''
	Get tweets either from a file or from the API.

	For API call, main documentation here:
	https://dev.twitter.com/streaming/reference/post/statuses/filter
	
	chose bounding box by picking points on google maps and then 
	rounding them out

	SW corner: 40.63,-74.12
	NE corner: 40.94,-73.68
	'''
	global nf_obj
	global is_trained
	source = None
	url = 'https://stream.twitter.com/1.1/statuses/filter.json'
	add = '?language=en&locations=-74.12,40.63,-73.68,40.94'

	#if the thread has been started with the LIVE mode specified
	if (mode == 'live'):
		print "--- SWITCHING TO LIVE MODE ---"
		source = twitterreq((url+add), 'GET', [])
		retrieve_tweets(source, mode)

	#if the thread has been started with the FILE mode specified
	elif (mode == 'file'):
		if data_file is None: sys.exit('ERROR: data file is None')

		print "--- SWITCHING TO FILE MODE ---"
		with open(os.path.join(data_dir,data_file), 'r') as tweet_file:
			source = csv.reader(tweet_file)
			next(source, None)
			retrieve_tweets(source, mode)

	elif (mode == 'newsflash'):
		print "--- SWITCHING TO LIVE MODE WITH NEWSFLASH OBJECT DATA ---"
		if data_file is None: sys.exit('ERROR: data file is None')
		
		print "Training Newsflash object"
		nf_obj = nf.train_nf(os.path.join(data_dir,data_file))
		print "Calculating preliminary rankings"
		nf.compute_rankings(nf_obj)
		is_trained = True
		for client in clients:
			client.write_message(json.dumps({'type' : 'status', 'status': True }))
		stream_stats(nf_obj)
		print "Begin streaming live data"
		source = twitterreq((url+add), 'GET', [])

		retreive_tweets_with_newsflash(nf_obj, source, 50)


	else:
		print "ERROR: invalid mode requested!"



def parse_streaming_tweet(t):
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

    return [tweet_id,date,user_id,followers,place,lat,lng,text,source,hashtags,urls,retweet_id], original

'''
ASYNCHRONOUS POLLING
'''

class WSHandler(tornado.websocket.WebSocketHandler):

	
	def check_origin(self, origin):
		return True

	def open(self):
		global isFirst
		global clients
		global directory
		global nf_obj
		global is_trained
		print 'new connection'
		self.write_message(json.dumps({'type' : 'files', 
			'files' : os.listdir(directory)}))
		clients.append(self)
		if is_trained:
			stream_stats(nf_obj)
		else:
			self.write_message(json.dumps({'type' : 'status', 'status': False }))
	
	def on_message(self, message):
		global directory
		data = json.loads(message.encode('utf-8'))
		if (data['type'] == 'mode_change'):
			for thread in threads:
				thread.stop = True
			args = ()
			results = []
			target = stream_tweets
			if (data['details']['mode'] == 'file'):
				console.log('FILE');
				args=('file', data['details']['file'], directory)
			elif (data['details']['mode'] == 'analyze'):
				args = (data['details']['file'], directory)
				target = analyze_file
			t = threading.Thread(target=target, args=args)
			threading.Thread.stop = False
			t.stop = False
			threads.append(t)
			t.start()
		elif (data['type'] == 'get_tweet_text'):
			self.write_message(json.dumps({'type' : 'tweet_text',
				'tweet_text' : nf_obj.tweets[data['tid']].text }))


	def on_close(self):
		global threads
		clients.remove(self)
		print 'connection closed'

application = tornado.web.Application([(r'/ws', WSHandler),])


if __name__ == "__main__":
	directory = sys.argv[1]
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
	try:
		t = threading.Thread(target=stream_tweets, args = ('newsflash', train_file, directory))
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
