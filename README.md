

# Things to remember

- note the fact that looking exclusively at geo-enabled tweets may introduce a bias.

- tweets.txt has approx 40 tweets per minute




# structure

living dictionary

adds new things, and deletes anything older than X

build it based on words.

need to have a sort of "significance" metric for a given term. It must be weighted by:

- overall freq of term (just an inverse index basically)
- rate of increase of tweets relating to the term
- our clustering metric for location
	+ keep subdividing, dS tells us about if there are any location hotspots/densities
	+ it can automatically determine size by splitting until entropy doesn't change beyond a certain threshold and then the size is whatever the previous splitting was.


# AB notes 2015-05-06 while making newsflash.py at first

- remember we haven't done anything about retweets yet, and that could be a useful metric.  
	+ number of RTs should increase the weight of the tweet
	+ can probably detect rate of increase of RTs also

- important, should deal with AT_USER and URL better, they are p relevant. but should also not be classified the same as other terms? should maybe use the additional data I added (links and such) in the tweets


__problem with the geography clustering thing we do:__ what if the big cluster is right in the middle? then it's not going to come up as significant
