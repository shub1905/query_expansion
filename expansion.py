import pickle
import preprocess
import nltk
import operator

# This is just wrong ...
def relevance_feedback_rocchio(tf_idf_matrix, query_vec, relev_docs_idx, term_list,
				query_list, alpha, beta, gamma):
    relev_set = {i for i in relev_docs_idx}
    # print type(query_vec)

    # alpha * q_0
    modi_query_vec = [a * alpha for a in query_vec]
    # print modi_query_vec

    # Coefficient - beta/num of relevant docs
    coe_r = len(relev_set)
    # Coefficient - gamma/num of non-relevant docs
    coe_nr = gamma/(10 - coe_r)
    coe_r = beta/coe_r
    # print coe_r, coe_nr

    # Modify the query vector by integrating RELEVANT docs' vectors
    relev_vec = [0] * len(tf_idf_matrix[0])
    for i in relev_set:
        cur_vec = tf_idf_matrix[i]
        relev_vec = [a + b for a, b in zip(relev_vec, cur_vec)]
	# print i
    relev_vec = [a * coe_r for a in relev_vec]
    modi_query_vec = [a + b for a, b in zip(modi_query_vec, relev_vec)]
    # print relev_vec

    # Modify the query vector by integrating NONRELEVANT docs' vectors
    nonrelev_vec = [0] * len(tf_idf_matrix[0])
    for i in range(10):
	if i not in relev_set:
            cur_vec = tf_idf_matrix[i]
            nonrelev_vec = [a + b for a, b in zip(nonrelev_vec, cur_vec)]
	    # print i
    nonrelev_vec = [a * coe_nr for a in nonrelev_vec]
    modi_query_vec = [a - b for a, b in zip(modi_query_vec, nonrelev_vec)]
    # print nonrelev_vec
    # print modi_query_vec

    # Match the weights in modified query vector with actual terms
    term_dict = {a:b for a, b in zip(term_list, modi_query_vec)}
    # Sort the terms by their weights
    sorted_term = sorted(term_dict.items(), key=operator.itemgetter(1), reverse=True)
    print sorted_term[:10]
    # Pull out the highest ordered terms as new queries with length added by 2
    new_query = [t[0] for t in sorted_term[:len(query_list) + 2]]
    return new_query

if __name__ == '__main__':
    # create term-doc index for all terms in relevant documents
    with open('term_list.pickle', 'rb') as handle:
        term_list = pickle.load(handle)
    with open('tf_idf_matrix.pickle','rb') as handle:
        tf_idf_matrix = pickle.load(handle)
    with open('query_vec.pickle','rb') as handle:
        query_vec = pickle.load(handle)
    with open('relev_doc_idx.pickle','rb') as handle:
        relev_docs_idx = pickle.load(handle)
    print relev_docs_idx
    query_list = ['gates']

    # main starts from here
    new_query = relevance_feedback_rocchio(
		tf_idf_matrix, query_vec, relev_docs_idx, term_list,
		query_list, 1, 0.75, 0.15)
    print new_query
