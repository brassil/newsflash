

# TODO

oooo look into what happens when a term wiht <50 gets shown o wait jk it wont. but it will if we implement a search box

the WSHandler has some now-deprecated things in it



### D3 / UI


- add some options to the UI
	+ e.g. only display terms with accel > 100%? (prob a bad idea idk)
	+ e.g. set a metric for how strongly to weight by acceleration.
- in the top trending terms, you should be able to click an "x" button and it gets added to the stopwords list
	+ I like this esp because then it would sort of help with the annoying duplicate thing with like "new york", "new", and "york".
- if you zoom out of the new york map really far, you can never find it again (could there be a min zoom and/or a reset view button)



### newsflash algorithms

- improve entropic bounding box calculation: 
	+ make it a little more stochastic than always splitting in the middle. We fixed part of the problem with the lat-long double-check switch but it could be better. Maybe the algo can take in a "thoroughness" level that checks a few options per iteration and chooses the best one
	+ also could normalize the box density by comparing freq of Tweets in the box containing a given term vs. the overall freq of all Tweets relating to the term (e.g. is this actually a dense grouping of tweets relating to this term, or is it just because it's in NY and it's densely populated anyways)
- improve acceleration algo by making it like more frequency graph over time instead of a 24h strict cutoffs
- maybe add a boolean somewhere (for each term) that tells you whether the term has been modified since the last Rank calculation. If it hasn't, then you don't need to recalculate it (although I guess some tweets could now be more than 24h ago so its accel would change but idk this might not have to be the case if we change how we calculate accel. )



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




# maps

[printing multiple maps](http://blog.webkid.io/multiple-maps-d3/)



# cool feature

