from cfx_address.utils import (
    eth_eoa_address_to_cfx_hex,
    # is_valid_address,
)

eoa_address = "0xd43d2a93e97245E290feE74276a1EF8D275bE646"
converted_address = "0x143d2a93e97245e290fee74276a1ef8d275be646"
hex_address = "0x1ecde7223747601823f7535d7968ba98b4881e09"
testnet_verbose_address = "CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4"

# other typed
# def test_is_valid_address():
#     assert is_valid_address(hex_address)
#     assert is_valid_address(testnet_verbose_address)
#     assert not is_valid_address("0x0")
#     assert not is_valid_address(114514)

def test_eoa_address_convert():
    assert eth_eoa_address_to_cfx_hex(eoa_address) == converted_address
