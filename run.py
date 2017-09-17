from datetime import date
from datetime import datetime
from blackscholes import black_scholes
from htmlparser import HTMLTableParser
import requests, json, datetime


rf = 2

r = requests.get('https://www.malaysiawarrants.com.my/result?underlying=all&type=call&moneyness=all&moneynessPercent=all&maturity=all&effectiveGearing=all&issuer=all&expriry=all&sortBy=na&sortOrder=na&timestamp&indicator=all&delta=undefined&expiry=all&mode=search')
if(r.ok):
    html_parser = HTMLTableParser()
    html_parser.feed(r.text)
    r.close()

    for table in html_parser.tables:
        for row in table:
            w_name = row[0]
            desc = row[1]

            if w_name == "" or row[2]== "" or "Near expiry" in desc or row[9] == '-' or row[10] == '-':
                continue

            price = float(row[2].replace(",", ""))
            ex_price = float(row[4].replace(",", ""))
            cr = float(row[5].replace(",", ""))
            exdate = row[6]
            vola = float(row[-1])
            
            bid = float(row[9].replace(",", ""))
            ask = float(row[10].replace(",", ""))

            if vola == 0 or cr > 1000:
                continue

            d = datetime.datetime.strptime(exdate, '%d %b %y')
            exdate = d.strftime('%Y-%m-%d')
            exdate = datetime.datetime.strptime(exdate, '%Y-%m-%d')
            #if w_name =="AXIATA-C9":
            #    print(row)
            time = float((exdate.date() - datetime.datetime.now().date()).days/365)
            
            bs = black_scholes(1,price,ex_price,time,vola/100,rf/100,cr)
            dif = round(bs/bid, 2)

            if dif < 1.5 and dif > 1.05:
                obj = json.loads(requests.get('https://www.malaysiawarrants.com.my/PowerSearchJSON?key=%s&limit=10&d=1488553270134&type=w' % w_name).text)
                symbol = obj['powersearch'][0]['symbol']
                
                price_data = requests.get('http://klse.i3investor.com/servlets/stk/%s.jsp' % symbol).text
                hp = HTMLTableParser()
                hp.feed(price_data)
                for x in hp.tables:
                    for i, val in enumerate(x):
                        if val[0] == 'Last Price':
                            last_price = float(x[i+1][0])

                diff = round(bs/last_price, 2)
                if dif < 1.5 and dif > 1.05:
                    print("%s - bs: %s  market: %s diff: %s" % (w_name, bs, last_price, diff))