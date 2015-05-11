

# TODO

oooo look into what happens when a term wiht <50 gets shown o wait jk it wont. but it will if we do a search

the WSHandler has some now-deprecated things in it

### newsflash algorithms

- improve entropic bounding box calculation: make it a little more stochastic than always splitting in the middle. We fixed part of the problem with the lat-long double-check switch but it could be better. Maybe the algo can take in a "thoroughness" level that checks a few options per iteration and chooses the best one
- improve acceleration algo by making it like more frequency graph over time instead of a 24h strict cutoffz
- tokenizer: implement ngrams > 2



# Things to remember
- note the fact that looking exclusively at geo-enabled tweets may introduce a bias.
- tweets.txt has approx 40 tweets per minute
- don't forget that retweeted tweets might appear multiple times in the streaming output csv and therefore other times downstream. 
- remember we haven't done anything about retweets yet, and that could be a useful metric.  
	+ number of RTs should increase the weight of the tweet?
	+ can probably detect rate of increase of RTs also?


# structure

- living dictionary
- adds new things, and deletes anything older than X
- term-centric data structures. distributed content to allow for fastest lookup and smallest storage footprint possible


# ranking metrics 

"term's acceleration and entropic density" lol sounds so flashy

- overall freq of term (just an inverse index basically)
- rate of increase of tweets relating to the term
- our clustering metric for location
	+ keep subdividing, dS tells us about if there are any location hotspots/densities
	+ it can automatically determine size by splitting until entropy doesn't change beyond a certain threshold and then the size is whatever the previous splitting was.


# AB notes 2015-05-06 while making newsflash.py at first



# maps

[printing multiple maps](http://blog.webkid.io/multiple-maps-d3/)



