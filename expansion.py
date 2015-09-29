import pickle
import preprocess
import nltk

def run():
    # get term-doc index
    return preprocess.create_index(docs)

if __name__ == '__main__':
    with open('relev_doc.pickle', 'rb') as handle:
	docs = pickle.load(handle)

    term_doc_index = run()

