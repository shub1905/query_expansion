import pickle
import nltk
import urllib2
import json
import time
import math
import operator
import numpy as np
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from collections import defaultdict
from bs4 import BeautifulSoup
def remove_stop_words(tokens):
    stopset = set(stopwords.words('english'))
    removed = [t for t in tokens if not t in stopset and len(t) != 1]
    return removed

def do_stemming(tokens):
        stemmer = SnowballStemmer('english')
        #print tokens
        stemmed = [stemmer.stem(t).encode('utf-8') for t in tokens]
        return stemmed

def get_tokens_for_single_doc(req):
    try:
        response = urllib2.urlopen(req)
 
        ## If no exception
	html_doc = response.read()
	
   	## Use BeautifulSoup to extract all texts on the page
 	## Reference: http://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
	soup = BeautifulSoup(html_doc, 'html.parser')
	for script in soup(['script', 'style', '[document]', 'head', 'title']):
	    script.extract()
	text = soup.get_text()
	lines = (line.strip() for line in text.splitlines())
	chunks = (phrase.strip() for line in lines for phrase in line.split())
	all_text = ' '.join(chunk for chunk in chunks if chunk)

	## Step 1: tokenize, and remove punctuations during the process
	tokenizer = RegexpTokenizer(r'\w+')
	text_tokens = tokenizer.tokenize(all_text.encode('utf-8').lower())

	## Step 2: remove stop words
	text_tokens = remove_stop_words(text_tokens)

	## Step 3: word stemming
	## Not necessary, could try; first maybe not include it
	## title_tokens = do_stemming(title_tokens)
	## desp_tokens = do_stemming(desp_tokens)
    except KeyboardInterrupt:
        print "Execution interrupted! Exiting ..."
	exit(0)
    except:
	print "Exception!"
	# print e.fp.read()
	text_tokens = []
    return text_tokens

def create_index_for_relev(relev_docs):
    print "Creating inverted index for each term in relevant documents (in top 10) ..."
    relev_index = {}
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    start_time = time.time()
    for d in relev_docs:
	print d
	## Download the full document
        req = urllib2.Request(d['url'], headers = headers)
	text_tokens = get_tokens_for_single_doc(req)
	print '#tokens read:', len(text_tokens)
	## Update the dictionary
	for t in text_tokens:
	    if t not in relev_index:
		    relev_index[t] = []
		# break
    end_time = time.time()
    print 'Creating index time:', end_time - start_time, 's'
    # print relev_index
    # print len(relev_index)
    return relev_index

def fill_in_index_for_res(all_docs, relev_index):
    print len(relev_index)
    print "Filling in inverted index for each term in result documents (<=1000) ..."
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

    start_time = time.time()
    num = 100 ## number of docs used for retrieving
    if len(all_docs) < num:
	top_len = len(all_docs)
    else:
	top_len = num

    max_tf = 1
    for i in range(top_len):
	req = urllib2.Request(all_docs[i], headers = headers)
	text_tokens = get_tokens_for_single_doc(req)
	print str(i + 1) + '/' + str(top_len) + ' - ' + all_docs[i] + ' - ' + '#tokens read:' + str(len(text_tokens))
	## Update the postings
	for t in text_tokens:
	    if t in relev_index:
		if len(relev_index[t]) == 0 or relev_index[t][-1][0] != i:
		    relev_index[t].append((i, 1))
		else:
		    relev_index[t][-1] = (i, relev_index[t][-1][1] + 1)
		    if relev_index[t][-1][1] > max_tf:
			max_tf = relev_index[t][-1][1]
    end_time = time.time()
    print 'Filling in index time:', end_time - start_time, 's'
    return relev_index, top_len, max_tf

def expand_query_wording(relev_index, top_len, max_tf, query):
    logN = math.log10(top_len)
    ## Compute idf for each term
    relev_index = {t: (relev_index[t], logN - math.log10(len(relev_index[t]))) for t in relev_index}
    ## Compute tf*idf for each term and make up vectors
    for t in relev_index:
	postings = relev_index[t][0]
	idf = relev_index[t][1]
	tf_idf_vec = [0] * top_len
	for p in postings:
	    pidx = p[0]
	    tf = p[1]
	    # tf = 0.6 * p[1]/max_tf + 0.4
	    tf_idf_vec[pidx] = tf * idf
        relev_index[t] = (postings, idf, tf_idf_vec)
    ## Compute scores for each term
    score_dict = {}
    for t in relev_index:
	if t not in query:
	    score =  0
	    for q in query:
		score += np.dot(relev_index[t][2], relev_index[q][2])
	    score_dict[t] = score
    ## Sort scores
    sorted_score = sorted(score_dict.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_score
