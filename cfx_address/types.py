import sys

from typing import (
    Literal,
    NewType, 
    TypedDict,
    Union,
    Callable,
)

from eth_typing import HexAddress

if sys.version_info >= (3,9):
    from typing import Annotated
    starts_with_net: Callable[[str], bool] = lambda x: (x.startswith("net") or x.startswith("NET"))
    TRIVIAL_NETWORK_PREFIX = Annotated[
        str, 
        starts_with_net
    ]
else:
    TRIVIAL_NETWORK_PREFIX = NewType("TRIVIAL_NETWORK_PREFIX", str)

NetworkPrefix = Union[
    Literal["cfx", "cfxtest"], TRIVIAL_NETWORK_PREFIX,
]

AddressType = Literal[
    "null", 
    "builtin", 
    "user", 
    "contract", 
    "invalid"
]

class Base32AddressParts(TypedDict):
    network_id: int
    address_type: AddressType
    hex_address: HexAddress
