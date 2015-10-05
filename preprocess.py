import pickle
import urllib2
import time
import operator
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
  # print tokens
  stemmed = [stemmer.stem(t).encode('utf-8') for t in tokens]
  return stemmed


def create_index(all_docs):
  print "Creating inverted index for each term in result documents (<=1000) ..."
  all_docs_tokens = []
  headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
  start_time = time.time()
  for doc in all_docs:
    url = doc['url']
    print url
    # Download the full document
    req = urllib2.Request(url, headers=headers)
    try:
      response = urllib2.urlopen(req)

      # If no exception
      html_doc = response.read()

      # Use BeautifulSoup to extract all texts on the page
      # Reference:
      # http://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
      soup = BeautifulSoup(html_doc, 'html.parser')
      for script in soup(['script', 'style', '[document]', 'head', 'title']):
        script.extract()
      text = soup.get_text()
      lines = (line.strip() for line in text.splitlines())
      chunks = (phrase.strip() for line in lines for phrase in line.split())
      all_text = ' '.join(chunk for chunk in chunks if chunk)

      # Step 1: tokenize, and remove punctuations during the process
      tokenizer = RegexpTokenizer(r'\w+')
      # title_tokens = tokenizer.tokenize(d['title'].encode('utf-8').lower())
      # desp_tokens = tokenizer.tokenize(d['desp'].encode('utf-8').lower())
      text_tokens = tokenizer.tokenize(all_text.encode('utf-8').lower())
      # print text_tokens

      # Step 2: remove stop words
      # title_tokens = remove_stop_words(title_tokens)
      # desp_tokens = remove_stop_words(desp_tokens)
      text_tokens = remove_stop_words(text_tokens)

      # Step 3: word stemming
      # Not necessary, could try; first maybe not include it
      ## title_tokens = do_stemming(title_tokens)
      ## desp_tokens = do_stemming(desp_tokens)
    except Exception as e:
      print "Exception!", e
      text_tokens = []
    finally:
      print len(text_tokens)
      # print text_tokens
      all_docs_tokens.append(text_tokens)

  end_time = time.time()
  print 'Total time:', end_time - start_time, 's'
  print 'all_docs_tokens length:', len(all_docs_tokens)
  print 'all_docs length:', len(all_docs), all_docs
  file_handle = open('doc_tokens.pickle','wb')
  pickle.dump(all_docs_tokens, file_handle)
  file_handle.close()
  return all_docs_tokens


def create_reverse_index(all_docs_tokens):
  term_doc_index = defaultdict(list)
  freq_term = {}
  for doc_id, doc_tokens in enumerate(all_docs_tokens):
    for token in doc_tokens:
      term_doc_index[token].append(doc_id)
      freq_term[token] = freq_term.get(token, 0) + 1

  # print term_doc_index, freq_term
  freq_term_sort = sorted(freq_term.items(), key=operator.itemgetter(1), reverse=True)
  return freq_term_sort

# handle = open('relev_doc.pickle', 'r')
# relev_docs = pickle.load(handle)
# create_index(relev_docs)

# file_handle = open('doc_tokens.pickle','r')
# all_docs_tokens = pickle.load(file_handle)
# create_reverse_index(all_docs_tokens)
# file_handle.close()