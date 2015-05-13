
![](logo.png "NEWSFLASH")

## Motivation

News media has always been a race for first to publication. In the past, publishers had hours or days to track down stories and their sources, check facts, produce written content and go to print. In modern news media, that window for success has shrunk to minutes if not seconds. More so than ever, readers have little loyalty to their source, moving wherever the story first emerges. If the Washington Post gets a push notification out to mobile even a minute before the New York Times, the Times has lost the first mover's advantage; a serious blow to viewership. As the New York Times editor for newsroom strategy says, "Anytime we push our news directly to a user's mobile, we see clicks and swipes skyrocket". And in breaking news you come in either first or last.
						
This rapid ­paced publishing environment presents several challenges. The first and most crucial hurdle is story discovery. Newsrooms sit in the dark, waiting for a lead to come their way. They employ manpower to find stories, scouring Tweets, Facebook posts, police scanners and other information vectors by hand. The publisher that gets lucky gets the scoop. With readers pawing at their lockscreens for whichever push notification pops up first, seconds can make a difference.

The breaking news of the first Ebola diagnosis in the US is a fantastic example of the widening gap between the pace of publication, and the sourcing of news. In this case, a local news station got notice of the Ebola diagnosis first, and Tweeted out the scoop. 

![](poster-ebola-tweet.png "Ebola tweet Houston")

Whichever national publication happened to be following and watching this local Houston news station on Twitter would now get the scoop first. In this case, it wasn't the New York Times or Washington Post but a small startup newsagency. They pushed their story to mobile phones minutes before anyone else, bringing them a substantial advantage in readership. It took hours for the New York Times to break the same story.

![](poster-ebola-nyt.png "Ebola NYT headline")
						
The pressure to write and publish as fast as journalists can source and synthesize often pushes the focus on fact checking to the second tier. The fallback is to publish as little as necessary at first, to get first mover's advantage, and then supplement with more robust material when facts come to light. This leaves a lot to be desired in the context of the typical high quality reporting of publishers like the Times or the Post.
						
Finally, with a story sourced and written, a value must be placed on the story. Does it get pushed to the homepage of the website? Of the app? Does it warrant a push notification? These seemingly small decisions can make all the difference in the success of a story. Bother a user with a useless notification, and you cause annoyance, and in the worst case, a lost subscriber. At the very least, the sorting of stories is an indicator to readers of the priorities of the publisher.
						
The advantages of automating this complex process promises not only faster response time for publishers, but also higher quality, better curated material for readers. In the interest of automatization, we developed Newsflash, a social media analytics platform that identifies the content and location of stories as they emerge in real time.	
				
			
		
## Goals and Outcomes

Newsflash began as a success predictor for stories. That is, once a publication had a story written, they could use our platform to predict how successful the story would be based on the topic. However, our initial research revealed a greater need amongst publishers was identifying stories in the first place so our focus shifted to a platform that combined geolocation and more robust trend detection.

Our first focus was detecting trends in the content of Tweets, and more importantly, trends that are spiking sharply. From our original tests, we found very promising results. Newsflash uses an inverted index of terms and Tweets for fast calculation of baseline frequency as well as rapid changes in frequency.  This inverted index is the core of the Newsflash _acceleration_ algorithm which calculates recent change in frequency of Tweets. 

The top trending topics according to Newsflash's _acceleration_ algorithm are clustered geographically using our iterative bounding box approach. This turned out to be an important but secondary metric in terms of offering meaningful analysis. Geographic clustering was less an indicator of stories in and of themselves than a metric that helped weight how likely a trending term was to represent a story.

Both detection of trending topics and identification of geographic clustering behind terms were successful endeavors in Newsflash. Considering our originally anticipated challenges of merely being able to obtain the necessary data and do simple geographic clustering, we are very happy with Newsflash's progress to date. Our algorithms not only detect trending topics in real time but augment analysis of those terms with a sense of geographic clustering.

Furthermore, this tool is not helpful in any way without an associated user interface, which Newsflash offers as well. Using our application, a user can see trending terms in real time as they adjust to trends. Selecting a term for further analysis displays the geographic clustering of the term as well as the ability to see the content of the Tweets that contributed to the trending topic of interest.

Data Collection
To begin developing the algorithmic backbone of Newsflash, we needed to set of training data. We took advantage of Twitter's Firehose API and the ability to receive only Tweets that were geotagged and fell within a geographic bounding box. For 8 days, we streamed the Firehose with a bounding box surrounding New York City. The Twitter. The goal was to stream long enough to cover significant events happening in New York City that our algorithm could detect. Success of Newsflash would be based on its  ability to sort these specific events out from the noise. One week of data collection yielded a corpus of 500,000 geotagged Tweets with a collective size of about 100 MB. If this data set proved to be statistically sufficient for real-time analysis, we had a benchmark on the rate of Tweets to be analyzed, and the amount memory/disk space those Tweets would require.

## Using Newsflash

We are in the process of preparing Newsflash to run live on the web. Currently, it can be run locally, with a limited set of options available.

To run Newsflash, begin by instantiating an instance of the server:

```bash
python code/server.py
```

Then, the Newsflash application can be started. We recommend the following set of arguments:

```bash
python code/app.py -t data/tweets_nyc_apr26-30.csv -m -i 1000
```

Finally, navigate in your web browser to `localhost:5000/bound`. 

The Newsflash app is set up such that the user can specify one of two preset Tweet collection regions (greater Manhattan area; continental US) or the coordinates for a custom region. We have experimented with multiple maps and Tweet collection regions. However, current limitations on data collection and computation prevent us from being able to offer custom Tweet collection regions. We provide the file `tweets_nyc_apr26-30.csv`, which contains Twitter data from the greater Manhattan area for a period of four days, from 4/26 through 4/30; therefore, please use the bounding box flag `-m`, to live-stream tweets from the same area. For a full list of options, enter: 

```bash
python code/app.py -h
```

Ideally, we'd have constantly updating databases, so that when you start streaming there's no time gap between the last tweet in the training file and the first streaming tweet. Currently, this is not feasible. The other consequence of this is: the initial rank calculation obviously only takes tweets from the file into account. For subsequent term rank calculations, the _acceleration_ metric is incorrect because the only tweets in the last 24 hours are the 50 or so that have just been collected in the time that the app has been running. Therefore, we recommend setting `-i 1000` or some relatively large number, such that the rankings are not recalculated while you explore the app. This means that, while new tweets will be streamed and added to the Newsflash data structures, the term rankings will not actually be updated live. Instead, they will give an accurate picture of what things looked like between April 26-30. Unfortunately, due to the scale of this project, we are unable to have a truly live, time-consistent database. Still, we have shown a proof of concept, and the code base is perfectly ready to support such a database had we the resources to implement one.



## The Newsflash paradigm

In the original conception of this project, we were back and forth on whether or not the content should be populated in real time or by loading a file containing pre-streamed Tweet data. In addition to making testing easier, working from files means that large quantities of tweets can be kept in advance, providing much more data to work with than a live feed (in particular with respect to time). Still, it is both informative and viscerally satisfying to analyze how new data coming in live affects the trends.

Therefore, we devised a solution that takes advantage of both sides. We developed a script to stream live tweets, constrained by language and location, to file. While the Newsflash web application provides the user with choices, the default behavior is to populate its data structures with existing Tweet data and then continue to update its model with a live stream. 

To maintain term frequency baselines that are as "current" as possible, Tweets older than a specified age are discarded; our current operating window when looking exclusively at the Manhattan area is seven days. Of course, this measure also serves to prevent the usage of too much disk space.

Given the massive amount of data necessary to make powerful insight, we spent a great deal of time on optimization. We implemented several paradigms for the Newsflash data structures and chose the most space-efficient, finding that a lean object-oriented representation was about 25% more space-efficient than an array representation, and about 75% more space-efficient than a hash map representation. We also rigorously time-optimized each step of the process of parsing and tokenizing Tweets, decreasing runtime by 40% from our initial implementation.

Ultimately, our algorithm can process about 5,000 tweets per second, using less than 3kb to store all necessary information. 

#### Entropic bounding box calculation

Topics trend in time and in space. We developed an algorithm to test for a clustered versus distributed distribution of Tweets relating to a term. Given the computational expense of most clustering algorithms, it would not be feasible to perform such analyses on thousands of terms, each of which may be linked to tens or hundreds of Tweets. We derived a simple, greedy algorithm that calculates a bounding box for a given term which captures a maximally dense area of Tweets relating to the term, derived from the concept of entropic decision trees. In principle, the algorithm repeatedly makes latitudinal and longitudinal cuts to the bounding box until further subdivisions would no longer result in a significant decrease in entropy. We provide simplified pseudocode below:

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

Thus, terms trending in a specific state (or city) will have small (or smaller) bounding boxes, whereas terms trending across the US will have enormous ones. Interestingly, with sufficient Tweet density, this algorithm gives an extremely high resolution. For example, given a large sample of Tweets from the greater Manhattan area, bounding boxes for 'brooklyn', 'union squar' (stemmed bigram), and the 'park' recapitulate the locations referred to by those terms because of the frequency with which users tweet about their current location and activities.


#### Trending terms and _acceleration_

The signature of an important news story is a surge of data related to the story. We developed a term-wise metric, termed _acceleration_, which computes the recent-to-total term frequency ratio. For a given term, the rate of relevant Tweets accumulated over the last 24 hours is compared to the background rate.

Still, absolute term frequency, bounding box area, and term density all provide valuable information. We sampled a variety of multifeatured vectors by which to weigh terms, and subjectively determined an optimal configuration. We chose not to include any location-related metrics in this calculation; calculated entropic density and other location-based metrics help determine the distribution or source of a term's significance signal, but simply the fact that a term is significant should be agnostic with respect to location.

#### Front-End Interface

The algorithms of Newsflash are of little practical use without a front end interface to allow viewing and analysis by a user. Thus, a large portion of our work focused on providing a useful interface for the user.

Initially, the front end of Newsflash was a tool for use ourselves. We needed to see how our data was grouped geographically, temporally, and by content. We started with a basic map of New York City using D3. We sourced the map from a collection of municipal maps available from the New York City local government. 

![](ny-map.png "NY map")

With this basic map as our front end template, we began to build out the server side of Newsflash. 

## Newsflash Server

The static Newsflash interface is served by a simple HTTP server with details and data communicated over a multithreaded Flask based websocket server making use of the Tornado websockets library. The server is multithreaded to allow new client connections to be detected and handled while the Newsflash model is trained and evaluated in parallel. 

Initially, we made use of the websocket server to replay files of Tweets collected from the Twitter firehose. We used these streams to visualize our data and understand how to best tweak the Newsflash model to glean the most information from our collected Twitter data.

We we gathered a better understanding of our dataset, we reworked our server to provide more useful analytical data. In the final iteration of the Newsflash server, data is continuously extracted from the Newsflash model, such as the live Twitter feed or trending terms, as is transmitted immediately to all connected clients. This enables a far more interactive user experience as new data can be presented  as it becomes available. 


## Newsflash Front End

As we refined our algorithms and server, the Newsflash interface evolved as well. In the final iteration of the Newsflash interface, the following events are communicated between client and server:

- Server status
	+ If the server is currently busy training the model, clients can connect but are displayed a loading screen.
	+ On the loading screen, the percent complete of model training is displayed for the user.
- Live Tweets
	+ As Tweets are collected over the API, their location is passed along to the client for visualization on the map.
- Analytics
	+ The model's ranked terms and associated weights are passed to clients for display. As the model is retrained, updated rankings are passed.
- Tweet content
	+ Any Tweet displayed in the browser has its Tweet ID associated with it in memory. Using this ID, the content of the Tweet can be retrieved and displayed on  request over websockets.


## Results
Testing Newsflash was to some degree a subjective process as we had to determine which topics Newsflash marked as trended corresponded to real events. Newsflash delivers the top 30 ranked terms amongst which we found many promising terms corresponding to emerging stories within the city. However, we faced two key challenges in producing meaningful rankings:

#### Data

Our data set was thorough, however the timing skewed our results. We terminated data collection at midnight Thursday April 30th. Newsflash is designed to be trained on an input data set which it then augments with live Tweets. In a production environment, this training dataset would run up until moments before training. This ensures that the Newsflash model is trained on data that is contextually relevant to the time and date that the model starts to collect live Tweets. However, since we only had a single data set that was many days outdated by the time we got to testing our model, we couldn't test our model on the most recently occurring events. Instead we had to look back the events of the week of April 27th in NYC. It also meant that we couldn't see how well the model generalized across many different datasets. This would have been useful analysis.

#### Volume vs. _acceleration_

Many terms rise to the top due solely to their sheer frequency. For instance, "New York" and similar terms are incredibly common in NYC and thus it's very difficult to weight these terms down. We don't want to ignore terms of high frequency entirely, but we do want to avoid reporting obvious terms like "New", "York", "Madison", etc. 

#### Successes

Our largest dataset does raise some very pertinent terms to the top such as "protest". On April 29th a protest for the Freddie Gray case in Baltimore took place in Union Square. Not only did the Newsflash model detect the sharp increase in this topic's popularity, it also found a very tight bound to the location of the protest in Union Square. Plotting the change in frequency, or _acceleration_ of the term's frequency, we can very clearly see the increase corresponding to the protest.


![](protest-graph-labeled.png "protest acceleration")
![](bounding-box_protest.png "protest maps")


Amongst other smaller data sets we used for testing we found similar successes, such as the Mayweather/Pacquiao fight which was widely discussed. However, the lack of a geographic center for this trend made it a less useful term to report as trending. Overall, we found that our model does pick up on true positives well, but overwhelmingly still reports false positives. Further research and parameter tuning is necessary to reduce the false positive rate of Newsflash. 

## Future directions

We are excited to continue development of Newsflash beyond the scope of this course. Currently, we are primarily focused on:

1. Improving entropic bounding box calculations
2. Improving resolution of the _acceleration_ metric
3. Regulate/standardize resizing of Tweet dots, especially in the case of overlapping tweets (they should be zoomed or shuffled on mouse hover so that all overlapping Tweets can be viewed/accessed)
4. Adding options in the UI so that the user can dynamically change the information provided
	a. Specify the resolution and relative weight of the _acceleration_ metric
	b. Search for terms
	c. Remove terms from the term rank list. For example, things like ‘new', ‘york', and ‘manhattan', are always considered significant in the greater Manhattan area due to sheer frequency, but are essentially stopwords in this context.


