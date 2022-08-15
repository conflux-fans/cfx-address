import base64
from typing import Iterable, Union

STANDARD_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
CUSTOM_ALPHABET = 'abcdefghjkmnprstuvwxyz0123456789'
ENCODE_TRANS = str.maketrans(STANDARD_ALPHABET, CUSTOM_ALPHABET)
DECODE_TRANS = str.maketrans(CUSTOM_ALPHABET, STANDARD_ALPHABET)
PADDING_LETTER = '='


def encode(buffer: Union[bytes, bytearray]) -> str:
    assert type(buffer) == bytes or type(buffer) == bytearray, "please pass an bytes"
    b32encoded = base64.b32encode(buffer)  # encode bytes
    b32str = b32encoded.decode().replace(PADDING_LETTER, "")  # translate chars
    return b32str.translate(ENCODE_TRANS)  # remove padding char


def decode(b32str: str) -> bytes:
    if not isinstance(b32str, str):
        raise TypeError(f"Invalid argument type: base32 decode requires a string type argument "
                        f"but receives an argument of type {type(b32str)}")
    if b32str != b32str.lower():
        raise ValueError(f"Invalid value: only lower case letters are used for base32 address, "
                        f"receives {b32str}")
    # pad to 8's multiple with '='
    b32len = len(b32str)
    if b32len % 8 > 0:
        padded_len = b32len + (8 - b32len % 8)
        b32str = b32str.ljust(padded_len, PADDING_LETTER)
    # translate and decode
    return base64.b32decode(b32str.translate(DECODE_TRANS))


def decode_to_words(b32str: str) -> bytearray:
    result = bytearray()
    for c in b32str:
        result.append(CUSTOM_ALPHABET.index(c))
    return result


def encode_words(words: Iterable[int]) -> str:
    result = ""
    for v in words:
        result += CUSTOM_ALPHABET[v]
    return result
