from cfx_address.address import Address

hex_address = "0x1ecde7223747601823f7535d7968ba98b4881e09"
test_verbose_address = "CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4"
testnet_address = "cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4"
main_net_address = "cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu"
main_net_verbose_address = "CFX:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE7GGP3VPU"

def test_encode():
    assert Address.encode_hex_address(hex_address, 1) == testnet_address
    assert Address.encode_hex_address(hex_address, 1, True) == test_verbose_address
    assert Address.encode_hex_address(hex_address, 1029) == main_net_address
    assert Address.encode_hex_address(hex_address, 1029, True) == main_net_verbose_address

def test_decode():
    assert Address.decode_hex_address(main_net_address) == hex_address
    assert Address.decode_network_id(main_net_address) == 1029
    assert Address.decode_address_type(main_net_address) == 'user'
