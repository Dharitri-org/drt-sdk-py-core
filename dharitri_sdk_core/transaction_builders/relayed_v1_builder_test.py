import pytest

from dharitri_sdk_core import TokenPayment
from dharitri_sdk_core.address import Address
from dharitri_sdk_core.errors import ErrInvalidRelayerV1BuilderArguments
from dharitri_sdk_core.testutils.wallets import load_wallets
from dharitri_sdk_core.transaction import Transaction
from dharitri_sdk_core.transaction_builders.relayed_v1_builder import \
    RelayedTransactionV1Builder
from dharitri_sdk_core.transaction_payload import TransactionPayload


class NetworkConfig:
    def __init__(self) -> None:
        self.min_gas_limit = 50_000
        self.gas_per_data_byte = 1_500
        self.gas_price_modifier = 0.01
        self.chain_id = "T"


class TestRelayedV1Builder:
    wallets = load_wallets()
    alice = wallets["alice"]
    bob = wallets["bob"]
    frank = wallets["frank"]
    grace = wallets["grace"]
    carol = wallets["carol"]

    def test_without_arguments(self):
        relayed_builder = RelayedTransactionV1Builder()

        with pytest.raises(ErrInvalidRelayerV1BuilderArguments):
            relayed_builder.build()

        inner_transaction = Transaction(
            chain_id="1",
            sender=Address.from_bech32(self.alice.label),
            receiver=Address.from_bech32("moa1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls29jpxv"),
            gas_limit=10000000,
            nonce=15,
            data=TransactionPayload.from_str("getContractConfig")
        )
        relayed_builder.set_inner_transaction(inner_transaction)

        with pytest.raises(ErrInvalidRelayerV1BuilderArguments):
            relayed_builder.build()

        network_config = NetworkConfig()
        relayed_builder.set_network_config(network_config)

        with pytest.raises(ErrInvalidRelayerV1BuilderArguments):
            relayed_builder.build()

    def test_compute_relayed_v1_tx(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=Address.from_bech32(self.bob.label),
            receiver=Address.from_bech32("moa1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls29jpxv"),
            gas_limit=60000000,
            nonce=198,
            data=TransactionPayload.from_str("getContractConfig")
        )
        # version is set to 1 to match the test in sdk-js-core
        inner_tx.version = 1
        inner_tx.signature = self.bob.secret_key.sign(inner_tx.serialize_for_signing())

        relayed_builder = RelayedTransactionV1Builder()
        relayed_builder.set_inner_transaction(inner_tx)
        relayed_builder.set_relayer_nonce(2627)
        relayed_builder.set_network_config(network_config)
        relayed_builder.set_relayer_address(Address.from_bech32(self.alice.label))

        relayed_tx = relayed_builder.build()

        # version is set to 1 to match the test in sdk-js-core
        relayed_tx.version = 1

        relayed_tx.signature = self.alice.secret_key.sign(relayed_tx.serialize_for_signing())

        assert relayed_tx.nonce == 2627
        assert str(relayed_tx.data) == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414141415141414141414141414141414141414141414141414141414141432f2f383d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a2276414f36414958687677774b4930767270665471643854567463597268456630714e6e324539734a4e6c6b315268326b2b37725a69344d48492b7133696c54366d3649302f63457554314d6b6f6d4e314775676c44513d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a317d"
        assert relayed_tx.signature.hex() == "759cbab03e1f2a8fe21faf53cdd36cd14add4018c91cce6e4b9f7b604ceca1404a18b9fd06b4480e204d4f1b08b201f0914da459486bf97ebbd09a759a162603"

    def test_compute_guarded_inner_tx(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=Address.from_bech32(self.bob.label),
            receiver=Address.from_bech32("moa1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q2fwu0j"),
            gas_limit=60000000,
            nonce=198,
            data=TransactionPayload.from_str("getContractConfig"),
            guardian=Address.from_bech32(self.grace.label),
            version=2,
            options=2
        )
        inner_tx.signature = self.bob.secret_key.sign(inner_tx.serialize_for_signing())
        inner_tx.guardian_signature = bytes.fromhex("c72e08622c86d9b6889fb9f33eed75c6a04a940daa012825464c6ccaad71640cfcf5c4d38b36fb0575345bbec90daeb2db7a423bfb5253cef0ddc5c87d1b5f04")

        relayed_builder = RelayedTransactionV1Builder()
        relayed_builder.set_inner_transaction(inner_tx)
        relayed_builder.set_relayer_nonce(2627)
        relayed_builder.set_network_config(network_config)
        relayed_builder.set_relayer_address(Address.from_bech32(self.alice.label))

        relayed_tx = relayed_builder.build()
        # version is set to 1 to match the test in sdk-js-core
        relayed_tx.version = 1

        relayed_tx.signature = self.alice.secret_key.sign(relayed_tx.serialize_for_signing())

        assert relayed_tx.nonce == 2627
        assert str(relayed_tx.data) == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a22617748304e2b4866704c49346968726374446b56426b33636b575949756656384d7536596e706c7147566239705447584f6f776c375231306a77316f5161545778595573374d41756353784c6e6c616b7378554541773d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a227879344959697947326261496e376e7a507531317871424b6c4132714153676c526b7873797131785a417a3839635454697a6237425855305737374a44613679323370434f2f745355383777336358496652746642413d3d227d"
        assert relayed_tx.signature.hex() == "01eb58224c72899a4a1a09f26fe35c1e07d1e31882e197f763115d5ba788b654af440a98c8f98d26838e8bd2e015bf4065f110b9423f8fc9b94fbadbe397440c"

    def test_guarded_inner_tx_and_guarded_relayed_tx(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=Address.from_bech32(self.bob.label),
            receiver=Address.from_bech32("moa1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q2fwu0j"),
            gas_limit=60000000,
            nonce=198,
            data=TransactionPayload.from_str("addNumber"),
            guardian=Address.from_bech32(self.grace.label),
            version=2,
            options=2
        )
        inner_tx.signature = self.bob.secret_key.sign(inner_tx.serialize_for_signing())
        inner_tx.guardian_signature = bytes.fromhex("b12d08732c86d9b6889fb9f33eed65c6a04a960daa012825464c6ccaad71640cfcf5c4d38b36fb0575345bbec90daeb2db7a423bfb5253cef0ddc5c87d1b5f04")

        relayed_builder = RelayedTransactionV1Builder()
        relayed_builder.set_inner_transaction(inner_tx)
        relayed_builder.set_relayer_nonce(2627)
        relayed_builder.set_network_config(network_config)
        relayed_builder.set_relayer_address(Address.from_bech32(self.alice.label))
        relayed_builder.set_relayed_transaction_version(2)
        relayed_builder.set_relayed_transaction_options(2)
        relayed_builder.set_relayed_transaction_guardian(Address.from_bech32(self.frank.label))

        relayed_tx = relayed_builder.build()
        relayed_tx.signature = self.alice.secret_key.sign(relayed_tx.serialize_for_signing())

        relayed_tx.guardian_signature = bytes.fromhex("d32c08722c86d9b6889fb9f33eed65c6a04a970daa012825464c6ccaad71640cfcf5c4d38b36fb0575345bbec90daeb2db7a423bfb5253cef0ddc5c87d1b5f04")

        assert relayed_tx.nonce == 2627
        assert str(relayed_tx.data) == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225957526b546e5674596d5679222c227369676e6174757265223a226e6a6a7678546353775756396a7a68722b55367041556c3549586d614158762f395648394b4554414a4f493172426b565169536c38442f7962535955634a484b4e6954686243325767796d6b4f564b624a4b6d4442773d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a227353304963797947326261496e376e7a5075316c7871424b6c6732714153676c526b7873797131785a417a3839635454697a6237425855305737374a44613679323370434f2f745355383777336358496652746642413d3d227d"
        assert relayed_tx.signature.hex() == "b419368be65b0d04b2ef0fe46c15c1512a5fa0de5f8f0b160e745a2ae7f85922a84ed7bcf4e4bf08663d51dd977aba695fcfb9cf9ad1a76872d86e8d1d5fb108"

    def test_compute_relayedV1_with_usernames(self):
        network_config = NetworkConfig()
        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=Address.from_bech32(self.carol.label),
            receiver=Address.from_bech32(self.alice.label),
            gas_limit=50000,
            sender_username="carol",
            receiver_username="alice",
            nonce=208,
            value=TokenPayment.moax_from_amount(1)
        )
        # version is set to 1 to match the test in sdk-js-core
        inner_tx.version = 1
        inner_tx.signature = self.carol.secret_key.sign(inner_tx.serialize_for_signing())

        builder = RelayedTransactionV1Builder()
        builder.set_inner_transaction(inner_tx)
        builder.set_relayer_nonce(715)
        builder.set_network_config(network_config)
        builder.set_relayer_address(Address.from_bech32(self.frank.label))

        relayed_tx = builder.build()

        # version is set to 1 to match the test in sdk-js-core
        relayed_tx.version = 1

        relayed_tx.signature = self.frank.secret_key.sign(relayed_tx.serialize_for_signing())

        assert relayed_tx.nonce == 715
        assert str(relayed_tx.data) == "relayedTx@7b226e6f6e6365223a3230382c2273656e646572223a227371455656633553486b6c45344a717864556e59573068397a536249533141586f3534786f32634969626f3d222c227265636569766572223a2241546c484c76396f686e63616d433877673970645168386b77704742356a6949496f3349484b594e6165453d222c2276616c7565223a313030303030303030303030303030303030302c226761735072696365223a313030303030303030302c226761734c696d6974223a35303030302c2264617461223a22222c227369676e6174757265223a225366586467586b64656d744c6637723555426e756156717957684267664b5977454b7a6e77526a532f5a34565354684d4f4a6c55534279467834335474397466496e366a4b7664695336586d4b746c353848726f44673d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a312c22736e64557365724e616d65223a22593246796232773d222c22726376557365724e616d65223a22595778705932553d227d"
        assert relayed_tx.signature.hex() == "0aa6c3d34acd8bdc5c6b47112f2266edf538d97e11a00cebc11c54c8eb5327d2d607a9f95892fc9a7093a357233a51fbf86118665bbab92bb7791c4313fb530b"
