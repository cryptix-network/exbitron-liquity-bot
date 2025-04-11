# Exbitron User API v2 OAS3 - Python 3

This repository contains Python code for interacting with the API of the Exbitron exchange ([exbitron.com](https://exbitron.com)).  
More information about the API endpoints can be found at: [Exbitron API Documentation](https://app.exbitron.com/api-documentation/).  

Additionally, this repository includes an example of a simple liquity bot. It is not a classic trading bot, it will still offer deals based on the settings. 

## Installation

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


## Explanation of the Cryptix Liquidity Bot

The Cryptix Liquidity Bot is designed to automate the process of placing buy and sell orders on the Exbitron exchange. It operates within predefined parameters to maximize trading efficiency and ensure liquidity on the market. The bot performs the following key functions:

    Market Price Fetching: The bot continuously fetches the latest market price for the selected trading pair (e.g., CYTX-USDT). It retrieves the order book data (top 50 bids and asks) to calculate the midpoint price between the best bid and best ask. This mid price serves as a reference for placing orders.

    Order Creation: Based on the calculated market price, the bot creates a series of buy and sell offers. The offers are spread out with a certain percentage (default 5%) between buy and sell orders. The number of orders can be customized, and each successive order price is adjusted with a small price difference (default 0.01), ensuring an optimized price spread.

    Balance Management: The bot starts with an initial amount of USDT (Tether) and coins. It checks and updates the balance regularly. The bot ensures that the balance doesn't exceed predefined maximum limits for both USDT and coin amounts. If the balance reaches the maximum, it will no longer place additional buy or sell orders.

    Order Placement: After calculating the offers, the bot places the orders on the exchange. The buy orders are placed with lower prices, and the sell orders are placed with higher prices. It evenly distributes the available USDT for buy orders and coins for sell orders across multiple offers.

    Error Handling & Rate Limits: The bot includes error handling mechanisms to ensure it continues operating smoothly even when encountering issues like network errors or rate limits imposed by the exchange. If too many requests are made in a short time, the bot will pause for a short period to comply with the rate limits.

    Order Cancellation: Before placing new orders, the bot cancels all previous open orders to ensure the latest orders are the ones being considered by the market. This helps maintain an accurate and up-to-date order book.

    Cycle & Timing: The bot works in cycles, and after completing each cycle, it waits for a defined amount of time (e.g., 15 minutes) before placing new orders. This interval can be adjusted based on trading strategies and market conditions.

The Cryptix Liquidity Bot is a useful tool for providing liquidity and ensuring that buy and sell orders are placed in a manner that maintains a stable market price for the selected trading pair.
