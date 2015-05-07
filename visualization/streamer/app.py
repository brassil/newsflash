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

def fetch_from_manhattan():
	'''
	main documentation here:
	https://dev.twitter.com/streaming/reference/post/statuses/filter
	
	chose bounding box by picking points on google maps and then 
	rounding them out

	SW corner: 40.63,-74.12
	NE corner: 40.94,-73.68
	'''

	url = 'https://stream.twitter.com/1.1/statuses/filter.json'
	add = '?language=en&locations=-74.12,40.63,-73.68,40.94'
	response = twitterreq((url+add), 'GET', [])

	for line in response:
		tweets_info = parse_tweet(line)
		if tweets_info is not None:
			print tweets_info
			
			for client in clients:
				client.write_message(json.dumps({'latitude' : tweets_info[0][5], 'longitude' : tweets_info[0][6], 'tweet' : tweets_info[0][7]}))


def parse_tweet(t):
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
		original = parse_tweet(t['retweeted_status'])

	return [tweet_id,date,user_id,followers,place,lat,lng,text,source,hashtags,urls,retweet_id], original


'''
ASYNCHRONYS POLLING
'''

class WSHandler(tornado.websocket.WebSocketHandler):

	
	def check_origin(self, origin):
		return True

	def open(self):
		global isFirst
		global clients
		print 'new connection'
		clients.append(self)
		if isFirst:
			t = threading.Thread(target=fetch_from_manhattan)
			t.start()
			self.isFirst = False
	
	def on_message(self, message):
		print 'message received %s' % message

	def on_close(self):
		clients.remove(self)
		if len(clients) == 0:
			isFirst = True
		print 'connection closed'

application = tornado.web.Application([(r'/ws', WSHandler),])


if __name__ == "__main__":
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
