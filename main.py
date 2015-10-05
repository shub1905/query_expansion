import urllib
import urllib2
import base64
import ConfigParser
import json
import preprocess  # customized in preprocess.py
import pickle
import time

# Helper function for reading config file
# Source: https://wiki.python.org/moin/ConfigParserExamples


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


def processSingleQuery(bingUrl, headers):
    print 'Executing query: ', bingUrl
    # Submit request
    req = urllib2.Request(bingUrl, headers=headers)
    response = urllib2.urlopen(req)
    # Get result list
    current_result = response.read()
    # current_result contains the json response from Bing.
    parsed_current = json.loads(current_result)['d']['results']
    return parsed_current

# Core function for processing query
# First do concatenation to get the Bing Search API request url
# Then send the request and get results
# Return only desired fields, which are 'Title', 'Url', 'Description' in our case
# Renamed to 'title', 'url', 'desp'


def processQueries(query):
    # Pass in the query string
    # Get top 1000 results by increment skip for every 50 top results
    # Specify the result format to be json
    parsed_result = []
    quoted_query = '+'.join(query)
    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}

    bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + quoted_query + '%27&$top=10&$format=json'
    top10 = processSingleQuery(bingUrl, headers)
    top10 = [{'title': r['Title'], 'url': r['Url'],
              'desp':r['Description']} for r in top10]

    if len(top10) < 10:
        return top10, parsed_result

    for skip in range(0, topUrlCount, 50):
        bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + \
            quoted_query + '%27&$top=50&$format=json' + '&$skip=' + str(skip)
        parsed_current = processSingleQuery(bingUrl, headers)
        parsed_current = [r['Url'] for r in parsed_current]
        parsed_result.extend(parsed_current)
        # print len(parsed_current)
        # time.sleep(1)

    print len(parsed_result)
    # for r in parsed_result:
    #    print r
    return top10, parsed_result

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
    # Open config file
    Config = ConfigParser.ConfigParser()
    Config.read('config.ini')
    # print Config.sections()

    # Read accountKey from the config file
    accountKey = ConfigSectionMap("BingAPI")['accountkey']
    topUrlCount = int(ConfigSectionMap("AppParameter")['TopURLCount'.lower()])

    # Pass in the query keyword list and get the result list
    # query = ['gates','1234jAsdkfjsl']	# for testing
    query = ['gates']
    print 'Your query: [', ' + '.join(query), ']'
    precision = 0.5
    prec_int = precision * 10
    top10, result = processQueries(query)
    print 'Length of top10 list:', len(top10)
    print 'Length of result list:', len(result)
    # print out for debugging
    # print json.dumps(result, indent=4, sort_keys=True)

    # Exit when there's less than 10 resuls returned from Bing
    if len(top10) < 10:
        print 'Less than 10 results found, exiting ...'
        exit(0)

    feed_prec_int, relev_doc = getUserFeedback(top10, query, prec_int)

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
    else:
        print 'Thanks for your feedback. We are refining your query ... \n'
        print "Below are the results that you marked as relevant:"
        print json.dumps(relev_doc, indent=4, sort_keys=True)

    # Preprocessing for AQE

    # below for test
    # for doc in relev_doc:
    #    print doc
    # with open('result.pickle', 'wb') as handle:
    #    pickle.dump(result, handle)
    # preprocess.create_index(relev_doc)
