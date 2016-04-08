def find_related_tweets(nf, start_terms):
	'''
	takes in the top n terms and tries to find groups of related tweets
	at first we're using 100 but this can be changed

	YO THIS DOESN'T WORK. after only 3 iterations we've captured almost
	all the terms (i.e. most tweets have <3 degrees of separation)
	'''
	terms = set()
	tweets = set()


	new_terms = set(start_terms)
	new_tweets = set()


	for level in range(3):
		for term in new_terms:
			new_tweets = new_tweets.union(nf.terms[term])

		# only lookup terms in tweets we haven't already looked up
		new_tweets = new_tweets.difference(tweets)
		terms = terms.union(new_terms)
		new_terms = set()

		for tid in new_tweets:
			new_terms = new_terms.union(nf.tweets[tid].words)

		tweets = tweets.union(new_tweets)
		new_tweets = set()

	return terms





