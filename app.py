import time 
import sys
import math
from binance.client import Client 
from config import api_key , secret_key,symbol,interval,quantity,short_ema,long_ema,leverage
limit = "200"

client  = Client(api_key, secret_key)

def round_down(num,digits):
        factor = 10.0 ** digits
        return math.floor(num * factor) / factor


def ema(s, n):
    """
    returns an n period exponential moving average for
    the time series s

    s is a list ordered from oldest (index 0) to most
    recent (index -1)
    n is an integer

    returns a numeric array of the exponential
    moving average
    """
    #s = array(s)
    ema = []
    j = 1

    #get n sma first and calculate the next n period ema
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema.append(sma)

    #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(( (s[n] - sma) * multiplier) + sma)

    #now calculate the rest of the values
    for i in s[n+1:]:
        tmp = ( (i - ema[j]) * multiplier) + ema[j]
        j = j + 1
        ema.append(tmp)

    return ema


def check_decimals(symbol):
    info = client.get_symbol_info(symbol)
    val = info['filters'][2]['stepSize']
    decimal = 0
    is_dec = False
    for c in val:
        if is_dec is True:
            decimal += 1
        if c == '1':
            break
        if c == '.':
            is_dec = True
    return decimal


def get_quan(symbol):

    res = client.get_symbol_ticker(symbol=symbol)
    value = float(res['price'])
    return value

def get_data():
    res = client.get_klines(symbol=symbol, interval=interval,limit=limit)
    return_data = []
    for each in res:
        return_data.append(float(each[4]))
    return  return_data

def get_tick_and_step_size(symbol):
    tick_size = None
    step_size = None
    #symbol_info = client.get_symbol_info(symbol)
    info = client.futures_exchange_info();#print(info)
    for each in info['symbols']:
        if(each['symbol'] != symbol):
            continue
        symbol_info = each
        for filt in symbol_info['filters']:
            if filt['filterType'] == 'PRICE_FILTER':
                tick_size = float(filt['tickSize'])
            elif filt['filterType'] == 'LOT_SIZE':
                step_size = filt['stepSize'];#print(filt['stepSize'])
        return str(step_size).rstrip("0")


def place_order(symbol,typ):
    if(typ == "BUY"):
        try:
            client.futures_change_leverage(symbol=symbol,leverage=leverage)
            QUAN = float(quantity / get_quan(symbol) );
            QUAN = round_down(QUAN,len(get_tick_and_step_size(symbol).split(".")[1]));print(QUAN)
        except Exception as e:
            print("failed for some reason ",str(QUAN),str(e))
            return
        # try:
            
        # except:
        #     print("Order Closing failed for ",symbol,str(e))
        try:
            print(client.futures_create_order(symbol=symbol, quantity=QUAN,type="MARKET", side=typ,reduceOnly=True));#RISK_AMOUNT2 += (RISK_AMOUNT2/100) * CHANGE_IN_AMOUNT
        except Exception as e:
            print("order exit failed ", symbol,str(e))
        try:
            print(client.futures_create_order(symbol=symbol, quantity=QUAN,type="MARKET", side=typ));
        except Exception as e:
            print("order opening failed",symbol,str(e))

    elif(typ == "SELL"):
        
        try:
            client.futures_change_leverage(symbol=symbol, leverage=leverage)
            QUAN = float(quantity / get_quan(symbol) );
            QUAN = round_down(QUAN,len(get_tick_and_step_size(symbol).split(".")[1]));print(QUAN)
            print(client.futures_create_order(symbol=symbol, quantity=QUAN, type="MARKET", side=typ,reduceOnly=True))
        except Exception as e:
            print("order exit failed",symbol, str(e))
        try:
            print(client.futures_create_order(symbol=symbol, quantity=QUAN, type="MARKET", side=typ))
        except Exception as e:
            print("order opening fails",symbol,str(e))






def main():
    last_ema50 = None
    last_ema200 = None
    buy =True
    sell = False
    print("Script Running...")
    order_history = client.get_all_orders(symbol=symbol,limit=1)
    if(len(order_history)):
        if(order_history[0]['side'] == 'BUY'):
        	 buy =True
        	 sell = False
        else:
        	buy = False
        	sell= True

    print("Looking for new Trades....");print("Watching ",symbol)#print("buy",buy)"""
    while True:
        data  = get_data()
        price = get_quan()
        #print(price)
        ema50 =ema(data,short_ema)[-1]
        ema200 = ema(data, long_ema)[-1]
        #print(ema50, ema200)

        if(ema50 > ema200 and last_ema50 and not buy):
            if(last_ema50 < last_ema200):
                print("buy it")
                place_order(symbol,"BUY")
                buy = True
                sell = False
                

        if(ema200  > ema50 and last_ema50 and not sell):
            if(last_ema200 < last_ema50):
                place_order(symbol,"SELL")
                sell = True
                buy = False


        last_ema50 = ema50 
        last_ema200 = ema200
        time.sleep(2)
        


if __name__ == "__main__":
    main()
