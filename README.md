

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