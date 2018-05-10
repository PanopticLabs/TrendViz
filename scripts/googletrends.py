import urllib2
import json
import csv

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def get_data(searchterms, timescale):
    if timescale == 'day':
        scale = 'now+1-d'
    if timescale == 'week':
        scale = 'now+7-d'
    if timescale == 'month':
        scale = 'today+1-m'
    if timescale == 'quarter':
        scale = 'today+3-m'
    if timescale == 'year':
        scale = 'today+12-m'

    first = True
    for term in searchterms:
        if first:
            trend_terms = '%7B%22keyword%22:%22' + urllib2.quote(term.lower()) + '%22,%22geo%22:%22%22,%22time%22:%22' + scale + '%22%7D'
            first = False
        else:
            trend_terms = trend_terms + ',%7B%22keyword%22:%22' + urllib2.quote(term.lower()) + '%22,%22geo%22:%22%22,%22time%22:%22' + scale + '%22%7D'

    query = '{"comparisonItem":[' + trend_terms + '],"category":0,"property":""}'


    url = 'https://trends.google.com/trends/api/explore?hl=en-US&tz=0&req=' + query + '&tz=0'

    #urlterm = urllib2.quote(searchterm)
    #url = 'https://trends.google.com/trends/api/explore?hl=en-US&tz=0&req=%7B%22comparisonItem%22:%5B%7B%22keyword%22:%22' + urlterm + '%22,%22geo%22:%22%22,%22time%22:%22' + scale + '%22%7D%5D,%22category%22:0,%22property%22:%22%22%7D&tz=0'
    req = urllib2.Request(url, headers=hdr)
    response = urllib2.urlopen(req)

    first = True
    for line in response:
        if first:
            first = False
        else:
            j = json.loads(line)

    response.close()

    request = json.dumps(j['widgets'][0]['request'])
    token = j['widgets'][0]['token']

    csvfile = get_csv(searchterms, timescale, request, token)
    return csvfile

def get_csv(searchterms, timescale, req, token):
    first = True
    for searchterm in searchterms:
        if first:
            q = searchterm
        else:
            q = q + ',' + searchterm

    urlterm = urllib2.quote(q)
    req = urllib2.quote(req)
    tz = "0"

    url = 'https://trends.google.com/trends/api/widgetdata/multiline/csv?req={0}&token={1}&tz={2}'.format(req, token, tz)

    request = urllib2.Request(url, headers=hdr)
    request.add_header('Referer', 'https://trends.google.com/trends/explore?date=now%201-d&q=' + urlterm)
    response = urllib2.urlopen(request)

    trend_csv = csv.reader(response)
    csvfile = 'csv/' + searchterm + '.csv'
    with open(csvfile, 'w') as fp:
        writer = csv.writer(fp, delimiter=',')

        count = 0
        for row in trend_csv:
            count += 1
            if count == 3:
                row[0] = 'Date'

                x = 1
                for searchterm in searchterms:
                    row[x] = searchterm.title() + ' Trends'
                    x += 1

                writer.writerow(row)

            if count > 3:
                writer.writerow(row)

    response.close()
    return csvfile
