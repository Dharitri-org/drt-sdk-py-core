import json
from base64 import b64decode, b64encode
from collections import OrderedDict
from typing import Any, Dict, Optional

from dharitri_sdk_core import Address
from dharitri_sdk_core.constants import (TRANSACTION_MIN_GAS_PRICE,
                                           TRANSACTION_OPTIONS_DEFAULT,
                                           TRANSACTION_VERSION_DEFAULT)
from dharitri_sdk_core.interfaces import (IAddress, IChainID, IGasLimit,
                                            IGasPrice, INonce, ISignature,
                                            ITransactionOptions,
                                            ITransactionPayload,
                                            ITransactionValue,
                                            ITransactionVersion)
from dharitri_sdk_core.transaction_payload import TransactionPayload


class Transaction:
    def __init__(
        self,
        chain_id: IChainID,
        sender: IAddress,
        receiver: IAddress,
        gas_limit: IGasLimit,
        sender_username: Optional[str] = None,
        receiver_username: Optional[str] = None,
        gas_price: Optional[IGasPrice] = None,
        nonce: Optional[INonce] = 0,
        value: Optional[ITransactionValue] = None,
        data: Optional[ITransactionPayload] = None,
        version: Optional[ITransactionVersion] = None,
        options: Optional[ITransactionOptions] = None,
        guardian: Optional[IAddress] = None
    ) -> None:
        self.chainID: IChainID = chain_id
        self.sender: IAddress = sender
        self.receiver: IAddress = receiver

        self.sender_username: str = sender_username or ""
        self.receiver_username: str = receiver_username or ""

        self.guardian: Optional[IAddress] = guardian

        self.gas_limit: IGasLimit = gas_limit
        self.gas_price: IGasPrice = gas_price or TRANSACTION_MIN_GAS_PRICE

        self.nonce: INonce = nonce or 0
        self.value: ITransactionValue = value or 0
        self.data: ITransactionPayload = data or TransactionPayload.empty()

        self.version: ITransactionVersion = version or TRANSACTION_VERSION_DEFAULT
        self.options: ITransactionOptions = options or TRANSACTION_OPTIONS_DEFAULT

        self.signature: ISignature = bytes()
        self.guardian_signature: ISignature = bytes()

    def serialize_for_signing(self) -> bytes:
        dictionary = self.to_dictionary(with_signature=False)
        serialized = self._dict_to_json(dictionary)
        return serialized

    def to_dictionary(self, with_signature: bool = True) -> Dict[str, Any]:
        dictionary: Dict[str, Any] = OrderedDict()
        dictionary["nonce"] = self.nonce
        dictionary["value"] = str(self.value)

        dictionary["receiver"] = self.receiver.bech32()
        dictionary["sender"] = self.sender.bech32()

        if self.sender_username:
            dictionary["senderUsername"] = b64encode(self.sender_username.encode()).decode()

        if self.receiver_username:
            dictionary["receiverUsername"] = b64encode(self.receiver_username.encode()).decode()

        dictionary["gasPrice"] = self.gas_price
        dictionary["gasLimit"] = self.gas_limit

        if self.data.length():
            dictionary["data"] = self.data.encoded()

        dictionary["chainID"] = self.chainID

        if self.version:
            dictionary["version"] = self.version

        if self.options:
            dictionary["options"] = self.options

        if self.guardian:
            dictionary["guardian"] = self.guardian.bech32()

        # When adding signatures, we don't have to follow any ordering,
        # so we can just add them at the end.
        if with_signature:
            dictionary["signature"] = self.signature.hex()

            if self.guardian_signature:
                dictionary["guardianSignature"] = self.guardian_signature.hex()

        return dictionary

    @staticmethod
    def from_dictionary(dictionary: Dict[str, Any]) -> "Transaction":
        chain = dictionary["chainID"]
        sender = Address.from_bech32(dictionary["sender"])
        receiver = Address.from_bech32(dictionary["receiver"])
        gas_limit = dictionary["gasLimit"]
        gas_price = dictionary["gasPrice"]
        nonce = dictionary["nonce"]
        value = dictionary["value"]
        sender_username = dictionary.get("senderUsername", "")
        receiver_username = dictionary.get("receiverUsername", "")
        data = dictionary.get("data", "")
        version = dictionary["version"]
        options = dictionary.get("options", None)
        guardian = dictionary.get("guardian", "")
        signature = dictionary.get("signature", "")
        guardian_signature = dictionary.get("guardianSignature")

        transaction = Transaction(
            chain_id=chain,
            sender=sender,
            receiver=receiver,
            gas_limit=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            value=value,
            version=version,
            options=options
        )

        if sender_username:
            transaction.sender_username = b64decode(sender_username.encode()).decode()

        if receiver_username:
            transaction.receiver_username = b64decode(receiver_username.encode()).decode()

        if data:
            transaction.data = TransactionPayload.from_encoded_str(data)

        if guardian:
            transaction.guardian = Address.from_bech32(guardian)

        if signature:
            transaction.signature = bytes.fromhex(signature)

        if guardian_signature:
            transaction.guardian_signature = bytes.fromhex(guardian_signature)

        return transaction

    def _dict_to_json(self, dictionary: Dict[str, Any]) -> bytes:
        serialized = json.dumps(dictionary, separators=(',', ':')).encode("utf8")
        return serialized
