from pathlib import Path

from dharitri_sdk_core.address import Address
from dharitri_sdk_core.constants import CONTRACT_DEPLOY_ADDRESS
from dharitri_sdk_core.transaction_intents_factories.smart_contract_transaction_intents_factory import \
    SmartContractTransactionIntentsFactory
from dharitri_sdk_core.transaction_intents_factories.transaction_intents_factory_config import \
    TransactionIntentsFactoryConfig


class TestSmartContract:
    config = TransactionIntentsFactoryConfig("D")
    factory = SmartContractTransactionIntentsFactory(config)

    def test_create_transaction_intent_for_deploy(self):
        sender = Address.from_bech32("moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8")
        contract = Path(__file__).parent.parent / "testutils" / "testdata" / "adder.wasm"
        gas_limit = 6000000
        args = [0]

        intent = self.factory.create_transaction_intent_for_deploy(
            sender=sender,
            bytecode=contract,
            gas_limit=gas_limit,
            arguments=args
        )

        assert intent.sender == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert intent.receiver == CONTRACT_DEPLOY_ADDRESS
        assert intent.data
        assert intent.gas_limit == 6000000 + 50000 + 1500 * len(intent.data)
        assert intent.value == 0

    def test_create_transaction_intent_for_execute(self):
        sender = Address.from_bech32("moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8")
        contract = Address.from_bech32("moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9")
        function = "add"
        gas_limit = 6000000
        args = [7]

        intent = self.factory.create_transaction_intent_for_execute(
            sender=sender,
            contract_address=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args
        )

        assert intent.sender == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert intent.receiver == contract.bech32()
        assert intent.gas_limit == 6059000
        assert intent.data
        assert intent.data.decode() == "add@07"
        assert intent.value == 0

    def test_create_transaction_intent_for_upgrade(self):
        sender = Address.from_bech32("moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8")
        contract_address = Address.from_bech32("moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9")
        contract = Path(__file__).parent.parent / "testutils" / "testdata" / "adder.wasm"
        gas_limit = 6000000
        args = [0]

        intent = self.factory.create_transaction_intent_for_upgrade(
            sender=sender,
            contract=contract_address,
            bytecode=contract,
            gas_limit=gas_limit,
            arguments=args
        )

        assert intent.sender == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert intent.receiver == "moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9"
        assert intent.data
        assert intent.data.decode().startswith("upgradeContract@")
        assert intent.gas_limit == 6000000 + 50000 + 1500 * len(intent.data)
        assert intent.value == 0
