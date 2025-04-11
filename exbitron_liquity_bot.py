import time
import exbitron_exchange_api as exchange

###
### CRYPTIX LIQUIDITY BOT FOR BUY AND SELL ORDERS ###
###

pair = 'CYTX-USDT'

# PUT HERE Your API Token created by Exbitron web app
exchange.TOKEN = 'YOUR_API_KEY_HERE'

# Starting values for the trading bot
START_USDT_AMOUNT = 100.0  # Initial amount of USDT (Tether) to start with, in this case, 100.0 USDT
START_COIN_AMOUNT = 100000.0  # Initial amount of coins to start with, in this case, 100,000 coins
MAX_USDT_AMOUNT = 100.0  # Maximum USDT amount the bot is allowed to hold, capped at 100.0 USDT
MAX_COIN_AMOUNT = 150000.0  # Maximum coin amount the bot is allowed to hold, capped at 150,000 coins
SPREAD_PERCENTAGE = 5.0  # Percentage to determine the price spread between buy and sell orders, 5% spread
NUM_OFFERS = 50  # Number of buy and sell orders to place, 50 orders in total
OFFER_DIFFERENCE = 0.005  # Difference between each successive buy or sell offer price, 0.005 = 0.5% price difference

def get_market_price():
    orderbook = exchange.GetOrderBook(pair, depth='50')

    if 'error' in orderbook:
        print(f"❌ Error fetching the order book: {orderbook['error']}")
        return None

    best_bid = None
    best_ask = None

    for order in orderbook['bids']:  
        if best_bid is None or float(order[0]) > best_bid: 
            best_bid = float(order[0])

    for order in orderbook['asks']:  
        if best_ask is None or float(order[0]) < best_ask: 
            best_ask = float(order[0])

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
        buy_price_i = buy_price * (1 - i * offer_difference)
        buy_offers.append(buy_price_i)

    for i in range(num_offers):
        sell_price_i = sell_price * (1 + i * offer_difference)
        sell_offers.append(sell_price_i)

    return buy_offers, sell_offers

def get_balance_usdt():
    print("Fetching USDT balance...")
    balance = exchange.Balances()
    print(f"USDT balance fetched: {balance}")
    return balance.get('USDT', 0.0)

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
            elif result.get('order_status') == 'pending':
                print(f"✅ Buy order at {buy_price} is pending. We will check later.")
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
            elif result.get('order_status') == 'pending':
                print(f"✅ Sell order at {sell_price} is pending. We will check later.")
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

        exchange.CancelAllOpenOrdersForMarket(pair)

        mid_price = get_market_price() 
        if mid_price is None:
            print("❌ Could not get mid price. Skipping order placement.")
            time.sleep(900)
            continue

        buy_offers, sell_offers = create_offers(mid_price, SPREAD_PERCENTAGE, NUM_OFFERS, OFFER_DIFFERENCE)

        if current_usdt_balance > 0 and current_coin_balance > 0:
            place_orders(buy_offers, sell_offers, current_usdt_balance, current_coin_balance)
        else:
            print("⚠️ Not enough balance to place new orders.")

        print("⏳ Waiting for the next cycle...\n")
        time.sleep(900) # Time for make new Orders / Refresh (in Seconds 900 = 15 Minutes)

        current_usdt_balance = get_balance_usdt()
        print(f"💰 Updated USDT balance: {current_usdt_balance}")
