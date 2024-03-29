import pytest

from dharitri_sdk_core.address import Address
from dharitri_sdk_core.errors import (ErrInvalidGasLimitForInnerTransaction,
                                        ErrInvalidRelayerV2BuilderArguments)
from dharitri_sdk_core.testutils.wallets import load_wallets
from dharitri_sdk_core.transaction import Transaction
from dharitri_sdk_core.transaction_builders.relayed_v2_builder import \
    RelayedTransactionV2Builder
from dharitri_sdk_core.transaction_payload import TransactionPayload


class NetworkConfig:
    def __init__(self) -> None:
        self.min_gas_limit = 50_000
        self.gas_per_data_byte = 1_500
        self.gas_price_modifier = 0.01
        self.chain_id = "T"


class TestRelayedV2Builder:
    wallets = load_wallets()
    alice = wallets["alice"]
    bob = wallets["bob"]

    def test_without_arguments(self):
        relayed_builder = RelayedTransactionV2Builder()

        with pytest.raises(ErrInvalidRelayerV2BuilderArguments):
            relayed_builder.build()

    def test_with_inner_tx_gas_limit(self):
        builder = RelayedTransactionV2Builder()
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=Address.from_bech32(self.alice.label),
            receiver=Address.from_bech32("moa1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls29jpxv"),
            gas_limit=10,
            nonce=15,
            data=TransactionPayload.from_str("getContractConfig")
        )
        # version is set to 1 to match the test in sdk-js-core
        inner_tx.version = 1
        inner_tx.signature = self.alice.secret_key.sign(inner_tx.serialize_for_signing())

        builder.set_network_config(network_config)
        builder.set_inner_transaction_gas_limit(10)
        builder.set_inner_transaction(inner_tx)
        builder.set_relayer_address(Address.from_bech32(self.alice.label))

        with pytest.raises(ErrInvalidGasLimitForInnerTransaction):
            builder.build()

    def test_compute_relayed_v2_transaction(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=Address.from_bech32(self.bob.label),
            receiver=Address.from_bech32("moa1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls29jpxv"),
            gas_limit=0,
            nonce=15,
            data=TransactionPayload.from_str("getContractConfig")
        )
        # version is set to 1 to match the test in sdk-js-core
        inner_tx.version = 1
        inner_tx.signature = self.bob.secret_key.sign(inner_tx.serialize_for_signing())

        builder = RelayedTransactionV2Builder()
        builder.set_inner_transaction(inner_tx)
        builder.set_inner_transaction_gas_limit(60_000_000)
        builder.set_relayer_nonce(37)
        builder.set_network_config(network_config)
        builder.set_relayer_address(Address.from_bech32(self.alice.label))

        relayed_tx = builder.build()
        # version is set to 1 to match the test in sdk-js-core
        relayed_tx.version = 1

        relayed_tx.sender = Address.from_bech32(self.alice.label)
        relayed_tx.signature = self.alice.secret_key.sign(relayed_tx.serialize_for_signing())

        assert relayed_tx.nonce == 37
        assert str(relayed_tx.data) == "relayedTxV2@000000000000000000010000000000000000000000000000000000000002ffff@0f@676574436f6e7472616374436f6e666967@e6adf0f39f35ef81824c3314451fddc841d47e3a108a1c19f6c0a62c20d839725c833427fa52bdc8493de7dee617f26392bb753b7ad882fa38110d226a052802"
