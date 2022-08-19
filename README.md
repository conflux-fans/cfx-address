# cfx-address

Conflux base32 address utilities

Full documentation -> https://conflux-fans.github.io/cfx-address/cfx_address.html#module-cfx_address

## installation

```bash
pip install cfx-address
```

### use Base32Address class methods

```python
from cfx_address import Base32Address
```

#### validate a base32 address
``` python
Base32Address.is_valid_base32("0x1ecde7223747601823f7535d7968ba98b4881e09") 
# False
Base32Address.validate("0x1ecde7223747601823f7535d7968ba98b4881e09")
# will raise an exception
```

#### encode and decode

``` python
# encode hex address to base32
Base32Address.encode("0x1ecde7223747601823f7535d7968ba98b4881e09", network_id=1)
#'cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4'

# decode base32 address
Base32Address.decode("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")
# result:
# {'network_id': 1,
# 'hex_address': '0x1ecde7223747601823f7535d7968ba98b4881e09',
# 'address_type': 'user'}
```

#### utilities

```python
address_str = "cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4"
address_verbose_str = "CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4"
assert Base32Address.equals(address_str, address_verbose_str)

Base32Address.calculate_mapped_evm_space_address(address_str)
Base32Address.zero_address(network_id=1)
Base32Address.shorten_base32_address(address_str)
```

### Base32Address instances

#### instance initialization

```python
address = Base32Address("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")
# 'cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4'

# Base32Address inherits from str
assert isinstance(address, str)

# init from hex address, in which case network_id is required
Base32Address("0x1ecde7223747601823f7535d7968ba98b4881e09", network_id=1029)
# 'cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu'

# change a base32 address to other network
Base32Address(address, network_id=1029)
# 'cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu'

# verbose option defaults to False
Base32Address(address, verbose=True)
# 'CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4'
```

#### __eq__ and properties

```python
# __eq__ is implemented, address in same network is treated equal
assert address == "cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4"
assert address == "CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4"
assert "CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4" == address
assert "cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4" == address

# address in different network is not equal
mainnet_address = Base32Address(address, 1029)
assert mainnet_address == "cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu"
assert not address == mainnet_address

# properties
[
    address.address_type,
    address.network_id,
    address.hex_address,
    address.verbose_address,
    address.short,
    address.mapped_evm_space_address
    address.eth_checksum_address
]
# ['user',
#  1,
#  '0x1ecde7223747601823f7535d7968ba98b4881e09',
#  'CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4',
#  'cfxtest:aat...95j4',
#  '0x349f086998cF4a0C5a00b853a0E93239D81A97f6',
#  '0x1ECdE7223747601823f7535d7968Ba98b4881E09']
```
