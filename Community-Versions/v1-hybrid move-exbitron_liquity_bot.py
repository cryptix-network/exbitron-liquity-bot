### User Version: BlueTooth

### Comment:
### I call this approach a hybrid move strategy. It resets orders based on two key conditions: either when the price changes by a defined percentage, or when a specific timer runs out.
###  I’ve tested this logic using a backtest setup with a converted TradingView script. Adding the percentage-based price movement as a trigger helps the bot react more intelligently to sudden market swings — especially during pump and dump situations.
### On the other hand, if the price range becomes too narrow and there’s not enough movement, the bot will go into a sleep state based on the timer, avoiding unnecessary actions in low-volatility conditions.

### Please note:
### Community versions of the bot have been provided by independent users. They are modified versions of the original, with new or modified features.
### We have not tested these versions, so use with caution.

import time
import exbitron_exchange_api as exchange

# Settings for pair and API token
pair = 'CPAY-USDT'
exchange.TOKEN = 'YOUR_API_KEY_HERE'

# Initial bot settings
START_USDT_AMOUNT = 100.0
START_COIN_AMOUNT = 20000.0
MAX_USDT_AMOUNT = 125.0
MAX_COIN_AMOUNT = 50000.0
SPREAD_PERCENTAGE = 5.0
NUM_OFFERS = 20
OFFER_DIFFERENCE = 0.01
PRICE_CHANGE_THRESHOLD = 1.0  # Percentage change required to trigger a reset

# Function to get the latest market price
def get_market_price():
    orderbook = exchange.GetOrderBook(pair, depth='50')

    if 'error' in orderbook:
        print(f"❌ Error fetching the order book: {orderbook['error']}")
        return None

    best_bid = None
    best_ask = None

    # Find the best bid price
    for order in orderbook['bids']:
        if best_bid is None or float(order[0]) > best_bid:
            best_bid = float(order[0])

    # Find the best ask price
    for order in orderbook['asks']:
        if best_ask is None or float(order[0]) < best_ask:
            best_ask = float(order[0])

    if best_bid is None or best_ask is None:
        print("❌ No valid bid or ask price found.")
        return None

    mid_price = (best_bid + best_ask) / 2
    print(f"Best Bid: {best_bid}, Best Ask: {best_ask}, Mid Price: {mid_price}")
    return mid_price

# Function to create buy and sell offers based on the market price
def create_offers(mid_price, spread_percentage, num_offers, offer_difference):
    buy_offers = []
    sell_offers = []

    spread = mid_price * (spread_percentage / 100.0)
    buy_price = mid_price - spread / 2
    sell_price = mid_price + spread / 2

    print(f"Creating offers: Mid price = {mid_price}, Spread = {spread}, Buy price = {buy_price}, Sell price = {sell_price}")

    # Create buy offers with decreasing prices
    for i in range(num_offers):
        buy_price_i = buy_price * (1 - i * offer_difference)
        buy_offers.append(buy_price_i)

    # Create sell offers with increasing prices
    for i in range(num_offers):
        sell_price_i = sell_price * (1 + i * offer_difference)
        sell_offers.append(sell_price_i)

    return buy_offers, sell_offers

# Function to get USDT balance
def get_balance_usdt():
    print("Fetching USDT balance...")
    balance = exchange.Balances()
    usdt_balance = next((item['balance'] for item in balance['user']['currencies'] if item['id'] == 'USDT'), 0.0)
    print(f"USDT balance fetched: {usdt_balance}")
    return usdt_balance

# Function to get Coin (CPAY) balance
def get_balance_coin():
    print("Fetching Coin balance...")
    balance = exchange.Balances()
    coin_balance = next((item['balance'] for item in balance['user']['currencies'] if item['id'] == 'CPAY'), 0.0)  
    print(f"Coin balance fetched: {coin_balance}")
    return coin_balance

# Function to place buy and sell orders
def place_orders(buy_offers, sell_offers, usdt_amount, coin_amount):
    print(f"Placing orders with {len(buy_offers)} buy and {len(sell_offers)} sell offers...")
    buy_amount_per_order = usdt_amount / len(buy_offers)
    sell_amount_per_order = coin_amount / len(sell_offers)

    # Place buy orders
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

    # Place sell orders
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

# Function to display ASCII art
def show_ascii_art():
    print("""
   _____ _______     _______ _______ _______   __
  / ____|  __ \ \   / /  __ \__   __|_   _\ \ / /
 | |    | |__) \ \_/ /| |__) | | |    | |  \ V / 
 | |    |  _  / \   / |  ___/  | |    | |   > <  
 | |____| | \ \  | |  | |      | |   _| |_ / . \ 
  \_____|_|  \_\ |_|  |_|      |_|  |_____/_/ \_\
                                                 
    """)

# Function to check if the price has changed significantly
def has_price_changed(last_price, current_price, threshold_percentage):
    price_change = ((current_price - last_price) / last_price) * 100
    return abs(price_change) >= threshold_percentage

if __name__ == '__main__':
    show_ascii_art()

    current_usdt_balance = START_USDT_AMOUNT
    current_coin_balance = START_COIN_AMOUNT
    last_price = None

    while True:
        print("\n🔄 Starting new cycle...")

        # Get latest market price
        mid_price = get_market_price()
        if mid_price is None:
            print("❌ Could not get mid price. Skipping order placement.")
            time.sleep(60)
            continue

        # Set initial price if this is the first run
        if last_price is None:
            last_price = mid_price
            print("⏳ First run, setting initial price baseline.")
            time.sleep(60)
            continue

        # Check if the price has changed significantly
        price_changed = has_price_changed(last_price, mid_price, PRICE_CHANGE_THRESHOLD)

        if price_changed:
            print(f"🔁 Price changed > {PRICE_CHANGE_THRESHOLD}%, resetting orders.")
            last_price = mid_price

            # Cap balances
            if current_usdt_balance > MAX_USDT_AMOUNT:
                current_usdt_balance = MAX_USDT_AMOUNT
            if current_coin_balance > MAX_COIN_AMOUNT:
                current_coin_balance = MAX_COIN_AMOUNT

            # Cancel & re-place orders
            exchange.CancelAllOpenOrdersForMarket(pair)
            time.sleep(10)

            updated_usdt_balance = get_balance_usdt()
            updated_coin_balance = get_balance_coin()

            if updated_usdt_balance > 0 and updated_coin_balance > 0:
                buy_offers, sell_offers = create_offers(mid_price, SPREAD_PERCENTAGE, NUM_OFFERS, OFFER_DIFFERENCE)
                place_orders(buy_offers, sell_offers, updated_usdt_balance, updated_coin_balance)
            else:
                print("⚠️ Not enough balance to place new orders.")

        else:
            print(f"⏸️ No significant price change. Skipping reset.")

        # Wait 15 minutes for the next cycle
        print("⏳ Waiting 15 minutes...")
        for remaining in range(900, 0, -1):
            mins, secs = divmod(remaining, 60)
            time_format = f"{mins:02d}:{secs:02d}"
            print(f"\r⏳ Next cycle in: {time_format}", end="")
            time.sleep(1)
