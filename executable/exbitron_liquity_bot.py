import time
import configparser
import exbitron_exchange_api as exchange

###
### CRYPTIX LIQUIDITY BOT FOR BUY AND SELL ORDERS ###
###

config = configparser.ConfigParser()
config.read('config.txt')

exchange.TOKEN = config['DEFAULT']['API_TOKEN']

START_USDT_AMOUNT = float(config['DEFAULT']['START_USDT_AMOUNT'])
START_COIN_AMOUNT = float(config['DEFAULT']['START_COIN_AMOUNT'])
MAX_USDT_AMOUNT = float(config['DEFAULT']['MAX_USDT_AMOUNT'])
MAX_COIN_AMOUNT = float(config['DEFAULT']['MAX_COIN_AMOUNT'])

SPREAD_PERCENTAGE = float(config['DEFAULT']['SPREAD_PERCENTAGE'])
NUM_OFFERS = int(config['DEFAULT']['NUM_OFFERS'])
OFFER_DIFFERENCE = float(config['DEFAULT']['OFFER_DIFFERENCE'])

SLEEP_TIME = int(config['DEFAULT']['SLEEP_TIME'])

pair = 'CYTX-USDT'

def get_market_price():
    orderbook = exchange.GetOrderBook(pair, depth='50')

    if 'error' in orderbook:
        print(f"❌ Error fetching the order book: {orderbook['error']}")
        return None

    best_bid = max((float(order[0]) for order in orderbook['bids']), default=None)
    best_ask = min((float(order[0]) for order in orderbook['asks']), default=None)

    if best_bid is None or best_ask is None:
        print("❌ No valid bid or ask price found.")
        return None

    mid_price = (best_bid + best_ask) / 2
    print(f"Best Bid: {best_bid}, Best Ask: {best_ask}, Mid Price: {mid_price}")
    return mid_price

def create_offers(mid_price, spread_percentage, num_offers, offer_difference):
    buy_offers = []
    sell_offers = []

    spread = mid_price * (spread_percentage / 100.0)
    buy_price = mid_price - spread / 2
    sell_price = mid_price + spread / 2

    print(f"Creating offers: Mid price = {mid_price}, Spread = {spread}, Buy price = {buy_price}, Sell price = {sell_price}")

    for i in range(num_offers):
        buy_offers.append(buy_price * (1 - i * offer_difference))
        sell_offers.append(sell_price * (1 + i * offer_difference))

    return buy_offers, sell_offers

def get_balance_usdt():
    print("Fetching USDT balance...")
    balance = exchange.Balances()
    usdt_balance = next((item['balance'] for item in balance['user']['currencies'] if item['id'] == 'USDT'), 0.0)
    print(f"USDT balance fetched: {usdt_balance}")
    return usdt_balance

def place_orders(buy_offers, sell_offers, usdt_amount, coin_amount):
    print(f"Placing orders with {len(buy_offers)} buy and {len(sell_offers)} sell offers...")
    buy_amount_per_order = usdt_amount / len(buy_offers)
    sell_amount_per_order = coin_amount / len(sell_offers)

    for buy_price in buy_offers:
        try:
            print(f"Placing buy order at {buy_price}...")
            result = exchange.Order(buy_amount_per_order / buy_price, pair, buy_price, 'buy', 'limit')
            print(f"Buy order result: {result}")  
            if result.get('hasError') or result.get('status') != 'OK':
                print(f"❌ Failed to place buy order at {buy_price}. Error: {result}")
            else:
                print(f"✅ Placed buy order at {buy_price}")
        except Exception as e:
            print(f"❌ Error placing buy order at {buy_price}: {e}")
            if "Too many requests" in str(e):
                print("⏳ Rate limit reached. Pausing for 10 seconds.")
                time.sleep(10)
        time.sleep(1)

    for sell_price in sell_offers:
        try:
            print(f"Placing sell order at {sell_price}...")
            result = exchange.Order(sell_amount_per_order, pair, sell_price, 'sell', 'limit')
            print(f"Sell order result: {result}")  
            if result.get('hasError') or result.get('status') != 'OK':
                print(f"❌ Failed to place sell order at {sell_price}. Error: {result}")
            else:
                print(f"✅ Placed sell order at {sell_price}")
        except Exception as e:
            print(f"❌ Error placing sell order at {sell_price}: {e}")
            if "Too many requests" in str(e):
                print("⏳ Rate limit reached. Pausing for 10 seconds.")
                time.sleep(10)
        time.sleep(1)

if __name__ == '__main__':
    current_usdt_balance = START_USDT_AMOUNT
    current_coin_balance = START_COIN_AMOUNT

    while True:
        print("\n🔄 Starting new cycle...")

        if current_usdt_balance > MAX_USDT_AMOUNT:
            current_usdt_balance = MAX_USDT_AMOUNT
            print(f"⚠️ USDT capped at max: {MAX_USDT_AMOUNT}")
        if current_coin_balance > MAX_COIN_AMOUNT:
            current_coin_balance = MAX_COIN_AMOUNT
            print(f"⚠️ Coin capped at max: {MAX_COIN_AMOUNT}")

        mid_price = get_market_price()
        if mid_price is None:
            print("❌ Could not get mid price. Skipping order placement.")
            time.sleep(SLEEP_TIME)
            continue

        exchange.CancelAllOpenOrdersForMarket(pair)
        print("⏳ Wait 10 seconds after deleting orders...")
        time.sleep(10)

        buy_offers, sell_offers = create_offers(mid_price, SPREAD_PERCENTAGE, NUM_OFFERS, OFFER_DIFFERENCE)

        if current_usdt_balance > 0 and current_coin_balance > 0:
            place_orders(buy_offers, sell_offers, current_usdt_balance, current_coin_balance)
        else:
            print("⚠️ Not enough balance to place new orders.")

        print(f"⏳ Waiting for the next cycle ({SLEEP_TIME // 60} min)...")

        for remaining in range(SLEEP_TIME, 0, -1):
            mins, secs = divmod(remaining, 60)
            time_format = f"{mins:02d}:{secs:02d}"
            print(f"\r⏳ Next cycle in: {time_format}", end="", flush=True)
            time.sleep(1)

        current_usdt_balance = get_balance_usdt()
        print(f"💰 Updated USDT balance: {current_usdt_balance}")
