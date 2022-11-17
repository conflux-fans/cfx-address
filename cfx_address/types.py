from typing import (
    Union,
    Callable,
)
from typing_extensions import (
    Literal,
    Annotated,
    TypedDict,
)

from eth_typing import ChecksumAddress

starts_with_net: Callable[[str], bool] = lambda x: (x.startswith("net") or x.startswith("NET"))
TRIVIAL_NETWORK_PREFIX = Annotated[
    str, 
    starts_with_net
]

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
    hex_address: ChecksumAddress
