import pytest
from cfx_address.utils import (
    eth_eoa_address_to_cfx_hex,
    normalize_to,
    validate_address_agaist_network_id
    # is_valid_address,
)
from cfx_address import (
    Base32Address
)
from cfx_utils.exceptions import (
    AddressNotMatch,
    Base32AddressNotMatch
)

eoa_address = "0xd43d2a93e97245E290feE74276a1EF8D275bE646"
converted_address = "0x143d2a93e97245e290fee74276a1ef8d275be646"
hex_address = "0x1ecde7223747601823f7535d7968ba98b4881e09"
testnet_verbose_address = "CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4"
mainnet_address = "cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu"

# other typed
# def test_is_valid_address():
#     assert is_valid_address(hex_address)
#     assert is_valid_address(testnet_verbose_address)
#     assert not is_valid_address("0x0")
#     assert not is_valid_address(114514)

def test_eoa_address_convert():
    assert eth_eoa_address_to_cfx_hex(eoa_address) == converted_address

def test_normalize():
    assert normalize_to(testnet_verbose_address, None) == hex_address
    assert normalize_to(testnet_verbose_address, 1029) == mainnet_address
    assert normalize_to(hex_address, None) == hex_address
    assert normalize_to(hex_address, 1) == testnet_verbose_address
    
def test_validate_against_network_id():
    address = Base32Address.zero_address(1)
    assert validate_address_agaist_network_id(address, 1)
    assert validate_address_agaist_network_id(address.hex_address, 1, True)
    assert validate_address_agaist_network_id(address, None)
    with pytest.raises(AddressNotMatch):
        validate_address_agaist_network_id(address.hex_address, None)
    with pytest.raises(Base32AddressNotMatch):
        validate_address_agaist_network_id(address, 1029)
