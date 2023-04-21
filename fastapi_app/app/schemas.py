from typing import Dict, List

from eth_utils import is_hex_address
from pydantic import BaseModel
from pydantic import validator

from .common.exceptions import InvalidEthereumAddress


def is_valid_ethereum_address(address: str) -> bool:
    return is_hex_address(address)


class BlockchainAddressSchema(BaseModel):
    address: str

    @validator("address")
    def validate_blockchain_address(cls, address):
        if not is_valid_ethereum_address(address):
            raise InvalidEthereumAddress("Invalid ethereum address")
        return address


class TokenAmounts(BaseModel):
    spend: Dict[str, float] = {}
    receive: Dict[str, float] = {}


class TokenAmountsInUSD(BaseModel):
    spend_usd: float = 0.0
    receive_usd: float = 0.0
    spend: Dict[str, float] = {}
    receive: Dict[str, float] = {}

    @validator("spend_usd", "receive_usd", pre=True)
    def format_float(cls, value):
        return float(f"{value:.2f}")


class DateTokenAmounts(TokenAmounts):
    date: str


class AddressData(BaseModel):
    address_data: List[DateTokenAmounts]
