from datetime import date
from datetime import datetime
from blackscholes import black_scholes
from htmlparser import HTMLTableParser
import requests, json, datetime, os

os.system("clear")

# risk free rate - Malaysia FD rate
rf = 4
data = requests.get('https://www.malaysiawarrants.com.my/mqmy/ScreenerJSONServlet?undefined&underlying=all&type=all&issuer=all&maturity=all&moneyness=all&moneynessPercent=all&effectiveGearing=all&expiry=all&indicator=all&sortBy=&sortOrder=asc').json()["data"]

for x in data:
    warrant_name = x["dwSymbol"]

    price = float(x["underlying_price"].replace(",", ""))
    ex_price = float(x["exercisePrice"].replace(",", ""))
    cr = float(x["conv_ratio"].replace(",", ""))
    exdate = x["maturity"]
    vola = float(x["impliedVolalitiy"])
    
    bid = float(x["bidPrice"].replace(",", ""))

    if vola == 0 or cr > 1000:
        continue

    d = datetime.datetime.strptime(exdate, '%d %b %y')
    exdate = d.strftime('%Y-%m-%d')
    exdate = datetime.datetime.strptime(exdate, '%Y-%m-%d')
    remaining_days = (exdate.date() - datetime.datetime.now().date()).days
    time = float(remaining_days/365)
    
    bs = black_scholes(1,price,ex_price,time,vola/100,rf/100,cr)
    margin = round(bs/bid, 2)

    if margin < 1.7 and margin > 1.2 and remaining_days > 60:
        print("%s\nblackscholes: %s\nmarket: %s\nmargin: %s\nexpired: %s\n" % (warrant_name, bs, bid, margin, exdate))
