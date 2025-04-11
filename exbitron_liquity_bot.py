import time
import exbitron_exchange_api as exchange

###
### LIQUIDITY BOT FOR BUY AND SELL ORDERS ###
###

pair = 'CYTX-USDT'
pairS = pair.split('-')

# PUT HERE Your API Token created by Exbitron web app
exchange.TOKEN = ''

# Set the middle price (this will be the center point between buy and sell)
MID_PRICE = 0.0005  # Example middle price (this is between buy and sell price)

# Set the start values for USDT and Coin
START_USDT_AMOUNT = 50.0  # Starting amount in USDT for buying
START_COIN_AMOUNT = 50000  # Starting amount of Coin for selling

# Set the maximum amounts for USDT and Coin (maximums that will never be exceeded)
MAX_USDT_AMOUNT = 100.0  # Max USDT that can be used (e.g., never use more than 100 USDT)
MAX_COIN_AMOUNT = 50000  # Max Coin that can be sold (e.g., never sell more than 50000 Coins)

# Set the spread (e.g., 10% spread)
SPREAD_PERCENTAGE = 10.0

# Set the number of offers (e.g., 100 offers)
NUM_OFFERS = 100

# Set the difference between each offer (e.g., 0.5% difference between each offer)
OFFER_DIFFERENCE = 0.005  # 0.5% difference between offers


# Function to create buy and sell offers based on the middle price, spread, and other parameters
def create_offers(mid_price, spread_percentage, num_offers, offer_difference):
    buy_offers = []
    sell_offers = []

    # Calculate the spread
    spread = mid_price * (spread_percentage / 100.0)

    # Calculate the first buy and sell offer prices
    buy_price = mid_price - spread / 2
    sell_price = mid_price + spread / 2

    # Create the buy offers
    for i in range(num_offers):
        buy_price_i = buy_price * (1 - i * offer_difference)
        buy_offers.append(buy_price_i)

    # Create the sell offers
    for i in range(num_offers):
        sell_price_i = sell_price * (1 + i * offer_difference)
        sell_offers.append(sell_price_i)

    return buy_offers, sell_offers


# Function to get the available USDT balance from your account
def get_balance_usdt():
    # Here you retrieve your USDT balance from the exchange
    balance = exchange.Balances()  # Get the balance info
    return balance['USDT']  # Return the available USDT balance


# Function to place orders
def place_orders(buy_offers, sell_offers, usdt_amount, coin_amount):
    buy_amount_per_order = usdt_amount / len(buy_offers)
    sell_amount_per_order = coin_amount / len(sell_offers)

    # Place buy orders
    for buy_price in buy_offers:
        order_status = exchange.Order(buy_amount_per_order, pairS[1], buy_price, 'buy', 'limit')
        if order_status is None or order_status['status'] != True or order_status['order_status'] != 'open':
            print(f"Failed to place buy order at {buy_price}")
            continue
        print(f"Placed buy order at {buy_price}")

    # Place sell orders
    for sell_price in sell_offers:
        order_status = exchange.Order(sell_amount_per_order, pairS[0], sell_price, 'sell', 'limit')
        if order_status is None or order_status['status'] != True or order_status['order_status'] != 'open':
            print(f"Failed to place sell order at {sell_price}")
            continue
        print(f"Placed sell order at {sell_price}")


if __name__ == '__main__':
    # Get the initial balance for USDT (you can change the initial amount if needed)
    current_usdt_balance = START_USDT_AMOUNT
    current_coin_balance = START_COIN_AMOUNT

    while True:
        # Ensure that USDT used does not exceed the maximum allowed amount
        if current_usdt_balance > MAX_USDT_AMOUNT:
            print(f"USDT balance exceeds the maximum limit of {MAX_USDT_AMOUNT}. Reducing to max limit.")
            current_usdt_balance = MAX_USDT_AMOUNT
        
        # Ensure that coins sold do not exceed the maximum allowed amount
        if current_coin_balance > MAX_COIN_AMOUNT:
            print(f"Coin balance exceeds the maximum limit of {MAX_COIN_AMOUNT}. Reducing to max limit.")
            current_coin_balance = MAX_COIN_AMOUNT

        # Create buy and sell offers based on the defined parameters
        buy_offers, sell_offers = create_offers(MID_PRICE, SPREAD_PERCENTAGE, NUM_OFFERS, OFFER_DIFFERENCE)

        # If there is enough USDT to place buy orders, place the orders
        if current_usdt_balance > 0:
            place_orders(buy_offers, sell_offers, current_usdt_balance, current_coin_balance)
        else:
            print("Not enough USDT to place buy orders.")

        # Wait for a specified interval before placing the next set of orders
        print("Waiting for next cycle...")
        time.sleep(60)  # Adjust the sleep time based on your needs

        # After each cycle, get the new balance of USDT (which includes proceeds from selling coins)
        current_usdt_balance = get_balance_usdt()
        print(f"Current USDT balance: {current_usdt_balance}")
