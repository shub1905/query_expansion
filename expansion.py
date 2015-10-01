import pickle
import preprocess
import nltk

def run(all_docs):
    # get term-doc index
    return preprocess.create_index(all_docs)

if __name__ == '__main__':
    # with open('relev_doc.pickle', 'rb') as handle:
    #    docs = pickle.load(handle)

    with open('result.pickle', 'rb') as handle:
	all_docs = pickle.load(handle)

    term_doc_index = run(all_docs)

