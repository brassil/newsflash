import argparse
import oauth2 as oauth
import urllib2 as urllib
import json
import sys
import csv

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
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    params = '?track=twitter&locations=-122.75,36.8,-121.75,37.8'
    response = twitterreq(url+params, 'GET', [])

    with open(out_file,'w') as f:
        for line in response: f.write(line)



if __name__ == '__main__':
    fetch_from_manhattan(sys.argv[1])    
