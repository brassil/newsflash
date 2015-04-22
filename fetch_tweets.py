import argparse
import oauth2 as oauth
import urllib2 as urllib
import json
import sys
import csv
import re

# See Assignment 1 instructions for how to get these credentials
access_token_key = "437912738-BIXQU5IwKRPz02pwMQt8aAEQRNJAPRzO1bXZGEHF"
access_token_secret = "1OFsZSI9aEjbtZNu2ztkxSXWFPTF3SpUvWiPp65XpGTgC"

consumer_key = "SyKA1Fy8dtZTLpjDv0baBmDAl"
consumer_secret = "cE1lSybtjPW3UzvMnEJ2xC8uPizCayGjQK73P8rtFiCyGM4X1M"

_debug = 0

oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
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

def fetch_samples():
    url = "https://stream.twitter.com/1.1/statuses/sample.json?language=en"
    parameters = []
    response = twitterreq(url, "GET", parameters)
    for line in response:
        print line.strip()

def fetch_from_manhattan(out_file):
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

    with open(out_file,'w') as f:
        # for line in response:
        #     f.write(line)

        w = csv.writer(f)
        w.writerow(['tweet_id','date','user_id','followers','place','lat',
            'lng','text','source','hashtags','urls','retweet_id'])

        for line in response:
            tweets_info = parse_tweet(line)
            if tweets_info is not None:
                w.writerow(tweets_info[0])
                if tweets_info[1] is not None: w.writerow(tweets_info[1])







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











if __name__ == '__main__':
    fetch_from_manhattan(sys.argv[1])    
















