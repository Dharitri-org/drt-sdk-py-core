from dataclasses import dataclass

from dharitri_sdk_core.address import Address
from dharitri_sdk_core.interfaces import (IAddress, IChainID, IGasPrice,
                                            ITransactionValue)


@dataclass
class DefaultTransactionBuildersConfiguration:
    chain_id: IChainID
    min_gas_price: IGasPrice = 1000000000
    min_gas_limit = 50000
    gas_limit_per_byte = 1500

    issue_cost: ITransactionValue = 50000000000000000
    gas_limit_dct_issue = 60000000
    gas_limit_dct_transfer = 200000
    gas_limit_dct_nft_transfer = 200000
    additional_gas_for_dct_transfer = 100000
    additional_gas_for_dct_nft_transfer = 800000

    dct_contract_address: IAddress = Address.from_bech32("moa1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls29jpxv")
    deployment_address: IAddress = Address.from_bech32("moa1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqhsx6tv")
