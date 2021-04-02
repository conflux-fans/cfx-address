
def eth_address_to_cfx(address: str):
    assert type(address) == str
    return '0x1' + address.lower()[3:]

def hex_address_bytes(hex_address: str):
    assert type(hex_address) == str
    return bytes.fromhex(hex_address.lower().replace('0x', ""))