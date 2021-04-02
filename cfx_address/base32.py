import base64

STANDARD_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
CUSTOM_ALPHABET   = 'abcdefghjkmnprstuvwxyz0123456789'
ENCODE_TRANS = str.maketrans(STANDARD_ALPHABET, CUSTOM_ALPHABET)
DECODE_TRANS = str.maketrans(CUSTOM_ALPHABET, STANDARD_ALPHABET)
PADDING_LETTER = '='

def encode(buffer):
    assert type(buffer) == bytes or type(buffer) == bytearray, "please pass an bytes"
    b32encoded = base64.b32encode(buffer) # encode bytes
    b32str = b32encoded.decode().replace(PADDING_LETTER, "") # translate chars
    return b32str.translate(ENCODE_TRANS) # remove padding char

def decode(b32str):
    assert type(b32str) == str, "please pass an str"
    # pad to 8's multiple with '='
    b32len = len(b32str)
    if b32len % 8 > 0:
        padded_len = b32len + (8 - b32len % 8)
        b32str = b32str.ljust(padded_len, PADDING_LETTER)
    # translate and decode
    return base64.b32decode(b32str.translate(DECODE_TRANS))

def decode_to_words(b32str):
    result = bytearray()
    for c in b32str:
        result.append(CUSTOM_ALPHABET.index(c))
    return result

def encode_words(words):
    result = ""
    for v in words:
        result += CUSTOM_ALPHABET[v]
    return result