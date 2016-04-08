




for tomorrow:

have all the text of the algorithmic side

and/or pseudocode slash code


# the Newsflash paradigm

In the original conception of this project, we were back and forth on whether or not the content should be populated in real time or by loading a file containing pre-streamed Tweet data. In addition to making testing easier, working from files means that large quantities of tweets can be kept in advance, providing much more data to work with than a live feed (in particular with respect to time). Still, it is both informative and viscerally satisfying to analyze how new data coming in live affects the trends.

Therefore, we devised a solution that takes advantage of both sides. We developed a script to stream live tweets, constrained by language and location, to file. While the Newsflash web application provides the user with choices, the default behavior is to populate its data structures with existing Tweet data and then continue to update its model with a live stream. 

To maintain term frequency baselines that are as "current" as possible, Tweets older than a specified age are discarded; our current operating window when looking exclusively at the Manhattan area is seven days. Of course, this measure also serves to prevent the usage of too much disk space.

Given the massive amount of data necessary to make powerful insight, we spent a great deal of time on optimization. We implemented several paradigms for the Newsflash data structures and chose the most space-efficient, finding that a lean object-oriented representation was about 25% more space-efficient than an array representation, and about 75% more space-efficient than a hashtable representation. We also rigorously time-optimized each step of the process of parsing and tokenizing Tweets, decreasing runtime by 40% from our initial implementation.

Ultimately, our algorithm can process about 5,000 tweets per second, using less than 3kb to store all necessary information. 


# bounding box calculation

Topics trend in time and in space. We developed an algorithm to test for a clustered vs. distributed distribution of Tweets relating to a term. Given the computational expense of most clustering algorithms, it would not be feasible to perform such analyses on thousands of terms, each of which may be linked to tens or hundreds of Tweets. We derived a simple, greedy algorithm that calculates a bounding box for a given term which captures a maximally dense area of Tweets relating to the term, derived from the concept of entropic decision trees. In principle, the algorithm repeatedly makes latitudinal and longitudinal cuts to the bounding box until further subdivisions would no longer result in a significant decrease in entropy. We provide simplified pseudocode below:

```python
def trending_location(term):
	points = [tweets[tweetID].location for tweetID in terms[term].tweets]
	i = 1 # splitting on latitude or longitude
	end = False # flag for system to avoid spurious premature ending

	# initial bounding box = continental US.
	# e.g. south = the southernmost latitude in the continental US
	box = [ [south, north], [west, east] ]

	while area(box) > threshold:
		midpoint = box[i][0] + (box[i][1] - box[i][0]) / 2

		less = []
		greater = []

		for point in points:
			if point[i] < midpoint:
				less.append(point)
			else:
				greater.append(point)


		if less has many more points than greater:
			end = False
			box[i][0] = midpoint
			i = (1 if i==0 else 0)
			points = greater

		else if greater has many more points than less:
			end = False
			box[i][1] = midpoint
			i = (1 if i==0 else 0)
			points = less

		else:
			if not end:
				end = True
				i = (1 if i==0 else 0)
			else:
				break

		return box
```

Thus, terms trending in a specific state (or city) will have small (or smaller) bounding boxes, whereas terms trending across the US will have enormous ones. Interestingly, with sufficient Tweet density, this algorithm gives an extremely high resolution. For example, given a large sample of Tweets from the greater Manhattan area, bounding boxes for 'brooklyn', 'union squar' (stemmed bigram), and the 'park' recapitulate the locations referred to by thosse terms because of the frequency with which users tweet about their current location and activities.




# Trending terms

We have implemented several metrics to determine the strength of trending terms, the simplest of which is term frequency. Currently, the Newsflash web application is static with respect to how it sorts term "trendiness", but the final implementation will allow users to choose and weight the criteria that determine term significance. 

While bounding box area and clustering density, and are useful, we are particularly interested in topics that are _trending now_. The absolute frequency of a term is much less important than a dramatic increase in its frequency. 


- content extraction (building the nf data structures)
- clustering of tweets using the bounding box algorithm -- incl pseudocode
- putting that together to determine term significance.  -- mayb incl pseudocode




the model refreshes as new information arrives. 
to run the server, in src:
python app.py ../data/tweets/
python server.py

go to localhost:5000/bound


if not quitting, do `ps` to get pids of running processes, then `kill -9 pid`


tbt and nj have wrong ass bounding boxes






