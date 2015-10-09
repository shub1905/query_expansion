import json
import preprocess
import expansion
import queryBing
import sys

# Prompt for user feedback for each of the Top 10 results
# If any relevant feedback found, put the corresponding result into the 'relevant' list
# and add the counter for precision of this round
# return the int version of precision

def getUserFeedback(result, query, prec_int):
    # Show 10 results in loop and get user feedback
    print '\nSee Top 10 results for these query keywords: [', ' + '.join(query), ']...'
    print 'Please give us your feedback:\n'
    relevant = []
    feed_prec_int = 0
    for i in range(10):
        print '[Result ' + str(i + 1) + ']'
        print 'Title:', result[i]['title']
        print 'URL:', result[i]['url']
        print 'Description:', result[i]['desp']
        while True:
            ans = raw_input('Is this a relevant result? (y/n) ')
	    ans = str.strip(ans).lower()
            if ans == 'y':
                feed_prec_int += 1
                relevant.append(i)
                break
            if ans == 'n':
                break
        print ''
    # return the number of docs marked as relevant
    # and indices of docs marked as relevant
    return feed_prec_int, relevant

# a. Get query result from Bing
# b. Get user feedback
# c. Preprocess - build inverted index
# d. Expansion - Rocchio algorithm

def rf_run(query_list, precision_int, accountKey, transcript_file):
    # a. Get query results from Bing
    result = queryBing.processQuery(query_list, accountKey)
    # Exit when there's less than 10 resuls returned from Bing
    if len(result) < 10:
        print 'Less than 10 results found, exiting ...'
        exit(0)

    # b. Get user feedback 
    feed_prec_int, relev_docs_idx = getUserFeedback(result, query_list, prec_int)

    #Generate trascript of the run
    generate_transcript(query_list, feed_prec_int, relev_docs_idx, result, transcript_file)

    # Check whether to exit the program
    # If no relevant result at all, exit
    if feed_prec_int == 0:
        print 'No relevant result for feedback ... exiting ...\n'
        exit(0)
    # If precision@10 has been reached
    elif feed_prec_int >= prec_int:
        print 'Precision@10 has been reached, exiting ...\n'
        exit(0)
    # This is where core of query expansion come in handy
    print 'Thanks for your feedback. We are refining your query ... \n'
    print "Below are the doc_idx that you marked as relevant:"
    print relev_docs_idx

    # c. Preprocess - build inverted index and get doc-term matrix
    # Get inverted index for each term in the result set
    inverted_index, max_tf = preprocess.create_index_for_all_docs(result)
    
    # Get tf*idf weight matrix according to the inverted index
    tf_idf_matrix, term_list, query_vec = preprocess.create_tf_idf_matrix(
                                        inverted_index, max_tf,
                                        len(result), query_list)
    # d. Expansion - Rocchio algorithm
    # parameters taken from reference text, check README for more info
    new_query = expansion.relevance_feedback_rocchio(
                	tf_idf_matrix, query_vec, relev_docs_idx, term_list,
                	query_list, 1, 0.75, 0.15)
    return new_query

def generate_transcript(query_list, feed_prec_int, relev_docs_idx, result, transcript_file):
    string_to_publish = '====================='*3+'\n'
    string_to_publish += 'Precision = {}\n'.format(feed_prec_int/10.0)
    string_to_publish += 'query: {}\n'.format(' '.join(query_list))
    string_to_publish += 'Results:\n'
    for idx,res in enumerate(result):
        if idx in relev_docs_idx:
            string_to_publish += 'Relevant: YES\n'
        else:
            string_to_publish += 'Relevant: NO\n'
        string_to_publish += json.dumps(result[idx], indent=4) + '\n'
    transcript_file.write(string_to_publish)

if __name__ == '__main__':
    transcript_file = open('transcript.txt','a')
    # Pass in the query keyword list
    if len(sys.argv) < 4:
        print '''Usage: python main.py account_key precision query_terms'''
        exit(0)

    # Get accountKey, precision, query
    # accountKey = 'v2+SSNBtR6FCjUsVvr1uh0oQr99PA3WU7RxbP3g6fzg'
    accountKey = sys.argv[1]
    precision = float(sys.argv[2])
    query_list = sys.argv[3:]
    print 'Your query: [', ' + '.join(query_list), ']'
    # Pass in the precision@10, but multiply it by 10
    prec_int = precision * 10

    # Get the program started after all parameters are set
    # while loop goes here
    while True:
        query_list = rf_run(query_list, prec_int, accountKey, transcript_file)
