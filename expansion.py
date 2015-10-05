import pickle
import preprocess
import nltk
import operator

def run(query):
    # create term-doc index for all terms in relevant documents
    with open('relev_doc.pickle','rb') as handle:
	relev_docs = pickle.load(handle)
    relev_index = preprocess.create_index_for_relev(relev_docs)

    # fill in index for all terms in relevant documents
    with open('result.pickle', 'rb') as handle:
       all_docs = pickle.load(handle)
    relev_index, top_len, max_tf = preprocess.fill_in_index_for_res(all_docs, relev_index)

    # expansion
    sorted_score = preprocess.expand_query_wording(relev_index, top_len, max_tf, query)
    for i in range(10):
	print sorted_score[i]

if __name__ == '__main__':
    query = ['gates']
    run(query)

