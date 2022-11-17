# changlog

## 1.0.0-beta.16

* All returned hex address is all encoded in checksum format, including
  * `Base32Address.decode`
  * `Base32Address(...).hex_address`
  * `normaliz_to`
  * The definition change of `AddressParts`
  * And `.eth_checksum_address` will be deprecated in the next version

## 1.0.0-beta.15

* Support python3.7

## 1.0.0-beta.14

* migrate to pylance
* Fix: `Base32Address` initialization logic when `verbose is None`

## 1.0.0-beta.13

* Mypy integration and support
* support default network id

## 1.0.0-beta.12

* Fix bug that `obj1 == obj2` is not equivalent to `not obj1 != obj2`

## 1.0.0-beta.11

* Fix `Base32Address.__eq__` comparison problem when the address to compare is not a str-typed object
* improve `utils.normalize_to` type hint

## 1.0.0-beta.10

* Add `_ignore_invalid_type` from address initialization from initialization and `Base32Address.encode`
* Remove force address type validation from `Base32Address.decode`

## 1.0.0-beta.9

* Add `_from_trust` option for address initialization. If set, the address initialization will not validate address input and will directly use the input as an encoded base32 address
* Add `public_key_to_cfx_hex` util. Add `Base32Address.from_public_key`
* internal util `hex_address_bytes` is removed, and is replaced by using `hexbytes.HexBytes`
