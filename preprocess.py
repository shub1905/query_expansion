import pickle
import nltk
import urllib2
import json
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from collections import defaultdict
from HTMLParser import HTMLParser
class MyHTMLParser(HTMLParser):
    # def handle_starttag(self, tag, attrs):
    #    print "Encountered a start tag:", tag
    # def handle_endtag(self, tag):
    #    print "Encountered an end tag :", tag
    def handle_data(self, data):
	data = data.strip()
	if data != '':
            print "Encountered some data  :", data.strip()

def remove_stop_words(tokens):
    stopset = set(stopwords.words('english'))
    removed = [t for t in tokens if not t in stopset and len(t) != 1]
    return removed

def do_stemming(tokens):
        stemmer = SnowballStemmer('english')
        #print tokens
        stemmed = [stemmer.stem(t).encode('utf-8') for t in tokens]
        return stemmed

def create_index(docs):
    print "Creating inverted index for each term in Top 10 documents ..."
    term_doc_index = defaultdict(list)
    
    for d in docs:

	print '\n', d['title']
	print '\n', d['desp']
	print '\n', d['url']

	## download the full document
	## might not be needed for now
	## and need to figure out how to really do this since it's all html
	## headers = {'Content-Type': 'application/json'}
        ## req = urllib2.Request(d['url'], headers = headers)
    	## response = urllib2.urlopen(req)
	## doc = response.read()
	## myparser = MyHTMLParser()
	## myparser.feed(doc)

	## Step 1: tokenize, and remove punctuations during the process
	tokenizer = RegexpTokenizer(r'\w+')
	title_tokens = tokenizer.tokenize(d['title'].encode('utf-8').lower())
	desp_tokens = tokenizer.tokenize(d['desp'].encode('utf-8').lower())
	
	## Step 2: remove stop words
	title_tokens = remove_stop_words(title_tokens)
	desp_tokens = remove_stop_words(desp_tokens)
	
	## Step 3: word stemming
	## Not necessary, could try; first maybe not include it
	## title_tokens = do_stemming(title_tokens)
	## desp_tokens = do_stemming(desp_tokens)

	print '\n', title_tokens
	print '\n', desp_tokens
	print '\n', d['url']
	break
