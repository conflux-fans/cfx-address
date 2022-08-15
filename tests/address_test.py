import pytest
from cfx_address.address import Base32Address
from cfx_address.types import InvalidAddress, InvalidBase32Address, InvalidHexAddress, InvalidNetworkId

hex_address = "0x1ecde7223747601823f7535d7968ba98b4881e09"
checksum_address = "0x1ECdE7223747601823f7535d7968Ba98b4881E09"

testnet_verbose_address = "CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4"
testnet_address = "cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4"

mainnet_address = "cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu"
mainnet_verbose_address = "CFX:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE7GGP3VPU"
custom_net_address = "net8888:aatp533cg7d0agbd87kz48nj1mpnkca8beh6tx5zc7"

invalid_type_address = "CFX:TYPE.NULL:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE7GGP3VPU"
invalid_net_address = "ETH:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4"
mixed_testnet_address = "CFXTEST:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4"
invalids = [ "TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4"
    "CFXTEST:TYPE.USER"
    "CFXTEST"
    "AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4"
]

# an unknown address type, should ignore
unknown_type_address = "CFX:GOD:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE7GGP3VPU"

def test_validation():
    assert Base32Address.is_valid_base32(testnet_address)
    assert Base32Address.is_valid_base32(mainnet_address)
    assert Base32Address.is_valid_base32(custom_net_address)
    assert Base32Address.is_valid_base32(testnet_verbose_address)
    assert Base32Address.is_valid_base32(testnet_verbose_address.lower())
    assert Base32Address.is_valid_base32(testnet_address.upper())
    assert not Base32Address.is_valid_base32(invalid_net_address)
    assert not Base32Address.is_valid_base32(invalid_type_address)
    assert not Base32Address.is_valid_base32(mixed_testnet_address)
    assert Base32Address.is_valid_base32(unknown_type_address)
    for invalid in invalids:
        assert not Base32Address.is_valid_base32(invalid)
    

def test_encode():
    assert str(Base32Address.encode(hex_address, 1)) == testnet_address
    assert str(Base32Address.encode(hex_address, 1, True)) == testnet_verbose_address
    assert str(Base32Address.encode(hex_address, 1029)) == mainnet_address
    assert str(Base32Address.encode(hex_address, 1029, True)) == mainnet_verbose_address
    assert str(Base32Address.encode(hex_address, 8888)) == custom_net_address
    with pytest.raises(InvalidNetworkId):
        Base32Address.encode(hex_address, 0)
    with pytest.raises(InvalidHexAddress):
        Base32Address.encode(testnet_address, 1)
    
def test_normalize():
    assert str(Base32Address.normalize(hex_address, 1029)) == mainnet_verbose_address
    assert str(Base32Address.normalize(mainnet_address)) == mainnet_verbose_address 
    assert str(Base32Address.normalize(mainnet_address, 1)) == testnet_verbose_address 
    with pytest.raises(InvalidAddress):
        Base32Address.normalize(invalid_net_address, 1)

def test_equals():
    assert Base32Address.equals(testnet_address, testnet_verbose_address)
    assert not Base32Address.equals(testnet_address, mainnet_address)

def test_zero_address():
    assert Base32Address.zero_address(1) == "cfxtest:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa6f0vrcsw"

# def test_validation_util():
#     validate_hex_address("0x0")

def test_decode():
    assert Base32Address.decode(mainnet_address)["hex_address"] == hex_address
    assert Base32Address.decode(mainnet_address)["network_id"] == 1029
    assert Base32Address.decode(mainnet_address)["address_type"] == 'user'

def test_instance():
    instance = Base32Address(testnet_address)
    assert instance.network_id == 1
    assert instance.hex_address == hex_address
    assert instance.eth_checksum_address == checksum_address
    assert instance.verbose_address == testnet_verbose_address
    assert f"{instance}" == testnet_address
    
    assert instance == testnet_verbose_address
    assert instance == testnet_address
