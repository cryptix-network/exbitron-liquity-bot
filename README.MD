# Exbitron User API v2 OAS3 - Python 3

This repository contains Python code for interacting with the API of the Exbitron exchange ([exbitron.com](https://exbitron.com)).  
More information about the API endpoints can be found at: [Exbitron API Documentation](https://app.exbitron.com/api-documentation/).  

Additionally, this repository includes an example of a simple liquity bot. It is not a classic trading bot, it will still offer deals based on the settings. 

## Exe Version

Edit the config file using a text editor and add the Exbitron API. Then set the values ​​for quantity, spread, and orders.
That's it, run the executable.


## Python Version Installation

To run the example, you need to install the `requests` package:  

```sh
pip3 install requests
```

## Running the Trading Bot

To start the bot, use:

```
python3 exbitron_liquity_bot.py
```

## API Key Setup

Before running the bot, update the API keys in the code under the variables section.
API keys can be generated from the Exbitron web platform in the Settings or Profile section after enabling 2FA.

## Usage
The use of this software has not been extensively tested. Use is at your own risk; we assume no liability for its use. This software is provided free of charge and is open source.


## Cryptix Liquidity Trading Bot for Exbitron

The Cryptix Liquidity Bot automatically places buy and sell orders on Exbitron to maintain market liquidity and to reduce the trading spread for a fair market. 

Here’s how it works:
Key Config Values:  (can be customized to your needs, with more or less spread. More or less USDT/CYTX, etc. )

- START_USDT_AMOUNT: Initial USDT balance (e.g., 100 USDT)
- START_COIN_AMOUNT: Initial coin balance (e.g., 20,000 coins)
- MAX_USDT_AMOUNT: Max USDT the bot can hold (e.g., 125 USDT)
- MAX_COIN_AMOUNT: Max coins the bot can hold (e.g., 50,000 coins)
- SPREAD_PERCENTAGE: Price spread between buy and sell orders (e.g., 5%)
- NUM_OFFERS: Number of buy/sell orders (e.g., 20 orders)
- OFFER_DIFFERENCE: Price difference between successive offers (e.g., 0.01)

Workflow:
- Fetches the latest market price (mid price between the best bid and ask).
- Creates buy and sell offers with a spread based on the market price.
- Places buy orders at lower prices and sell orders at higher prices.
- Ensures balance stays within the max limits for both USDT and coins.
-  Cancels old orders before placing new ones.
-  Repeats the cycle every 15 minutes, updating balances and adjusting orders.

What the liquidity/trading bot DOES NOT do:
- It does not buy or sell coins itself -> wash trading / fake volume
- It does not create fake offers / jump-away orders

It uses real buy/sell offers (or both, depending on the settings), which are updated every 15 minutes (or depending on the settings). It is designed to provide a stable market and reduce spreads. Useful for market makers and spread traders or for an effective purchase/sale of coins.

Free to use and no Dev Fees

Must be run with Python. We will provide an executable version without Python soon. 
All you need is an Exbitron API, which you can create for free in your account. And Account Balances.

The bot isn't yet field-tested. Therefore, it should be tested and observed with small values ​​first, especially due to the maximum order values. This hasn't been tested yet. It's also important to note that the bot deletes and resets all orders every 15 minutes, according to the settings. This includes manual orders.
I therefore recommend creating a new account with a fixed USDT amount to Test. This way, even manual trading won't cause any conflicts.

