from typing import Any

from cfx_address.types import (
    InvalidHexAddress, 
    InvalidNetworkId
)
from eth_utils.address import (
    is_hex_address
)
from eth_typing.evm import (
    HexAddress,
)

def eth_eoa_address_to_cfx_hex(eoa_address: str) -> HexAddress:
    """
    Convert an ethereum EOA address to valid cfx hex address.
    
    In conflux, only addresses starting with 0x1 are valid user-type addresses. 
    This function convert ethereum EOA address to the corresponding form in conflux.

    :param str address: ethereum address
    :raises InvalidHexAddress: 
    :return HexAddress: corresponding hex address in conflux, starting with '0x1'
    """
    validate_hex_address(eoa_address)
    return '0x1' + eoa_address.lower()[3:] # type: ignore


def hex_address_bytes(hex_address: str):
    assert type(hex_address) == str
    return bytes.fromhex(hex_address.lower().replace('0x', ""))

def validate_network_id(network_id: Any):
    if isinstance(network_id, int) and network_id > 0:
        return True
    raise InvalidNetworkId("Expected network_id to be a positive integer. "
                     f"Receives {network_id} of type {type(network_id)}")



def validate_hex_address(hex_address):
    if not is_hex_address(hex_address):
        raise InvalidHexAddress("Expected a hex40 address. "
                                f"Receives {hex_address}")
