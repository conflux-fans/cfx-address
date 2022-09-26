# utils do not rely on other modules are defined here to avoid recursive import
from typing import (
    Any,
    Literal,
    Union,
    cast,
)
from hexbytes import (
    HexBytes,
)

from cfx_utils.exceptions import (
    InvalidNetworkId,
    InvalidHexAddress, 
    
)
from eth_utils.crypto import (
    keccak
)
from eth_utils.address import (
    is_hex_address
)
from eth_typing.evm import (
    HexAddress,
)

def public_key_to_cfx_hex(public_key: Union[str, bytes]) -> HexAddress:
    """
    return the corresponding hex address of a public key in conflux: "0x1" + keccak(pk).hex()[-39]
    
    :param Union[str, bytes] public_key: str or bytes representation of public key
    :return HexAddress: Hex representation of the correspondign hex address
    
    
    >>> public_key_to_cfx_hex("0xdacdaeba8e391e7649d3ac4b5329ca0e202d38facd928d88b5f729b89a497e43cc4ad3816fcfdb241497b3b43862afb4c899bc284bf60feca4ee66ff868d1feb")
    '0x152d251c36aec31072b90a85b95bf9435b07edb8'
    """    
    public_key = HexBytes(public_key)
    # only EOA has a corresponding public key
    address = "0x1" + keccak(public_key).hex()[-39:]
    return cast(HexAddress, address)

def eth_eoa_address_to_cfx_hex(eoa_address: str) -> HexAddress:
    """
    Convert an ethereum EOA address to valid cfx hex address.
    
    In conflux, only addresses starting with 0x1 are valid user-type addresses. 
    This function convert ethereum EOA address to the corresponding form in conflux.

    :param str address: ethereum address
    :raises InvalidHexAddress: the argument is not a valid hex address 
    :return HexAddress: corresponding hex address in conflux, starting with '0x1'
    :examplse: 
    
    >>> eth_eoa_address_to_cfx_hex("0xd43d2a93e97245E290feE74276a1EF8D275bE646")
    '0x143d2a93e97245e290fee74276a1ef8d275be646'
    """
    validate_hex_address(eoa_address)
    return '0x1' + eoa_address.lower()[3:] # type: ignore

def validate_network_id(network_id: Any) -> Literal[True]:
    """
    Checks if the given value is a positive integer.


    :param Any hex_address: value to validate
    :raises InvalidHexAddress: raised if not valid
    :return Literal[True]: returns True if valid
    """
    if isinstance(network_id, int) and network_id > 0:
        return True
    raise InvalidNetworkId("Expected network_id to be a positive integer. "
                     f"Receives {network_id} of type {type(network_id)}")

def validate_hex_address(value: Any) -> Literal[True]:
    """
    Checks if the given string of text type is an address in hexadecimal encoded form.

    :param Any hex_address: value to validate
    :raises InvalidHexAddress: raised if not valid
    :return Literal[True]: returns True if valid
    """
    if not is_hex_address(value):
        raise InvalidHexAddress("Expected a hex40 address. "
                                f"Receives {value}")
    return True
