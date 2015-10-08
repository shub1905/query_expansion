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
def remove_stop_words(tokens):
    stopset = set(stopwords.words('english'))
    removed = [t for t in tokens if not t in stopset and len(t) != 1]
    return removed

def do_stemming(tokens):
    stemmer = SnowballStemmer('english')
    #print tokens
    stemmed = [stemmer.stem(t).encode('utf-8') for t in tokens]
    return stemmed

def get_tokens_for_single_doc(doc):
    title_text = doc['title']
    desp_text = doc['desp']

    ## Step 1: tokenize, and remove punctuations during the process
    tokenizer = RegexpTokenizer(r'\w+')
    title_tokens = tokenizer.tokenize(title_text.encode('utf-8').lower())
    desp_tokens = tokenizer.tokenize(desp_text.encode('utf-8').lower())

    ## Step 2: remove stop words
    title_tokens = remove_stop_words(title_tokens)
    desp_tokens = remove_stop_words(desp_tokens)

    ## Step 3: word stemming
    ## Not necessary, could try; first maybe not include it
    ## title_tokens = do_stemming(title_tokens)
    ## desp_tokens = do_stemming(desp_tokens)

    return title_tokens, desp_tokens

def create_index_for_all_docs(result):
    print "Creating inverted index for each term in the result set ..."
    inverted_index = {}
    max_tf = 1
    for i in range(len(result)):
	title_tokens, desp_tokens = get_tokens_for_single_doc(result[i])
	## Update the dictionary
	for t in title_tokens:
	    if t not in inverted_index:
		inverted_index[t] = defaultdict(int)
	    inverted_index[t][i] += 1
	    if inverted_index[t][i] > max_tf:
		max_tf = inverted_index[t][i]
        for t in desp_tokens:
            if t not in inverted_index:
                inverted_index[t] = defaultdict(int)
            inverted_index[t][i] += 1
	    if inverted_index[t][i] > max_tf:
                max_tf = inverted_index[t][i]
    return inverted_index, max_tf

def create_tf_idf_matrix(inverted_index, max_tf, num_doc, query_list):
    print "Creating document-term matrix according to the inverted index ..."
    # print '\n'
    query_dict = {q for q in query_list}
    # print query_dict
    term_list = inverted_index.keys()
    tf_idf_matrix = []
    query_vec = [0] * len(term_list)
    logN = math.log(num_doc, 2)
    for i in range(len(term_list)):
	cur_inverted = inverted_index[term_list[i]]
	cur_vec = [0] * num_doc
	cur_idf = logN - math.log(len(cur_inverted), 2)
	for doc_idx in cur_inverted:
	    tf = cur_inverted[doc_idx]	# could apply SMART variant here
	    cur_vec[doc_idx] = tf * cur_idf
	tf_idf_matrix.append(cur_vec)
	if term_list[i] in query_dict:
      	    query_vec[i] = cur_idf
	# print term, cur_idf, cur_inverted
	# print cur_vec
    # transpose - document to words
    tf_idf_matrix = [list(x) for x in zip(*tf_idf_matrix)]
    # cosine normalization
    tf_idf_matrix = [(x/np.linalg.norm(x)).tolist() for x in tf_idf_matrix]
    query_vec = (query_vec/np.linalg.norm(query_vec)).tolist()
    return tf_idf_matrix, term_list, query_vec

if __name__ == '__main__':
    # create term-doc index for all terms in relevant documents
    with open('result.pickle', 'rb') as handle:
        result = pickle.load(handle)
    with open('relev_doc_idx.pickle','rb') as handle:
        relev_docs_idx = pickle.load(handle)
    print relev_docs_idx

    query_list = ['gates']

    # main starts from here
    # Get inverted index for each term in the result set
    inverted_index, max_tf = create_index_for_all_docs(result)
    # for i in inverted_index:
    # print i, inverted_index[i]

    # Get tf*idf weight matrix according to the inverted index
    tf_idf_matrix, term_list, query_vec = create_tf_idf_matrix(
					inverted_index, max_tf,
					len(result), query_list)
    '''
    with open('tf_idf_matrix.pickle', 'wb') as handle:
        pickle.dump(tf_idf_matrix, handle)
    with open('term_list.pickle', 'wb') as handle:
        pickle.dump(term_list, handle)
    with open('query_vec.pickle', 'wb') as handle:
        pickle.dump(query_vec, handle)
    '''
 
