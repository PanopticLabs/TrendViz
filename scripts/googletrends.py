import urllib2
import requests
import json
import csv
import io
hdr = {
        'Host': 'trends.google.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.7 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'}

session = requests.Session()
response = session.get('https://trends.google.com', headers=hdr)

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
    response = session.get(url, headers=hdr)
    j = json.loads(response.text[4:])
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
    newhdr = dict(hdr)
    newhdr['Referer'] = 'https://trends.google.com/trends/explore?date=now%201-d&q=' + urlterm
    response = session.get(url, headers=newhdr)
    trend_csv = csv.reader(io.StringIO(response.text))
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
