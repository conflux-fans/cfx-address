from typing import (
    Optional,
    Union,
    cast,
    Literal,
    overload,
)

from eth_utils.address import (
    is_hex_address,
)

from cfx_address._utils import (
    validate_hex_address,
    validate_network_id,
    eth_eoa_address_to_cfx_hex,
    public_key_to_cfx_hex,
)
from cfx_address.address import (
    Base32Address
)

from cfx_utils.exceptions import (
    Base32AddressNotMatch,
    AddressNotMatch,
)
from cfx_utils.types import (
    HexAddress,
)

validate_base32 = Base32Address.validate
is_valid_base32 = Base32Address.is_valid_base32

@overload
def normalize_to(address: str, network_id: None, verbose=False) -> HexAddress:
    ...

@overload
def normalize_to(address: str, network_id: int, verbose=False) -> Base32Address:
    ...

def normalize_to(
    address: str, network_id:Union[int, None], verbose=False
) -> Union[Base32Address, HexAddress]:  
    """
    normalize a hex or base32 address to target network or hex address

    :param str address: a base32 address or hex address
    :param Union[int, None] network_id: target network id. None will return hex address
    :return Union[Base32Address, HexAddress]: a normalized base32 address or hex address, depending on network id
    """    
    if network_id is not None:
        return Base32Address(address, network_id, verbose)
    else:
        if is_hex_address(address):
            return cast(HexAddress, address)
        # error will be raised if address is not a Base32Address
        return Base32Address(address).hex_address

def validate_address_agaist_network_id(address: str, network_id: Union[int, None], accept_hex: Optional[bool]=False) -> Literal[True]:
    """
    Validate address in specific network context. Error will be raised only if:
        1. address validity checking: 
            address is a base32 address or hex / base32 address if accept_hex
        2. network id validity checking: 
            the network id of the address should be same as network_id, this step will be skipped if address is hex address or network_id is None

    :param str address: address to validate
    :param Union[int, None] network_id: if is None, then network id checking will be skipped
    :param Optional[bool] accept_hex: whether a hex address is accepted, if. Defaults to False
    :raises AddressNotMatch: hex address is received when accept_hex is not True
    :raises Base32AddressNotMatch: the network id of address does not equal to network_id
    :return Literal[True]: returns True if no exceptions are raised
    
    >>> from cfx_address.utils import validate_address_agaist_network_id
    >>> address = Base32Address.zero_address(1)
    >>> validate_address_agaist_network_id(address, 1)
    True
    >>> validate_address_agaist_network_id(address.hex_address, 1, True)
    True
    >>> validate_address_agaist_network_id(address, None)
    True
    >>> validate_address_agaist_network_id(address.hex_address, None)
    Traceback (most recent call last):
        ...
    cfx_utils.exceptions.AddressNotMatch: hex address is not accepted
    >>> validate_address_agaist_network_id(address, 1029)
    Traceback (most recent call last):
        ...
    cfx_utils.exceptions.Base32AddressNotMatch: expects address of network id 1029, receives address of network id 1
    
    """    
    if is_hex_address(address):
        if accept_hex:
            return True
        raise AddressNotMatch("hex address is not accepted")
    else:
        # the address is Base32Address (or invalid)
        address_network_id = Base32Address.decode(address)["network_id"]
        if address_network_id == network_id or network_id is None:
            return True
        raise Base32AddressNotMatch(f"expects address of network id {network_id}, "
                                    f"receives address of network id {address_network_id}")


__all__ = [
    "validate_hex_address",
    "validate_network_id",
    "eth_eoa_address_to_cfx_hex",
    "validate_base32",
    "is_valid_base32",
    "validate_address_agaist_network_id",
    # "is_hex_address"
]
