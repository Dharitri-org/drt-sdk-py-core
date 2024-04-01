import pytest

from dharitri_sdk_core import Address
from dharitri_sdk_core.errors import InvalidInnerTransactionError
from dharitri_sdk_core.testutils.wallets import load_wallets
from dharitri_sdk_core.transaction import Transaction, TransactionComputer
from dharitri_sdk_core.transaction_factories.relayed_transactions_factory import \
    RelayedTransactionsFactory
from dharitri_sdk_core.transaction_factories.transactions_factory_config import \
    TransactionsFactoryConfig


class TestRelayedTransactionsFactory:
    config = TransactionsFactoryConfig("T")
    factory = RelayedTransactionsFactory(config)
    transaction_computer = TransactionComputer()
    wallets = load_wallets()

    def test_create_relayed_v1_with_invalid_inner_tx(self):
        alice = self.wallets["alice"]

        inner_transaction = Transaction(
            sender=alice.label,
            receiver="moa1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls29jpxv",
            gas_limit=10000000,
            data="getContractConfig".encode(),
            chain_id=self.config.chain_id
        )

        with pytest.raises(InvalidInnerTransactionError, match="The inner transaction is not signed"):
            self.factory.create_relayed_v1_transaction(
                inner_transaction=inner_transaction,
                relayer_address=Address.from_bech32(self.wallets["bob"].label)
            )

        inner_transaction.gas_limit = 0
        inner_transaction.signature = b"invalidsignature"

        with pytest.raises(InvalidInnerTransactionError, match="The gas limit is not set for the inner transaction"):
            self.factory.create_relayed_v1_transaction(
                inner_transaction=inner_transaction,
                relayer_address=Address.from_bech32(self.wallets["bob"].label)
            )

    def test_create_relayed_v1_transaction(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="moa1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls29jpxv",
            gas_limit=60000000,
            chain_id=self.config.chain_id,
            data=b"getContractConfig",
            nonce=198
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.nonce = 2627

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414141415141414141414141414141414141414141414141414141414141432f2f383d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a22746264506468326e45757a317973436e414b724c3573386253576e4865304142326434735a4f365253794434315a516f4a69434d346430543762356976587a456475346579595468462f30617a6e41614363354442413d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a327d"
        assert relayed_transaction.signature.hex() == "71c43095b3289582e8f6fbb1b38fc3a42a2bf091944a4ed64756bf8dd17738dabf9a32da7450e313e7bcec53c6f11d639d6bec79bbd6975841a9517eecd4b207"

    def test_create_relayed_v1_transaction_with_usernames(self):
        alice = self.wallets["alice"]
        carol = self.wallets["carol"]
        frank = self.wallets["frank"]

        inner_transaction = Transaction(
            sender=carol.label,
            receiver=alice.label,
            gas_limit=50000,
            chain_id=self.config.chain_id,
            nonce=208,
            sender_username="carol",
            receiver_username="alice",
            value=1000000000000000000
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = carol.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(frank.label)
        )
        relayed_transaction.nonce = 715

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = frank.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3230382c2273656e646572223a227371455656633553486b6c45344a717864556e59573068397a536249533141586f3534786f32634969626f3d222c227265636569766572223a2241546c484c76396f686e63616d433877673970645168386b77704742356a6949496f3349484b594e6165453d222c2276616c7565223a313030303030303030303030303030303030302c226761735072696365223a313030303030303030302c226761734c696d6974223a35303030302c2264617461223a22222c227369676e6174757265223a226b702f6f36652b4f666334722f42667545436b446850666330546d52663578622f736665637a487968416f414479763156696a6d6346337a68632f766e7839774c36426e586451384f4c62526e3436537947557743413d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c22736e64557365724e616d65223a22593246796232773d222c22726376557365724e616d65223a22595778705932553d227d"
        assert relayed_transaction.signature.hex() == "aae9b37b80a61e80a86011b4f61fb50a98d23b49bb4899ca962f1c085234a1cb45dfeb509bfcba075c32452d6906b227f99d1c4ffb946df542c644b4b70a9808"

    def test_compute_relayed_v1_with_guarded_inner_tx(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]
        grace = self.wallets["grace"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="moa1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q2fwu0j",
            gas_limit=60000000,
            chain_id=self.config.chain_id,
            data=b"getContractConfig",
            nonce=198,
            version=2,
            options=2,
            guardian=grace.label
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(inner_tx_bytes)
        inner_transaction.guardian_signature = grace.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.nonce = 2627

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a22617748304e2b4866704c49346968726374446b56426b33636b575949756656384d7536596e706c7147566239705447584f6f776c375231306a77316f5161545778595573374d41756353784c6e6c616b7378554541773d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a224252306a414e69706a32796d4466694b426a364e757034454948652f5972383971687a443374453565556670626638503870506159376a44614779514e66735159776f4f4b58414b4873644b5a4557336672427743773d3d227d"
        assert relayed_transaction.signature.hex() == "86a1dfafd0a0139f3a0cd24f51f396cd2a573c061c10b13619b2f4ba137c40fbd890559fd65bf941a52cf085244f2af2a139ef2817d15d5c0d1eb7d0dd8a910d"

    def test_guarded_relayed_v1_with_guarded_inner_tx(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]
        grace = self.wallets["grace"]
        frank = self.wallets["frank"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="moa1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q2fwu0j",
            gas_limit=60000000,
            chain_id=self.config.chain_id,
            data=b"addNumber",
            nonce=198,
            version=2,
            options=2,
            guardian=grace.label
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(inner_tx_bytes)
        inner_transaction.guardian_signature = grace.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.options = 2
        relayed_transaction.nonce = 2627
        relayed_transaction.guardian = frank.label

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(relayed_tx_bytes)
        relayed_transaction.guardian_signature = frank.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225957526b546e5674596d5679222c227369676e6174757265223a226e6a6a7678546353775756396a7a68722b55367041556c3549586d614158762f395648394b4554414a4f493172426b565169536c38442f7962535955634a484b4e6954686243325767796d6b4f564b624a4b6d4442773d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a22492b4a544753686f696a432f483366557a4c79522f44534b31457135746f79392b796b457554444335746c53765a61577543435a76667a6a704a7872636e5868316e5178453376434a2f7947753836677270583841513d3d227d"
        assert relayed_transaction.signature.hex() == "46b0383b43e39948ba78bc63e60dae5d1177b6d5e371578ebcc16f3196a18068b8671c5ff3ca3d42a4f378ec509f72db89a4b55b0b15224f44d53a4fed286604"

    def test_create_relayed_v2_with_invalid_inner_tx(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]
        carol = self.wallets["carol"]

        inner_transaction = Transaction(
            sender=alice.label,
            receiver=bob.label,
            gas_limit=50000,
            chain_id=self.config.chain_id
        )

        with pytest.raises(InvalidInnerTransactionError, match="The gas limit should not be set for the inner transaction"):
            self.factory.create_relayed_v2_transaction(
                inner_transaction=inner_transaction,
                inner_transaction_gas_limit=50000,
                relayer_address=Address.from_bech32(carol.label)
            )

        inner_transaction.gas_limit = 0
        with pytest.raises(InvalidInnerTransactionError, match="The inner transaction is not signed"):
            self.factory.create_relayed_v2_transaction(
                inner_transaction=inner_transaction,
                inner_transaction_gas_limit=50000,
                relayer_address=Address.from_bech32(carol.label)
            )

    def test_compute_relayed_v2_transaction(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="moa1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls29jpxv",
            gas_limit=0,
            chain_id=self.config.chain_id,
            data=b"getContractConfig",
            nonce=15,
            version=2,
            options=0
        )

        serialized_inner_transaction = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(serialized_inner_transaction)

        relayed_transaction = self.factory.create_relayed_v2_transaction(
            inner_transaction=inner_transaction,
            inner_transaction_gas_limit=60_000_000,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.nonce = 37

        serialized_relayed_transaction = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(serialized_relayed_transaction)

        assert relayed_transaction.version == 2
        assert relayed_transaction.options == 0
        assert relayed_transaction.data.decode() == "relayedTxV2@000000000000000000010000000000000000000000000000000000000002ffff@0f@676574436f6e7472616374436f6e666967@9b5f2023b8423891f994f7c2fe1560ef9a1370e13243acabe3a457320416493323ba1f5e7e1dab9932ec8bab18b60745c3a283f737fc42aa06b12db92200eb00"
