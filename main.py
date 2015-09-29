import urllib, urllib2
import base64
import ConfigParser
import json
import preprocess # customized in preprocess.py
import pickle

## Helper function for reading config file
## Source: https://wiki.python.org/moin/ConfigParserExamples
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

## Core function for processing query
## First do concatenation to get the Bing Search API request url
## Then send the request and get results
## Return only desired fields, which are 'Title', 'Url', 'Description' in our case
## Renamed to 'title', 'url', 'desp'
def processQuery(query):
    ## Pass in the query string
    ## Get top 10 results
    ## Specify the result format to be json
    quoted_query = '+'.join(query)
    bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + quoted_query + '%27&$top=10&$format=json'
    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}
    req = urllib2.Request(bingUrl, headers = headers)
    response = urllib2.urlopen(req)
    
    ## Get result list
    result = response.read()
    ## result contains the json response from Bing. 
    parsed_result = json.loads(result)['d']['results']
    parsed_result = [{'title': r['Title'], 'url': r['Url'], 'desp':r['Description']} for r in parsed_result]
    return parsed_result

## Prompt for user feedback for each of the Top 10 results
## If any relevant feedback found, put the corresponding result into the 'relevant' list
## and add the counter for precision of this round
## return the int version of precision 
def getUserFeedback(result, query, prec_int):
    ## Show 10 results in loop and get user feedback
    print '\nSee Top 10 results for these query keywords: [', ', '.join(query), ']...'
    print 'Please give us your feedback:\n'
    relevant = []
    feed_prec_int = 0
    for i in range(len(result)):
        print '[Result ' + str(i + 1) + ']'
        print 'Title:', result[i]['title']
	print 'URL:', result[i]['url']
        print 'Description:', result[i]['desp']
	while True:
	    ans = raw_input('Is this a relevant result? (y/n) ')
	    if ans == 'y':
		feed_prec_int += 1
		relevant.append(result[i])
		break
	    if ans == 'n':
		break
	print ''
    return feed_prec_int, relevant 
 
if __name__ == '__main__':
    ## Open config file
    Config = ConfigParser.ConfigParser()
    Config.read('config.ini')
    # print Config.sections()

    ## Read accountKey from the config file
    accountKey = ConfigSectionMap("BingAPI")['accountkey']
    # print accountKey

    ## Pass in the query keyword list and get the result list
    # query = ['gates','1234jAsdkfjsl']	# for testing 
    query = ['gates']
    print ' '.join(query)
    precision = 0.5
    prec_int = precision * 10
    result = processQuery(query)
    # print out for debugging
    # print json.dumps(result, indent=4, sort_keys=True)

    ## Exit when there's less than 10 resuls returned from Bing
    if len(result) < 10:
	'Less than 10 results found, exiting ...'

    feed_prec_int, relev_doc = getUserFeedback(result, query, prec_int)

    ## Check whether to exit the program
    ## If no relevant result at all, exit
    if feed_prec_int == 0:
	print 'No relevant result for feedback ... exiting ...\n'
        exit(0)
    ## If precision@10 has been reached
    elif feed_prec_int >= prec_int:
        print 'Precision@10 has been reached, exiting ...\n'
	exit(0)
    ## This is where core of query expansion come in handy
    else:
	print 'Thanks for your feedback. We are refining your query ... \n'
    print "Below are the results that you marked as relevant:"
    print json.dumps(relev_doc, indent=4, sort_keys=True)

    ## Preprocessing for AQE
    
    # below for test
    # for doc in relev_doc:
    #    print doc
    # with open('relev_doc.pickle', 'wb') as handle:
    # pickle.dump(relev_doc, handle)
    # preprocess.create_index(relev_doc)
