import sys

from typing import (
    Annotated,
    Literal,
    NewType, 
    TypedDict,
    Union
)

from eth_typing import HexAddress

class InvalidAddress(ValueError):
    pass

class InvalidBase32Address(InvalidAddress):
    """
    The supplied address is not a valid Base32 address, as defined in CIP-37
    """
    pass

class InvalidHexAddress(InvalidAddress):
    pass

class InvalidNetworkId(ValueError):
    pass


if sys.version_info >= (3,9):
    TRIVIAL_NETWORK_PREFIX = Annotated[str, lambda x: x.startswith("net")]
else:
    TRIVIAL_NETWORK_PREFIX = NewType("TRIVIAL_NETWORK_PREFIX", str)

NetworkPrefix = Union[
    Literal["cfx", "cfxtest"], TRIVIAL_NETWORK_PREFIX,
]

AddressType = Literal[
    "type.null", 
    "type.builtin", 
    "type.user", 
    "type.contract", 
    "type.invalid"
]

class Base32AddressParts(TypedDict):
    network_id: int
    address_type: AddressType
    hex_address: HexAddress
