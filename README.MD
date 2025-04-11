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

