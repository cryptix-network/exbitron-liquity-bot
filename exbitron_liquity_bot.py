import math
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

# Set the amount of USDT and Coin
USDT_AMOUNT = 50.0  # Amount in USDT for buying
COIN_AMOUNT = 50000  # Amount of Coin for selling

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
    # Create buy and sell offers based on the defined parameters
    buy_offers, sell_offers = create_offers(MID_PRICE, SPREAD_PERCENTAGE, NUM_OFFERS, OFFER_DIFFERENCE)

    # Place the orders for buy and sell offers
    place_orders(buy_offers, sell_offers, USDT_AMOUNT, COIN_AMOUNT)

    # Wait for a specified interval before placing the next set of orders
    while True:
        print("Waiting for next cycle...")
        time.sleep(60)  # Adjust the sleep time based on your needs
