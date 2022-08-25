from typing import (
    Optional,
    Union,
    cast
)

from cfx_address._utils import (
    validate_hex_address,
    validate_network_id,
    eth_eoa_address_to_cfx_hex
)
from cfx_address.address import (
    Base32Address
)
from eth_utils.address import (
    is_hex_address,
)

from cfx_utils.types import (
    HexAddress,
)

validate_base32 = Base32Address.validate
is_valid_base32 = Base32Address.is_valid_base32

def normalize_to(
    address: str, network_id:Optional[int] = None, verbose=False
) -> Union[Base32Address, HexAddress]:  
    """
    normalize a hex or base32 address to target network or hex address

    :param str address: a base32 address or hex address
    :param Optional[int] network_id: target network id, defaults to None(and will return hex address)
    :return Union[Base32Address, HexAddress]: a normalized base32 address or hex address, depending on network id
    """    
    if network_id is not None:
        return Base32Address(address, network_id, verbose)
    else:
        if is_hex_address(address):
            return cast(HexAddress, address)
        return Base32Address(address).hex_address

# def is_valid_address(value: str) -> bool:
#     """
#     checks if a value is a valid string-typed address, either hex address or base32 address is ok

#     :param Any value: value to check
#     :return bool: True if valid, otherwise False
#     """    
#     return is_hex_address(value) or is_valid_base32(value)

__all__ = [
    "validate_hex_address",
    "validate_network_id",
    "eth_eoa_address_to_cfx_hex",
    "validate_base32",
    "is_valid_base32",
    # "is_hex_address"
]
