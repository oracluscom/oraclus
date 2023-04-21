import datetime

from fastapi import APIRouter, Depends, HTTPException

from ..common.exceptions import InvalidBlockchainAddress
from ..common.loggers import logger
from ..schemas import AddressData, BlockchainAddressSchema
from ..services import expl_service

router = APIRouter()


@router.get("/erc20_txns_details/{address}", response_model=AddressData)
async def get_eth_erc20_txns_details_by_address(address: str = Depends(BlockchainAddressSchema)):
    try:
        month_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

        address_str = address.address
        address_data = await expl_service.get_address_erc20_txns_details(address_str, date_limit=month_ago)

        # Create an instance of AddressData
        address_data_instance = AddressData(address_data=address_data)

        return address_data_instance
    except InvalidBlockchainAddress:
        raise HTTPException(status_code=400, detail="Invalid blockchain address")
