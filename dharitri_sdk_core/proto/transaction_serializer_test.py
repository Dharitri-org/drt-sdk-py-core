from dharitri_sdk_core.proto.transaction_serializer import ProtoSerializer
from dharitri_sdk_core.testutils.wallets import load_wallets
from dharitri_sdk_core.transaction import Transaction, TransactionComputer


class TestProtoSerializer:
    wallets = load_wallets()
    alice = wallets["alice"]
    bob = wallets["bob"]
    carol = wallets["carol"]
    proto_serializer = ProtoSerializer()
    transaction_computer = TransactionComputer()

    def test_serialize_tx_no_data_no_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=50000,
            chain_id="local-testnet",
            nonce=89,
            value=0,
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "0859120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc0340d08603520d6c6f63616c2d746573746e657458026240de0b83647f9990b927ef9d3ff11ee0e6f2f50cc613c04c0e5b834f3e39eb0d2807cd664ce195713e1d9599e0a84cb56a400fe4e24e4e8d305e0d6dbc34597b0d"

    def test_serialize_tx_with_data_no_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=80000,
            chain_id="local-testnet",
            data=b"hello",
            nonce=90
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "085a120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc034080f1044a0568656c6c6f520d6c6f63616c2d746573746e65745802624025fc0da0e2e1be76a217072ef27cee8fee2b8fdaa4154b128ec7565cf6bec61bf9c1df3a495fce4bafb06a5ed0f0d5b38dab3eaeb11ed862255938ae9d4dcc05"

    def test_serialize_tx_with_data_and_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=100000,
            chain_id="local-testnet",
            nonce=92,
            data=b"for the spaceship",
            value=123456789000000000000000000000
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "085c120e00018ee90ff6181f3761632000001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc0340a08d064a11666f722074686520737061636573686970520d6c6f63616c2d746573746e6574580262401ff0a3e5da0b2e7d1160e8711456f5e1da865eb6607c0777511b621fac119e859ff900e7c56f0b0962c67edc75da10523ff5dc29a9b1ec8060685ad5dd1f3505"

    def test_serialize_tx_with_nonce_zero(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            chain_id="local-testnet",
            gas_limit=80000,
            nonce=0,
            value=0,
            data=b"hello",
            version=1
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc034080f1044a0568656c6c6f520d6c6f63616c2d746573746e657458016240d73e9c2f978d248eaba41c2453088f0e3488c02eb88ede7b1f40a22527a0f90c747056163a1625c127b3b6bd602a3a0cb607478a45d0a847e471911b3b87e805"

    def test_serialized_tx_with_usernames(self):
        transaction = Transaction(
            sender=self.carol.label,
            receiver=self.alice.label,
            gas_limit=50000,
            chain_id="T",
            nonce=204,
            value=1000000000000000000,
            sender_username="carol",
            receiver_username="alice"
        )
        transaction.signature = self.carol.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "08cc011209000de0b6b3a76400001a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e12205616c6963652a20b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba32056361726f6c388094ebdc0340d08603520154580262403f3f645f9ac38142c1087a76b855e48ed0aa44185146df5f3317b8887e7b59f195d6093d3c2b30fb693a27e3175a199ef04a6e650101ab3f4b3649f0fe2f5204"
