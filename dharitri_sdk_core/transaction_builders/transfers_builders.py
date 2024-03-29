from typing import List, Optional, Protocol, Sequence

from dharitri_sdk_core.interfaces import (IAddress, IGasLimit, IGasPrice,
                                            INonce, ITokenPayment,
                                            ITransactionValue)
from dharitri_sdk_core.serializer import arg_to_string
from dharitri_sdk_core.transaction_builders.transaction_builder import (
    ITransactionBuilderConfiguration, TransactionBuilder)


class IDCTTransferConfiguration(ITransactionBuilderConfiguration, Protocol):
    gas_limit_dct_transfer: IGasLimit
    additional_gas_for_dct_transfer: IGasLimit


class IDCTNFTTransferConfiguration(ITransactionBuilderConfiguration, Protocol):
    gas_limit_dct_nft_transfer: IGasLimit
    additional_gas_for_dct_nft_transfer: IGasLimit


class MOAXTransferBuilder(TransactionBuilder):
    def __init__(self,
                 config: ITransactionBuilderConfiguration,
                 sender: IAddress,
                 receiver: IAddress,
                 payment: ITokenPayment,
                 nonce: Optional[INonce] = None,
                 data: Optional[str] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        assert payment.is_moax()
        super().__init__(config, nonce, payment.amount_as_integer, gas_limit, gas_price)
        self.sender = sender
        self.receiver = receiver
        self.data = data

    def _estimate_execution_gas(self) -> IGasLimit:
        return 0

    def _build_payload_parts(self) -> List[str]:
        return [self.data] if self.data else []


class DCTTransferBuilder(TransactionBuilder):
    def __init__(self,
                 config: IDCTTransferConfiguration,
                 sender: IAddress,
                 receiver: IAddress,
                 payment: ITokenPayment,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.gas_limit_dct_transfer = config.gas_limit_dct_transfer
        self.additional_gas_for_dct_transfer = config.additional_gas_for_dct_transfer

        self.sender = sender
        self.receiver = receiver
        self.payment = payment

    def _estimate_execution_gas(self) -> IGasLimit:
        return self.gas_limit_dct_transfer + self.additional_gas_for_dct_transfer

    def _build_payload_parts(self) -> List[str]:
        return [
            "DCTTransfer",
            arg_to_string(self.payment.token_identifier),
            arg_to_string(self.payment.amount_as_integer)
        ]


class DCTNFTTransferBuilder(TransactionBuilder):
    def __init__(self,
                 config: IDCTNFTTransferConfiguration,
                 sender: IAddress,
                 destination: IAddress,
                 payment: ITokenPayment,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.gas_limit_dct_nft_transfer = config.gas_limit_dct_nft_transfer
        self.additional_gas_for_dct_nft_transfer = config.additional_gas_for_dct_nft_transfer

        self.sender = sender
        self.receiver = sender
        self.destination = destination
        self.payment = payment

    def _estimate_execution_gas(self) -> IGasLimit:
        return self.gas_limit_dct_nft_transfer + self.additional_gas_for_dct_nft_transfer

    def _build_payload_parts(self) -> List[str]:
        return [
            "DCTNFTTransfer",
            arg_to_string(self.payment.token_identifier),
            arg_to_string(self.payment.token_nonce),
            arg_to_string(self.payment.amount_as_integer),
            arg_to_string(self.destination)
        ]


class MultiDCTNFTTransferBuilder(TransactionBuilder):
    def __init__(self,
                 config: IDCTNFTTransferConfiguration,
                 sender: IAddress,
                 destination: IAddress,
                 payments: Sequence[ITokenPayment],
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.gas_limit_dct_nft_transfer = config.gas_limit_dct_nft_transfer
        self.additional_gas_for_dct_nft_transfer = config.additional_gas_for_dct_nft_transfer

        self.sender = sender
        self.receiver = sender
        self.destination = destination
        self.payments = payments

    def _estimate_execution_gas(self) -> IGasLimit:
        return (self.gas_limit_dct_nft_transfer + self.additional_gas_for_dct_nft_transfer) * len(self.payments)

    def _build_payload_parts(self) -> List[str]:
        parts = [
            "MultiDCTNFTTransfer",
            arg_to_string(self.destination),
            arg_to_string(len(self.payments))
        ]

        for payment in self.payments:
            parts.extend([
                arg_to_string(payment.token_identifier),
                arg_to_string(payment.token_nonce),
                arg_to_string(payment.amount_as_integer)
            ])

        return parts
