from cfx_address import base32

hex_address = '02e1a5817abf2812f04c744927fc91f03099c0f4'
base32_address = 'anu4nan416ybf6cpsvewt9ev8a2kxuhy'

def test_encode():
  assert base32.encode(bytes.fromhex(hex_address)) == base32_address
  assert base32.encode("hello world".encode("utf-8")) == "rbw025dteb5086xppu"

def test_decode():
  assert base32.decode("rbw025dteb5086xppu").decode() == "hello world"
  assert base32.decode(base32_address).hex() == hex_address