import urllib
import urllib2
import base64
import json

# Get query result from Bing

def executeSingleQuery(bingUrl, headers):
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

def processQuery(query, accountKey):
    # Pass in the query string
    # Get top 1000 results by increment skip for every 50 top results
    # Specify the result format to be json
    quoted_query = '+'.join(query)
    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}

    # for skip in range(0, topUrlCount, 50):
    bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + \
                quoted_query + '%27&$top=10&$format=json&$skip=0'
    parsed_result = executeSingleQuery(bingUrl, headers)

    if len(parsed_result) < 10:
        return parsed_result

    parsed_result = [{'title': r['Title'], 'url': r['Url'],
                    'desp':r['Description']} for r in parsed_result]

    return parsed_result


