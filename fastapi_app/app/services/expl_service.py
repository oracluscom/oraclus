"""
`?data=` (required) → data bits, comma-separated list of (`address`, `balances`, `events`, `mempool`), at least one is required
`?from=` → module list, comma-separated, or `all`, or `default` which is the first module; exactly one module must be specified when paginating past the default page
`?limit=` → `1`, `10`, `100`, `1000`, or `default` which is `10`
`?page=` → if paginating balances: `0`, `ℕ`, or `default` which is `0` (no offset limit); if paginating events or mempool: `0`, `ℕ`, `-0`, `-ℕ`, or `default` which is `-0` (max offset is 100k records); when paginating, `?from=` must contain exactly one of (`balances`, `events`, `mempool`) and may additionaly contain `address`
`?segment=` → date in `YYYY-MM-DD` format; shows events only for this date; when specified, `events` must be present in `?data=`, `mempool` must not be present in `?data=`; drops max offset constraint on `?page=`; exactly one module must be specified in `?from=` even for the default page
`?mixins=` → mixin data, comma-separated list of (`stats`)
`?library=` → library data, comma-separated list of (`blockchains`, `modules`, `currencies`, `extras`, `rates({:list})`)
"""
"""
data
  address
    balances
    events
  balances
    ethereum-main
      ethereum
    ethereum-erc-20: <class 'dict'> (805 items)
    ethereum-erc-721: <class 'dict'> (1000 items)
    ethereum-erc-1155: <class 'dict'> (36 items)
  events
    ethereum-main: <class 'list'> (1000 items)
    ethereum-main
    ethereum-trace: <class 'list'> (82 items)
    ethereum-trace
    ethereum-erc-20: <class 'list'> (1000 items)
    ethereum-erc-20
    ethereum-erc-721: <class 'list'> (1000 items)
    ethereum-erc-721
    ethereum-erc-1155: <class 'list'> (64 items)
    ethereum-erc-1155
library
  blockchains
    ethereum
      modules
  modules
    ethereum-main: <class 'dict'> (16 items)
    ethereum-trace: <class 'dict'> (16 items)
    ethereum-erc-20: <class 'dict'> (16 items)
    ethereum-erc-721: <class 'dict'> (16 items)
    ethereum-erc-1155: <class 'dict'> (16 items)
  currencies: <class 'dict'> (1953 items)
  rates: <class 'dict'> (1537 items)
  extras
    ethereum-main
context
  api
"""
import asyncio
from collections import defaultdict
from contextlib import nullcontext

import aiohttp
import requests

from ..common.decorators import timer_decorator
from ..common.generators import infinite_generator
from ..common.loggers import logger
from ..config import settings

address_test = settings.address_justin_sun
PARAMS = {
    "data": "address,balances,events",
    "from": "all",
    "limit": 1_000,
    "library": "blockchains,modules,currencies,extras,rates(usd)",
}
URL = "https://api.3xpl.com/ethereum/address/{address}"
HEADERS = {"Authorization": f"Bearer {settings.EXPL_COM_API_KEY}"}


###########################################################################
@timer_decorator
def sample_run():
    date_limit = "2023-01-01"
    return asyncio.run(get_address_erc20_txns_details(address_test, date_limit))


###########################################################################
@timer_decorator
def dry_request(url, params=None, headers=None):
    return requests.get(url, params=params, headers=headers)


def request_address_erc20_events(address=address_test, params=PARAMS, headers=HEADERS):
    url_formatted = URL.format(address=address)
    return requests.get(url_formatted, params=params, headers=headers)


###########################################################################
async def fetch_async(session, url, params=None, headers=None, semaphore=None):
    async with semaphore if semaphore else nullcontext():
        async with session.get(url, params=params, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"{url} | {response.status} | {response.reason} | {response.text}")
                return None


###########################################################################
async def fetch_recent_erc20_txns_list(session, address, page_limit=1_000, result_limit=1_000, date_limit=None):
    url = "https://api.3xpl.com/ethereum/address/{address}"
    params = {
        "data": "address,events",
        "from": "ethereum-erc-20",
        "limit": page_limit,
        "library": "blockchains,modules,currencies,extras,rates(usd)",
        "page": "-0",
    }
    url_formatted = url.format(address=address)
    txns_set = set()
    for page in infinite_generator():
        params["page"] = f"-{page}"
        data = await fetch_async(session, url_formatted, params=params, headers=HEADERS)
        if not data:
            break
        txns_events = data["data"]["events"]["ethereum-erc-20"]

        # if we have reached desired date limit
        if date_limit and txns_events[-1]["time"] < date_limit:
            txns_list = [i["transaction"] for i in txns_events if i["time"] >= date_limit]
            txns_set = txns_set.union(set(txns_list))
            break

        txns_list = [i["transaction"] for i in txns_events]
        txns_set = txns_set.union(set(txns_list))
        # if we have reached last page
        if len(txns_list) < page_limit:
            break
        # if we have reached desired limit
        if not date_limit and len(txns_set) >= result_limit:
            break

    result = list(txns_set)
    return result


async def fetch_single_tx_details(session, tx, semaphore):
    url = "https://api.3xpl.com/ethereum/transaction/{tx}"
    url_formatted = url.format(tx=tx)
    params = {
        "data": "transaction,events",
        "from": "ethereum-erc-20",
        "limit": 1000,
        "page": 0,
        "library": "currencies",
    }
    data = await fetch_async(session, url_formatted, params=params, headers=HEADERS, semaphore=semaphore)
    return data


async def get_tx_detail_for_txns_list_using_sliding_window(session, txns_list, max_concurrent=10):
    results = []
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_and_process(tx):
        try:
            result = await fetch_single_tx_details(session, tx, semaphore)
            results.append(result)
        except Exception as e:
            logger.error(f"Error fetching {tx=}: {e}")

    tasks = [fetch_and_process(tx) for tx in txns_list]
    await asyncio.gather(*tasks)

    return results


async def get_erc20_txns_details(address, page_limit=1_000, result_limit=1_000, date_limit=None):
    async with aiohttp.ClientSession() as session:
        txns_list = await fetch_recent_erc20_txns_list(
            session,
            address=address,
            page_limit=page_limit,
            result_limit=result_limit,
            date_limit=date_limit,
        )
        responses = await get_tx_detail_for_txns_list_using_sliding_window(session, txns_list, max_concurrent=10)
        return txns_list, responses


async def get_erc20_txns_list_only(address=address_test, page_limit=10, result_limit=20):
    async with aiohttp.ClientSession() as session:
        txns_list = await fetch_recent_erc20_txns_list(
            session,
            address=address,
            page_limit=page_limit,
            result_limit=result_limit,
        )
        return txns_list


def currency_to_token_address(currency):
    return currency.split("/")[1]


def process_transactions(responses, address, token_address_info_dict):
    d = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    for tx in responses:
        date = tx["data"]["transaction"]["time"].split("T")[0]
        for event in tx["data"]["events"]["ethereum-erc-20"]:
            if event["address"] == address:
                token_address = currency_to_token_address(event["currency"])
                currency = event["currency"]
                decimals = 18
                token = ""
                if currency in tx["library"]["currencies"]:
                    token = tx["library"]["currencies"][currency]["symbol"]
                    decimals = tx["library"]["currencies"][currency]["decimals"]
                elif token_address in token_address_info_dict:
                    print(f"Token {token_address} not in tx['library']['currencies'] but in token_address_info_dict")
                    token = token_address_info_dict[token_address]["symbol"]

                if token == "":
                    continue
                if decimals == 0:
                    logger.warning(f"{token=} | {decimals=}")

                amount = abs(int(event["effect"]) * 10**-decimals)
                if "-" in event["effect"]:
                    d[date]["spend"][token] += amount
                    if token_address in token_address_info_dict:
                        d[date]["usd"]["spend"] += amount * float(token_address_info_dict[token_address]["usd"])
                else:
                    d[date]["receive"][token] += amount
                    if token_address in token_address_info_dict:
                        d[date]["usd"]["receive"] += amount * float(token_address_info_dict[token_address]["usd"])
    return d


###############################################################################
async def get_address_erc20_txns_details(address, date_limit=None):
    async with aiohttp.ClientSession() as session:
        txns_list = await fetch_recent_erc20_txns_list(
            session,
            address,
            page_limit=1_000,
            result_limit=1_000,
            date_limit=date_limit,
        )
        responses = await get_tx_detail_for_txns_list_using_sliding_window(session, txns_list, max_concurrent=10)
        token_address_list = sorted(
            set(
                currency_to_token_address(i["currency"])
                for j in responses
                for i in j["data"]["events"]["ethereum-erc-20"]
            )
        )
        token_address_info_dict = {}  # service is not included
        result = process_transactions(responses, address, token_address_info_dict)
        result_list = [
            {
                "date": date,
                "spend_usd": data.get("usd", {}).get("spend", 0),
                "receive_usd": data.get("usd", {}).get("receive", 0),
                "spend": data["spend"] if "spend" in data else {},
                "receive": data["receive"] if "receive" in data else {},
            }
            for date, data in result.items()
        ]
        sorted_result = sorted(result_list, key=lambda x: x["date"])

    return sorted_result
