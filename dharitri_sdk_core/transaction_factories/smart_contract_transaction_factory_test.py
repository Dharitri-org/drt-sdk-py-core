from pathlib import Path

from dharitri_sdk_core.address import Address
from dharitri_sdk_core.constants import CONTRACT_DEPLOY_ADDRESS
from dharitri_sdk_core.tokens import Token, TokenComputer, TokenTransfer
from dharitri_sdk_core.transaction_factories.smart_contract_transactions_factory import \
    SmartContractTransactionsFactory
from dharitri_sdk_core.transaction_factories.transactions_factory_config import \
    TransactionsFactoryConfig


class TestSmartContractTransactionsFactory:
    config = TransactionsFactoryConfig("D")
    factory = SmartContractTransactionsFactory(config, TokenComputer())

    def test_create_transaction_for_deploy(self):
        sender = Address.new_from_bech32("moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8")
        contract = Path(__file__).parent.parent / "testutils" / "testdata" / "adder.wasm"
        gas_limit = 6000000
        args = [0]

        transaction = self.factory.create_transaction_for_deploy(
            sender=sender,
            bytecode=contract,
            gas_limit=gas_limit,
            arguments=args
        )

        assert transaction.sender == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert transaction.receiver == CONTRACT_DEPLOY_ADDRESS
        assert transaction.data
        assert transaction.gas_limit == gas_limit
        assert transaction.value == 0

    def test_create_transaction_for_execute_no_transfer(self):
        sender = Address.new_from_bech32("moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8")
        contract = Address.new_from_bech32("moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9")
        function = "add"
        gas_limit = 6000000
        args = [7]

        intent = self.factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args
        )

        assert intent.sender == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert intent.receiver == "moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9"
        assert intent.gas_limit == gas_limit
        assert intent.data
        assert intent.data.decode() == "add@07"
        assert intent.value == 0

    def test_create_transaction_for_execute_and_tranfer_native_token(self):
        sender = Address.new_from_bech32("moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8")
        contract = Address.new_from_bech32("moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9")
        function = "add"
        gas_limit = 6000000
        args = [7]
        moax_amount = 1000000000000000000

        transaction = self.factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            native_transfer_amount=moax_amount
        )

        assert transaction.sender == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert transaction.receiver == "moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9"
        assert transaction.gas_limit == gas_limit
        assert transaction.data
        assert transaction.data.decode() == "add@07"
        assert transaction.value == 1000000000000000000

    def test_create_transaction_for_execute_and_send_single_dct(self):
        sender = Address.new_from_bech32("moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8")
        contract = Address.new_from_bech32("moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9")
        function = "dummy"
        gas_limit = 6000000
        args = [7]
        token = Token("FOO-6ce17b", 0)
        transfer = TokenTransfer(token, 10)

        transaction = self.factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            token_transfers=[transfer]
        )

        assert transaction.sender == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert transaction.receiver == "moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9"
        assert transaction.gas_limit == gas_limit
        assert transaction.data
        assert transaction.data.decode() == "DCTTransfer@464f4f2d366365313762@0a@64756d6d79@07"
        assert transaction.value == 0

    def test_create_transaction_for_execute_and_send_multiple_dcts(self):
        sender = Address.new_from_bech32("moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8")
        contract = Address.new_from_bech32("moa1qqqqqqqqqqqqqpgqak8zt22wl2ph4tswtyc39namqx6ysa2sd8ssc7aswp")
        function = "dummy"
        gas_limit = 6000000
        args = [7]

        foo_token = Token("FOO-6ce17b", 0)
        foo_transfer = TokenTransfer(foo_token, 10)

        bar_token = Token("BAR-5bc08f", 0)
        bar_transfer = TokenTransfer(bar_token, 3140)

        transaction = self.factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            token_transfers=[foo_transfer, bar_transfer]
        )

        assert transaction.sender == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert transaction.receiver == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert transaction.gas_limit == gas_limit
        assert transaction.data
        assert transaction.data.decode() == "MultiDCTNFTTransfer@00000000000000000500ed8e25a94efa837aae0e593112cfbb01b448755069e1@02@464f4f2d366365313762@@0a@4241522d356263303866@@0c44@64756d6d79@07"
        assert transaction.value == 0

    def test_create_transaction_for_execute_and_send_single_nft(self):
        sender = Address.new_from_bech32("moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8")
        contract = Address.new_from_bech32("moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9")
        function = "dummy"
        gas_limit = 6000000
        args = [7]
        token = Token("NFT-123456", 1)
        transfer = TokenTransfer(token, 1)

        transaction = self.factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            token_transfers=[transfer]
        )

        assert transaction.sender == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert transaction.receiver == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert transaction.gas_limit == gas_limit
        assert transaction.data
        assert transaction.data.decode() == "DCTNFTTransfer@4e46542d313233343536@01@01@00000000000000000500b9353fe8407f87310c87e12fa1ac807f0485da39d152@64756d6d79@07"
        assert transaction.value == 0

    def test_create_transaction_for_execute_and_send_multiple_nfts(self):
        sender = Address.new_from_bech32("moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8")
        contract = Address.new_from_bech32("moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9")
        function = "dummy"
        gas_limit = 6000000
        args = [7]

        first_token = Token("NFT-123456", 1)
        first_transfer = TokenTransfer(first_token, 1)
        second_token = Token("NFT-123456", 42)
        second_transfer = TokenTransfer(second_token, 1)

        transaction = self.factory.create_transaction_for_execute(
            sender=sender,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=args,
            token_transfers=[first_transfer, second_transfer]
        )

        assert transaction.sender == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert transaction.receiver == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert transaction.gas_limit == gas_limit
        assert transaction.data
        assert transaction.data.decode() == "MultiDCTNFTTransfer@00000000000000000500b9353fe8407f87310c87e12fa1ac807f0485da39d152@02@4e46542d313233343536@01@01@4e46542d313233343536@2a@01@64756d6d79@07"
        assert transaction.value == 0

    def test_create_transaction_for_upgrade(self):
        sender = Address.new_from_bech32("moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8")
        contract_address = Address.new_from_bech32("moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9")
        contract = Path(__file__).parent.parent / "testutils" / "testdata" / "adder.wasm"
        gas_limit = 6000000
        args = [0]

        transaction = self.factory.create_transaction_for_upgrade(
            sender=sender,
            contract=contract_address,
            bytecode=contract,
            gas_limit=gas_limit,
            arguments=args
        )

        assert transaction.sender == "moa1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssfq94h8"
        assert transaction.receiver == "moa1qqqqqqqqqqqqqpgqhy6nl6zq07rnzry8uyh6rtyq0uzgtk3e69fq9ny2r9"
        assert transaction.data
        assert transaction.data.decode().startswith("upgradeContract@")
        assert transaction.gas_limit == gas_limit
        assert transaction.value == 0
