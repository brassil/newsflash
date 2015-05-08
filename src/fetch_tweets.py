#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import argparse
import oauth2 as oauth
import urllib2 as urllib
import json
import sys
import csv
import re
from os import path
import pickle

from newsflash import Newsflash, parse_tweet, compute_rankings
from tokenizer import Tokenizer

# See Assignment 1 instructions for how to get these credentials
access_token_key = "602261126-aEYMLujye1c9wBgWma3iEFCXLLsVHjYPyKp5oxxM"
access_token_secret = "5q1T16Y2cnqj3MBp9T5t0nHsw9L8mirgUcbLBwYjauHN7"

consumer_key = "vuTIHbQAQLeMKtq4XlEKAeik9"
consumer_secret = "rLDfV62htmmn02uNcNhxBZhQiMlGYpp4lBQyT569j1vmQhnVTr"

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
        w = csv.writer(f)
        w.writerow(['tweet_id','date','user_id','followers','place','lat',
            'lng','text','source','hashtags','urls','retweet_id'])

        for line in response:
            tweets_info = parse_streaming_tweet(line)
            if tweets_info is not None:
                w.writerow(tweets_info[0])
                if tweets_info[1] is not None: w.writerow(tweets_info[1])


def run_newsflash(nf_pickle_file):
    '''
    modified version of fetch_from_manhattan; instead of writing to a csv file
    it puts the tweets into the newsflash object and calculates rankings
    '''
    nf = pickle.load(file(nf_pickle_file))

    print 'Newsflash pickle object successfully loaded'

    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    add = '?language=en&locations=-74.12,40.63,-73.68,40.94'
    response = twitterreq((url+add), 'GET', [])

    print 'API call made'

    update = 0

    for line in response:
        tweets_info = parse_streaming_tweet(line)
        if tweets_info is not None:
            update += 1
            sys.stdout.write(' Parsing tweet %d    \r' % (update))
            sys.stdout.flush()

            nf.last_tweet = parse_tweet(nf, tweets_info[0])
            if tweets_info[1] is not None:
                # if it's a retweet, add the original tweet, but DON'T
                # upddate "last tweet" bc it's obv gonna be older
                parse_tweet(nf, tokenizer, tweets_info[1])

        # update every 50 tweets
        if update == 50:
            sys.stdout.write('Recomputing rankings\n')
            update = 0
            rankings = compute_rankings(nf, True)
            for term in rankings[:20]:
                rank = nf.ranks[term]
                print '%s (%d, %f)\t%f' % (term, rank.freq, rank.dfreq, rank.box_size) 
            sys.stdout.write('\n')







if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    option = parser.add_mutually_exclusive_group(required=True)
    option.add_argument('-s', '--stream_to_file', help='Specify output CSV '
        'file to which tweets should be streamed')
    option.add_argument('-p', '--newsflash_pickle', help='Specify newsflash '
        'pickle file to import and continue populating')
    opts = parser.parse_args()

    if opts.stream_to_file:
        fetch_from_manhattan(opts.stream_to_file)

    else:
        p = opts.newsflash_pickle
        if not path.isfile(p):
            sys.exit('ERROR - could not find pickle file at %s.' % p)
        run_newsflash(p)
















