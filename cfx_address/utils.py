from typing import (
    Any
)

from cfx_address._utils import (
    validate_hex_address,
    validate_network_id,
    eth_eoa_address_to_cfx_hex
)
from cfx_address.address import (
    Base32Address
)
# from eth_utils.address import (
#     is_hex_address
# )

validate_base32 = Base32Address.validate
is_valid_base32 = Base32Address.is_valid_base32

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
