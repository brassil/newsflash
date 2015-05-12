import porter_stemmer
import re

class Tokenizer(object):
	def __init__(self, stop_words):
		self.stemmer = porter_stemmer.PorterStemmer()
		self.stops = []
		if(stop_words is not None):
			with open(stop_words, 'r') as file:
				for line in file:
					self.stops.append(line)

	def clip_duplicates(self, text):
		return re.sub(r'(.)\1+', r'\1\1', text)

	def clip_hashes(self,word):
		res = re.sub(r'^#', r'', word)
		return res

	def clip_punc(self, word):
		return re.sub(r'([,\.\'\"\*\&\%\$\@;\:\?\-\!])+', r'', self.stemmer.stem(word, 0, len(word)-1))

	def find_urls(self, word):
		if (re.search('(http://|https://|www.)',word)):
			return 'URL'
		return word

	def find_user(self, word):
		if(re.match('@', word)):
			return 'AT_USER'
		return word

	def alph_start(self, word):
		if(re.match('[a-zA-Z]', word)):
			return True
		return False

	def no_stop(self, word):
		if word in self.stops:
			return False
		return True


	def __call__(self, tweet):
		words = tweet.split(' ');
		words = [self.clip_duplicates(self.clip_punc(self.find_user(self.find_urls(self.clip_hashes(word.lower()))))) for word in words if self.no_stop(self.alph_start(self.clip_hashes(word)))]

		return words
