import requests
import json
import configparser

### https://github.com/simonjriddix/exbitron-api-python/blob/main/exbitron_exchange_api.py ###
### Cryptis: Addet CancelAllOpenOrdersForMarket
### Cryptis: Addet Debug
### Cryptis: Config File Function

config = configparser.ConfigParser()
config.read('config.txt')

API_ENDPOINT = "https://api.exbitron.digital/api/v1"
TOKEN = config['DEFAULT']['API_TOKEN']
UserAgent = 'Exbitron/CryptixBot'

def ReturnDataOrError(response):
    answer=json.loads(response.text)
    if answer['status'].upper()=='OK' and not answer['hasError']:
        return answer['data']
    raise Exception(answer['errorMessage'])

def ReturnTimestampOrError(response):
    answer=json.loads(response.text)
    if answer['status']=='OK' and not answer['hasError']:
        return answer['timestamp']
    raise Exception(answer['errorMessage'])

def ReturnDirectOrError(response):
    answer=json.loads(response.text)
    if 'status' in answer and answer['status']!='OK' and 'hasError' in answer and answer['hasError']:
        raise Exception(answer['errorMessage'])
    return answer

def ReturnStatusOrError(response):
    try:
        answer = response.json()
        if "success" in answer and answer["success"]:
            return True
        else:
            print(f"[API] Answer: {answer}")  
            return False
    except Exception as e:
        print(f"[EXCEPTION] {e}")
        return False
    
### BALANCES ###

def Balances(zero: bool = False):
    url = f"{API_ENDPOINT}/balances?zero={zero}"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 )
    return ReturnDataOrError(response)

### Coin Gecko ###

def GetCoinGeckoHistoricalTrades(ticker_id: str, limit: int=None, type: str=None, start_time: str=None, end_time: str=None):
    url = f"{API_ENDPOINT}/cg/historical_trades?ticker_id={ticker_id}"
    if limit!=None:
        url+=f"&limit={limit}"
    if type!=None:
        url+=f"&type={type}"
    if start_time!=None:
        url+=f"&start_time={start_time}"
    if end_time!=None:
        url+=f"&end_time={end_time}"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent}
                 )
    return ReturnDirectOrError(response)

def GetCoinGeckoOrderBook(ticker_id: str, depth: str=None):
    url = f"{API_ENDPOINT}/cg/orderbook?ticker_id={ticker_id}"
    if depth!=None:
        url+=f"&depth={depth}"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent},
                 )
    return ReturnDirectOrError(response)

def GetCoinGeckoPairs():
    url = f"{API_ENDPOINT}/cg/pairs"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent},
                 )
    return ReturnDirectOrError(response)

def GetCoinGeckoTickers():
    url = f"{API_ENDPOINT}/cg/tickers"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent},
                 )
    return ReturnDirectOrError(response)

### CMC ###

def GetCoinMarketCapAssets():
    url = f"{API_ENDPOINT}/cmc/assets"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent},
                 )
    return ReturnDirectOrError(response)

def GetCoinMarketCapOrderBook(market_pair: str, depth:str, level: str):
    url = f"{API_ENDPOINT}/cmc/orderbook/{market_pair}?"
    if depth!=None:
        url+=f"&depth={depth}"
    if level!=None:
        url+=f"&level={level}"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent},
                 )
    return ReturnDirectOrError(response)

def GetCoinMarketCapSummary():
    url = f"{API_ENDPOINT}/cmc/summary"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent},
                 )
    return ReturnDirectOrError(response)

def GetCoinMarketCapTicker():
    url = f"{API_ENDPOINT}/cmc/ticker"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent},
                 )
    return ReturnDirectOrError(response)

def GetCoinMarketCapTrades(market_pair: str):
    url = f"{API_ENDPOINT}/cmc/trades/{market_pair}"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent},
                 )
    return ReturnDirectOrError(response)

### HISTORY ###

def HistoryTrades(market_id: str=None, From: int=None, to: int=None, limit: int=None, page: int=None):
    url = f"{API_ENDPOINT}/history/trade?"
    if market_id!=None:
        url+=f"&market_id={market_id}"
    if From!=None:
        url+=f"&from={From}"
    if to!=None:
        url+=f"&to={to}"
    if limit!=None:
        url+=f"&limit={limit}"
    if page!=None:
        url+=f"&page={page}"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 )
    return ReturnDataOrError(response)

def HistoryTransaction(currency_id: str=None, type: str=None, From: int=None, to: int=None, limit: int=None, page: int=None):
    url = f"{API_ENDPOINT}/history/tx?"
    if currency_id!=None:
        url+=f"&currency_id={currency_id}"
    if type!=None:
        url+=f"&type={type}"
    if From!=None:
        url+=f"&from={From}"
    if to!=None:
        url+=f"&to={to}"
    if limit!=None:
        url+=f"&limit={limit}"
    if page!=None:
        url+=f"&page={page}"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 )
    return ReturnDataOrError(response)

### ORDER ###

def Order(amount: float, market: str, price: float, side: str, type: str):
    url = f"{API_ENDPOINT}/order"
    response = requests.post(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 json={
                    "amount": amount,
                    "market": market,
                    "price": price,
                    "side": side,
                    "type": type
                    }
                 )
    return ReturnDirectOrError(response)

# TODO
#: Orders class must be pass as parameter
def OrderBatch():
    url = f"{API_ENDPOINT}/order/batch"
    response = requests.post(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 data=json.dumps({
                    "orders": [
                        {
                        "amount": 0,
                        "market": "string",
                        "price": 0,
                        "side": "string",
                        "type": "string"
                        }
                    ]})
                 )
    return ReturnDataOrError(response)

def OrderCancelBatch(orders: list[str]):
    url = f"{API_ENDPOINT}/order/cancel/batch"
    response = requests.post(
        url,
        headers={
            "User-Agent": UserAgent,
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        data=json.dumps({"orders": orders}) 
    )
    return ReturnStatusOrError(response)

def CancelAllOpenOrdersForMarket(market: str):
    try:
        open_orders_wrapper = GetMarketOrder(market, "open")
        open_orders = open_orders_wrapper["userOrders"]["result"]

        print(f"[DEBUG] open_orders in {market}: {open_orders}")

        order_ids = [order["id"] for order in open_orders]

        if not order_ids:
            print(f"✅ No open orders in {market}")
            return

        print(f"🔄 Deleting {len(order_ids)} orders in {market}...")
        response = OrderCancelBatch(order_ids)

        if isinstance(response, dict) and response.get('status') == 'OK' and 'cancelled_orders' in response:
            print(f"✅ Successfully deleted {len(response['cancelled_orders'])} orders.")

    except Exception as e:
        print(f"❌ Error with {market}: {e}")

def GetMarketOrder(market: str, status: str, page: int=None, limit: int=None):
    url = f"{API_ENDPOINT}/order/market/{market}?status={status}"
    if page!=None:
        url=f"&page={page}"
    if limit!=None:
        url=f"&limit={limit}"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 )
    return ReturnDataOrError(response)


def GetOrder(id: str):
    url = f"{API_ENDPOINT}/order/{id}/cancel"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 )
    return ReturnDataOrError(response)

def OrderCancel(id: str):
    url = f"{API_ENDPOINT}/order/{id}/cancel"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 )
    return ReturnStatusOrError(response)

### ORDER BOOK ###

def GetOrderBook(market_pair: str, depth: int = 50):
    url = f"{API_ENDPOINT}/orderbook/{market_pair}"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 )
    return ReturnDirectOrError(response)

### MISC ###

def Ping():
    url = f"{API_ENDPOINT}/ping"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 )
    return ReturnTimestampOrError(response)

### TRADING ###

def GetTrading():
    url = f"{API_ENDPOINT}/trading/info"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 )
    return ReturnDataOrError(response)

def GetTradingPair(ticker: str):
    url = f"{API_ENDPOINT}/trading/info/{ticker}"
    response = requests.get(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 )
    return ReturnDataOrError(response)

def GetBalance(interval: str, market: str, timeFrom: int, timeTo: int):
    url = f"{API_ENDPOINT}/trading/kline"
    response = requests.post(url, 
                 headers={"User-Agent": UserAgent, "Authorization": f"Bearer {TOKEN}"},
                 data=json.dumps({
                    "interval": interval,
                    "market": market,
                    "timeFrom": timeFrom,
                    "timeTo": timeTo
                    })
                )
    return ReturnDataOrError(response)