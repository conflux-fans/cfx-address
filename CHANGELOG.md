# changlog

## 1.0.0-beta.10

* Add `_ignore_invalid_type` from address initialization from initialization and `Base32Address.encode`
* Remove force address type validation from `Base32Address.decode`

## 1.0.0-beta.9

* Add `_from_trust` option for address initialization. If set, the address initialization will not validate address input and will directly use the input as an encoded base32 address
* Add `public_key_to_cfx_hex` util. Add `Base32Address.from_public_key`
* internal util `hex_address_bytes` is removed, and is replaced by using `hexbytes.HexBytes`
