# Ethereum Address ERC20 Transaction Analyzer

## Overview

This project is a part of the methods used in [oraclus.com](https://www.oraclus.com/) analytical tool to assess Ethereum blockchain address ERC20 transactions, either from a given time period or a transaction number limit. The analyzer fetches transaction data from the Ethereum blockchain and processes it to provide valuable insights into the activity of a specific Ethereum address.

## TLDR 
```
cp .env.sample .env
# add your 3xpl_com_api_key to .env file 
make up 
curl -X GET http://localhost:8000/api/ethereum/erc20/erc20_txns_details/0x3ddfa8ec3052539b6c9549f12cea2c295cff5296 -H 'accept: application/json'
```

## Features

- Fetch Ethereum address ERC20 transaction data from the Ethereum blockchain.
- Analyze transaction data based on a specified time period or a transaction number limit.
- Filter transactions by token types and value thresholds.
- Generate analytical reports on transaction patterns and trends.
- Export transaction data and analysis results in various formats (CSV, JSON, etc.).
- Easily integrate with the [oraclus.com](https://www.oraclus.com/) analytical tool for further analysis.

## Requirements

To use this project, you will need an API key from [3xpl.com](https://www.3xpl.com/). Sign up for an account and obtain the API key from their website.

## Setup

1. Clone this repository to your local machine.
2. Install the required dependencies.
3. Set up the required environment variables, including the API key from 3xpl.com.
4. Run the project and analyze Ethereum address ERC20 transactions.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
