import sys
import json
import pandas as pd

sys.path.insert(0, 'scripts')
import googletrends
import coinmarketcap
import cryptocompare
import fudhud
import plotly_fourline


def getSymbol(coinname):
    with open('symbols.json') as json_data:
        symbols = json.load(json_data)
        symbol = symbols[coinname.lower()]
        return symbol


try:
    timescale = sys.argv[1]

    coin = sys.argv[2]
    term = coin.replace('-', ' ')

except Exception as e:
    raise

try:
    sym = getSymbol(coin)
    print('Retrieved Symbol: ' + sym)
except:
    #Download symbol data from coinmarketcap, current limit is set to top 200 coins
    coinlimit = 200

    print('Downloading symbols for top ' + str(coinlimit) + ' coins...')
    coinmarketcap.downloadSymbols(coinlimit, 'symbols.json')
    try:
        sym = getSymbol(coin)
        print('Retrieved Symbol: ' + sym)
    except Exception as e:
        print(e)

try:
    print('Gathering data from Google Trends and CryptoCompare...')
    csvfile = googletrends.get_data([term], timescale)
    df = pd.read_csv(csvfile, delimiter=',')
    timelist = list(df['Date'])
    pricelist = cryptocompare.lookupPrice(timelist, sym, 'USD', True)
    #df['Historical Prices (USD)'] = pd.Series(pricelist, index=df.index)
    #df = df.assign('Historical Prices (USD)'=p.Series(pricelist).values)
    df['Historical Price (USD)'] = pricelist
    df.to_csv(csvfile)

    data = {
        'title' :  term.title() + ' Trends vs Price',
        'data' : []
    }
    if timescale == 'week':
        mentions = fudhud.getMentions(['$' + sym.lower()])
        data['data'].append({
            'title' : 'Twitter',
            'xlabel' : 'Date',
            'x' : mentions['twitter-date'],
            'ylabel' : 'Mentions',
            'y' : mentions['twitter-$' + sym.lower()],
            'yaxis' : 'y3'
        })
        data['data'].append({
            'title' : 'Reddit',
            'xlabel' : 'Date',
            'x' : mentions['reddit-date'],
            'ylabel' : 'Mentions',
            'y' : mentions['reddit-$' + sym.lower()],
            'yaxis' : 'y3'
        })

    data['data'].append({
        'title' : 'Price',
        'xlabel' : 'Date',
        'x' : timelist,
        'ylabel' : 'Historical Price (USD)',
        'y' : pricelist,
        'yaxis' : 'y1'
    })
    data['data'].append({
        'title' : 'Google Trends',
        'xlabel' : 'Date',
        'x' : timelist,
        'ylabel' : 'Google Trends',
        'y' : list(df[term.title() + ' Trends']),
        'yaxis' : 'y2'
    })


    print('Complete')
    print('Creating visualization...')
    plotly_fourline.plotGraph(data)
except Exception as e:
    print(e)
