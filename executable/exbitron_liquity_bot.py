import sys
import time
import configparser
import exbitron_exchange_api as exchange
import asyncio
import websockets
import threading
import os

# ========== INFO ==========
# @Cryptis 
# https://github.com/cryptix-network/exbitron-liquity-bot
#


sys.stdout.reconfigure(encoding='utf-8')

# ========== CONFIG ==========

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

pair = 'CPAY-USDT'

LOG_FILE_PATH = 'cryptix_bot.txt'

# ========== LOGGING FUNCTION ==========

def log_to_file(message):
    if os.path.exists(LOG_FILE_PATH):
        os.remove(LOG_FILE_PATH)
    
    with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log_file:
        log_file.write(message + '\n')

# ========== WEBSOCKET SERVER ==========

clients = set()

async def send_to_clients(message):
    log_to_file(message)
    
    for client in clients:
        try:
            await client.send(message)
        except Exception as e:
            print(f"❌ Error sending to client: {e}")
    print(message)

async def websocket_handler(websocket, path):
    print("🌐 WebSocket client connected")
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)
        print("❌ WebSocket client disconnected")

async def start_websocket_server():
    server = await websockets.serve(websocket_handler, 'localhost', 8765)
    print("WebSocket Server running on ws://localhost:8765/")
    await server.wait_closed()

def run_websocket_server():
    asyncio.run(start_websocket_server())

ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
ws_thread.start()

# ========== TRADING LOGIC ==========

async def get_market_price():
    orderbook = exchange.GetOrderBook(pair, depth='50')
    if 'error' in orderbook:
        await send_to_clients(f"❌ Error fetching the order book: {orderbook['error']}")
        return None

    best_bid = max((float(order[0]) for order in orderbook['bids']), default=None)
    best_ask = min((float(order[0]) for order in orderbook['asks']), default=None)

    if best_bid is None or best_ask is None:
        await send_to_clients("❌ No valid bid or ask price found.")
        return None

    mid_price = (best_bid + best_ask) / 2
    await send_to_clients(f"Best Bid: {best_bid}, Best Ask: {best_ask}, Mid Price: {mid_price}")
    return mid_price

async def create_offers(mid_price, spread_percentage, num_offers, offer_difference):
    buy_offers = []
    sell_offers = []

    spread = mid_price * (spread_percentage / 100.0)
    buy_price = mid_price - spread / 2
    sell_price = mid_price + spread / 2

    await send_to_clients(f"Creating offers: Mid price = {mid_price}, Spread = {spread}, Buy = {buy_price}, Sell = {sell_price}")

    for i in range(num_offers):
        buy_offers.append(buy_price * (1 - i * offer_difference))
        sell_offers.append(sell_price * (1 + i * offer_difference))

    return buy_offers, sell_offers

async def get_balance_usdt():
    await send_to_clients("Fetching USDT balance...")
    balance = exchange.Balances()
    usdt_balance = next((item['balance'] for item in balance['user']['currencies'] if item['id'] == 'USDT'), 0.0)
    await send_to_clients(f"USDT balance: {usdt_balance}")
    return usdt_balance

async def get_balance_coin():
    await send_to_clients("Fetching CPAY balance...")
    balance = exchange.Balances()
    coin_balance = next((item['balance'] for item in balance['user']['currencies'] if item['id'] == 'CPAY'), 0.0)
    await send_to_clients(f"CPAY balance: {coin_balance}")
    return coin_balance

async def place_orders(buy_offers, sell_offers, usdt_amount, coin_amount):
    await send_to_clients(f"Placing {len(buy_offers)} buy and {len(sell_offers)} sell orders...")

    buy_amount_per_order = usdt_amount / len(buy_offers)
    sell_amount_per_order = coin_amount / len(sell_offers)

    # Placing Buy Orders
    for buy_price in buy_offers:
        try:
            await send_to_clients(f"Placing BUY @ {buy_price}")
            result = exchange.Order(buy_amount_per_order / buy_price, pair, buy_price, 'buy', 'limit')

            if result.get('hasError') or result.get('status') != 'OK':
                await send_to_clients(f"❌ Failed to place buy order at {buy_price}. Error: {result}")
            else:
                await send_to_clients(f"✅ Placed buy order at {buy_price}")
        except Exception as e:
            await send_to_clients(f"❌ Buy order error: {e}")
            if "Too many requests" in str(e):
                await asyncio.sleep(10) 
        await asyncio.sleep(0.1)

    # Placing Sell Orders
    for sell_price in sell_offers:
        try:
            await send_to_clients(f"Placing SELL @ {sell_price}")
            result = exchange.Order(sell_amount_per_order, pair, sell_price, 'sell', 'limit')

            if result.get('hasError') or result.get('status') != 'OK':
                await send_to_clients(f"❌ Failed to place sell order at {sell_price}. Error: {result}")
            else:
                await send_to_clients(f"✅ Placed sell order at {sell_price}")
        except Exception as e:
            await send_to_clients(f"❌ Sell order error: {e}")
            if "Too many requests" in str(e):
                await asyncio.sleep(10) 
        await asyncio.sleep(0.1)

async def show_ascii_art():
    await send_to_clients(r"""
   _____ _______     _______ _______ _______   __
  / ____|  __ \ \   / /  __ \__   __|_   _\ \ / /
 | |    | |__) \ \_/ /| |__) | | |    | |  \ V / 
 | |    |  _  / \   / |  ___/  | |    | |   > <  
 | |____| | \ \  | |  | |      | |   _| |_ / . \ 
  \_____|_|  \_\ |_|  |_|      |_|  |_____/_/ \_\
    """)

# ========== MAIN LOOP ==========

async def main():
    await show_ascii_art()

    current_usdt_balance = START_USDT_AMOUNT
    current_coin_balance = START_COIN_AMOUNT

    while True:
        await send_to_clients("\n🔄 Starting new cycle...")

        if current_usdt_balance > MAX_USDT_AMOUNT:
            current_usdt_balance = MAX_USDT_AMOUNT
            await send_to_clients(f"⚠️ USDT capped at {MAX_USDT_AMOUNT}")
        if current_coin_balance > MAX_COIN_AMOUNT:
            current_coin_balance = MAX_COIN_AMOUNT
            await send_to_clients(f"⚠️ CPAY capped at {MAX_COIN_AMOUNT}")

        mid_price = await get_market_price()
        if mid_price is None:
            await send_to_clients("❌ Skipping cycle (no mid price).")
            await asyncio.sleep(SLEEP_TIME)
            continue

        exchange.CancelAllOpenOrdersForMarket(pair)
        await send_to_clients("🧹 Orders canceled. Waiting 10 seconds...")
        await asyncio.sleep(10)

        updated_usdt_balance = await get_balance_usdt()
        updated_coin_balance = await get_balance_coin()

        await send_to_clients(f"💰 Updated USDT: {updated_usdt_balance}")
        await send_to_clients(f"💰 Updated CPAY: {updated_coin_balance}")

        if current_usdt_balance > 0 and current_coin_balance > 0:
            buy_offers, sell_offers = await create_offers(mid_price, SPREAD_PERCENTAGE, NUM_OFFERS, OFFER_DIFFERENCE)
            await place_orders(buy_offers, sell_offers, current_usdt_balance, current_coin_balance)
        else:
            await send_to_clients("⚠️ Not enough balance to place orders.")

        await send_to_clients(f"⏳ Waiting {SLEEP_TIME // 60} minutes...")
        await send_to_clients(f"⏳ Next cycle: waiting {SLEEP_TIME // 60} minutes...")

        for remaining in range(SLEEP_TIME, 0, -1):
            mins, secs = divmod(remaining, 60)
            print(f"\r⏳ Next cycle in: {mins:02d}:{secs:02d}", end='', flush=True)
            await asyncio.sleep(1)

        print()

# Run the main loop with asyncio
if __name__ == '__main__':
    if os.path.exists(LOG_FILE_PATH):
        os.remove(LOG_FILE_PATH)

    asyncio.run(main())
