#once source is defined in the stream_tweets thread, iterate over the source 
#and stream them
def retrieve_tweets(source, mode):
	thread = threading.current_thread()
	for tweet in source:
		if thread.stop:
			threads.remove(thread)
			break
		tweets_info = None
		if (mode == 'live'):
			tweets_info = parse_streaming_tweet(tweet)
		if (mode == 'file'):
			tweets_info = [tweet]

		if tweets_info is not None:
			print {'type' : 'tweet', 'tweet' : {'latitude' : tweets_info[0][5], 
					'longitude' : tweets_info[0][6], 'tweet' : tweets_info[0][7], 
					'time' : tweets_info[0][1], 'location': tweets_info[0][4]}}
			if mode == 'file':time.sleep(2)
			for client in clients:
				client.write_message(json.dumps({'type' : 'tweet', 
					'tweet' : {'latitude' : tweets_info[0][5], 
					'longitude' : tweets_info[0][6], 'tweet' : tweets_info[0][7], 
					'time' : tweets_info[0][1], 'location': tweets_info[0][4]}}))




def analyze_file(data_file, directory):
	nf_obj = nf.train_nf(directory+data_file, bi)
	sorted_terms = nf.compute_rankings(nf_obj)
	top_20_terms, top_20_boxes = nf.get_top_x_terms(sorted_terms, 20, nf_obj)
	stat_data = {'type' : 'top_term_stats', 'stats' : []}
	for term_ind in range(0,len(top_20_terms)):
		term = top_20_terms[term_ind]
		rank = nf_obj.ranks[term]
		stat_data['stats'].append({'term' : term, 'freq' : rank.freq, 
			'dfreq' : rank.dfreq, 'box_size' : rank.box_size, 
			'boxes' : top_20_boxes[term_ind], 
			'tweets' : nf.get_tweets_by_term(nf_obj, term)})
	top_10_links = list(reversed(sorted(nf_obj.urls, key=lambda x: len(nf_obj.urls[x]))))[:10]
	link_data = {'type' : 'top_links', 'links' : [link for link in top_10_links]}
	for client in clients:
		print stat_data
		print link_data
		client.write_message(json.dumps(stat_data))
		client.write_message(json.dumps(link_data))


def stream_tweets(mode='live', data_file=None, data_dir=None):
	'''
	==========================================================================
	============================ ANTIQUATED ==================================
	==========================================================================

	Get tweets either from a file or from the API.

	For API call, main documentation here:
	https://dev.twitter.com/streaming/reference/post/statuses/filter
	
	chose bounding box by picking points on google maps and then 
	rounding them out

	SW corner: 40.63,-74.12
	NE corner: 40.94,-73.68
	'''
	global nf_obj
	global is_trained
	source = None
	url = 'https://stream.twitter.com/1.1/statuses/filter.json'
	add = '?language=en&locations=-74.12,40.63,-73.68,40.94'

	#if the thread has been started with the LIVE mode specified
	if (mode == 'live'):
		print "--- SWITCHING TO LIVE MODE ---"
		source = twitterreq((url+add), 'GET', [])
		retrieve_tweets(source, mode)

	#if the thread has been started with the FILE mode specified
	elif (mode == 'file'):
		if data_file is None: sys.exit('ERROR: data file is None')

		print "--- SWITCHING TO FILE MODE ---"
		with open(os.path.join(data_dir,data_file), 'r') as tweet_file:
			source = csv.reader(tweet_file)
			next(source, None)
			retrieve_tweets(source, mode)

	elif (mode == 'newsflash'):
		print "--- SWITCHING TO LIVE MODE WITH NEWSFLASH OBJECT DATA ---"
		if data_file is None: sys.exit('ERROR: data file is None')
		
		print "Training Newsflash object"
		nf_obj = nf.train_nf(os.path.join(data_dir,data_file))
		print "Calculating preliminary rankings"
		nf.compute_rankings(nf_obj)
		is_trained = True
		for client in clients:
			client.write_message(json.dumps({'type' : 'status', 'status': True }))
		stream_stats(nf_obj)
		print "Begin streaming live data"
		source = twitterreq((url+add), 'GET', [])

		retreive_tweets_with_newsflash(nf_obj, source, 50)


	else:
		print "ERROR: invalid mode requested!"





class WSHandler(tornado.websocket.WebSocketHandler):

	def check_origin(self, origin):
		return True

	def open(self):
		global isFirst
		global clients
		global directory
		global nf_obj
		global is_trained
		print 'New connection'
		self.write_message(json.dumps({'type' : 'files', 
			'files' : os.listdir(directory)}))
		clients.append(self)
		if is_trained:
			stream_stats(nf_obj)
		else:
			self.write_message(json.dumps({'type':'status', 'status':False }))
	
	def on_message(self, message):
		global directory
		data = json.loads(message.encode('utf-8'))
		if (data['type'] == 'mode_change'):
			for thread in threads:
				thread.stop = True
			args = ()
			results = []
			target = stream_tweets
			if (data['details']['mode'] == 'file'):
				console.log('FILE');
				args=('file', data['details']['file'], directory)
			elif (data['details']['mode'] == 'analyze'):
				args = (data['details']['file'], directory)
				target = analyze_file
			t = threading.Thread(target=target, args=args)
			threading.Thread.stop = False
			t.stop = False
			threads.append(t)
			t.start()
		elif (data['type'] == 'get_tweet_text'):
			self.write_message(json.dumps({'type' : 'tweet_text',
				'tweet_text' : nf_obj.tweets[data['tid']].text }))


	def on_close(self):
		global threads
		clients.remove(self)
		print 'Connection closed'