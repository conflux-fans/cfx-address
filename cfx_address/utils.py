from typing import Any

from cfx_address.types import InvalidHexAddress, InvalidNetworkId
from eth_utils.address import is_hex_address

def eth_address_to_cfx(address: str):
    assert type(address) == str
    return '0x1' + address.lower()[3:]


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
