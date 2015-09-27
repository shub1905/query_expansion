import urllib2
import base64
import ConfigParser
import json

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
    bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + query + '%27&$top=10&$format=json'
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
## and mark 'has_relev' to 'True'
## return the 'has_relev' flag and the 'relevant' list
def getUserFeedback(result):
    ## Show 10 results in loop and get user feedback
    print '\nSee Top 10 results below, and please give us your feedback:\n'
    relevant = []
    has_relev = False
    for i in range(len(result)):
        print '[Result ' + str(i + 1) + ']'
        print 'Title:', result[i]['title']
	print 'URL:', result[i]['url']
        print 'Description:', result[i]['desp']
	while True:
	    ans = raw_input('Is this a relevant result? (y/n) ')
	    if ans == 'y':
		has_relev = True
		relevant.append(result[i])
		break
	    if ans == 'n':
		break
	print ''
    return has_relev, relevant 
 
if __name__ == '__main__':
    ## Open config file
    Config = ConfigParser.ConfigParser()
    Config.read('config.ini')
    # print Config.sections()

    ## Read accountKey from the config file
    accountKey = ConfigSectionMap("BingAPI")['accountkey']
    # print accountKey

    ## Pass in the query and get the result list
    query = 'gates'
    result = processQuery(query)
    # print out for debugging
    # print json.dumps(result, indent=4, sort_keys=True)
    
    has_relev, relevant = getUserFeedback(result)
    ## If no relevant results, exit the program
    if not has_relev:
	print 'No relevant result for feedback ... exiting ...\n'
        exit(0)
    print json.dumps(relevant, indent=4, sort_keys=True)
