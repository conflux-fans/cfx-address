from cfx_address import base32
from cfx_address.utils import (
    hex_address_bytes
)

MAIN_NET_NETWORK_ID = 1029
TEST_NET_NETWORK_ID = 1

class Address:
    """Conflux base32 address"""
    MAIN_NET_PREFIX = "cfx"
    TEST_NET_PREFIX = "cfxtest"
    COMMON_NET_PREFIX = "net"

    TYPE_NULL = "null"
    TYPE_BUILTIN = "builtin"
    TYPE_USER = "user"
    TYPE_CONTRACT = "contract"
    TYPE_INVALID = "invalid"
    TYPE = "type"

    HEX_PREFIX = "0x"
    DELIMITER = ":"

    VERSION_BYTE = bytes(1)
    CHECKSUM_TEMPLATE = bytes(8)

    def __init__(self, base32_address):
        assert type(base32_address) == str
        self._network_id = Address.decode_network_id(base32_address)
        self._hex_address = Address.decode_hex_address(base32_address)
        self._address = Address.encode_hex_address(self._hex_address, self._network_id)
        self._verbose_address = Address.encode_hex_address(self._hex_address, self._network_id, True)

    @classmethod
    def create_from_hex_address(cls, hex_address, network_id):
        return Address(cls.encode_hex_address(hex_address, network_id))

    @property
    def network_id(self):
        return self._network_id

    @property
    def hex_address(self):
        return self._hex_address

    @property
    def address(self):
        return self._address

    @property
    def verbose_address(self):
        return self._verbose_address

    @classmethod
    def encode_hex_address(cls, hex_address, network_id, verbose = False):
        assert type(hex_address) == str
        assert type(network_id) == int
        network_prefix = cls._encode_network_prefix(network_id)
        address_bytes = hex_address_bytes(hex_address)
        payload = base32.encode(cls.VERSION_BYTE + address_bytes)
        checksum = cls._create_checksum(network_prefix, payload)
        parts = [network_prefix]
        if verbose:
            address_type = cls._detect_address_type(address_bytes)
            parts.append(cls.TYPE + "." + address_type)
        parts.append(payload + checksum)
        address = cls.DELIMITER.join(parts)
        if verbose:
            return address.upper()
        return address

    @classmethod
    def decode_network_id(cls, base32_address):
        parts = base32_address.split(cls.DELIMITER)
        assert len(parts) >= 2, "invalid base32 address"
        return cls._decode_network_prefix(parts[0])

    @classmethod
    def decode_hex_address(cls, base32_address):
        assert type(base32_address) == str
        parts = base32_address.split(cls.DELIMITER)
        assert len(parts) >= 2, "invalid base32 address"
        address_buf = base32.decode(parts[-1])
        hex_buf = address_buf[1:21]
        return cls.HEX_PREFIX + hex_buf.hex()

    @classmethod
    def decode_address_type(cls, base32_address):
        hex_address = cls.decode_hex_address(base32_address)
        return cls._detect_address_type(hex_address_bytes(hex_address))

    @classmethod
    def has_network_prefix(cls, base32_address):
        parts = base32_address.split(cls.DELIMITER)
        if len(parts) < 2:
            return False
        if parts[0] in [cls.MAIN_NET_PREFIX, cls.TEST_NET_PREFIX]:
            return True
        if parts[0].startswith(cls.COMMON_NET_PREFIX):
            return True
        return False

    @classmethod
    def is_valid_base32(cls, base32_address):
        try:
            base32_address = base32_address.lower()
            if type(base32_address) != str:
                return False
            # check parts
            parts = base32_address.split(cls.DELIMITER)
            if len(parts) < 2:
                return False
            # check prefix
            if not cls.has_network_prefix(base32_address):
                return False
            # check address type
            address_type = cls.decode_address_type(base32_address)
            if address_type == cls.TYPE_INVALID:
                return False
            # check checksum
            hex_address = cls.decode_hex_address(base32_address)
            address_bytes = hex_address_bytes(hex_address)
            payload = base32.encode(cls.VERSION_BYTE + address_bytes)
            checksum = cls._create_checksum(parts[0], payload)
            if checksum != base32_address[-8:]:
                return False
            return True
        except:
            return False

    @classmethod
    def normalize_hex_address(cls, address):
        if cls.has_network_prefix(address):
            return cls.decode_hex_address(address)
        return address

    @classmethod
    def normalize_base32_address(cls, address, network_id):
        if not cls.has_network_prefix(address):
            assert network_id > 0
            return cls.encode_hex_address(address, network_id)
        return address

    @classmethod
    def _encode_network_prefix(cls, network_id):
        assert network_id > 0
        if network_id == MAIN_NET_NETWORK_ID:
            return cls.MAIN_NET_PREFIX
        elif network_id == TEST_NET_NETWORK_ID:
            return cls.TEST_NET_PREFIX
        else:
            return cls.COMMON_NET_PREFIX + network_id

    @classmethod
    def _decode_network_prefix(cls, network_prefix):
        if network_prefix == cls.MAIN_NET_PREFIX:
            return MAIN_NET_NETWORK_ID
        elif network_prefix == cls.TEST_NET_PREFIX:
            return TEST_NET_NETWORK_ID
        else:
            assert network_prefix.startswith(cls.COMMON_NET_PREFIX)
            return int(network_prefix.replace(cls.COMMON_NET_PREFIX, ""))

    @classmethod
    def _create_checksum(cls, prefix, payload):
        '''
        create checksum from prefix and payload
        :param prefix: network prefix (string)
        :param payload: bytes
        :return: string
        '''
        prefix = cls._prefix_to_words(prefix)
        delimiter = cls.VERSION_BYTE
        payload = base32.decode_to_words(payload)
        template = cls.CHECKSUM_TEMPLATE
        mod = cls._poly_mod(prefix + delimiter + payload + template)
        return base32.encode(cls._checksum_to_bytes(mod))

    @classmethod
    def _detect_address_type(cls, hex_address_buf):
        if hex_address_buf == bytes(20):
            return cls.TYPE_NULL
        first_byte = hex_address_buf[0] & 0xf0
        if first_byte == 0x00:
            return cls.TYPE_BUILTIN
        elif first_byte == 0x10:
            return cls.TYPE_USER
        elif first_byte == 0x80:
            return cls.TYPE_CONTRACT
        else:
            return cls.TYPE_INVALID

    @classmethod
    def _prefix_to_words(cls, prefix):
        words = bytearray()
        for v in bytes(prefix, 'ascii'):
            words.append(v & 0x1f)
        return words

    @classmethod
    def _checksum_to_bytes(cls, data):
        result = bytearray(0)
        result.append((data >> 32) & 0xff)
        result.append((data >> 24) & 0xff)
        result.append((data >> 16) & 0xff)
        result.append((data >> 8) & 0xff)
        result.append((data) & 0xff)
        return result

    @classmethod
    def _poly_mod(cls, v):
        '''
        :param v: bytes
        :return: int64
        '''
        assert type(v) == bytes or type(v) == bytearray
        c = 1
        for d in v:
            c0 = c >> 35
            c = ((c & 0x07ffffffff) << 5) ^ d
            if c0 & 0x01:
                c ^= 0x98f2bc8e61
            if c0 & 0x02:
                c ^= 0x79b76d99e2
            if c0 & 0x04:
                c ^= 0xf33e5fb3c4
            if c0 & 0x08:
                c ^= 0xae2eabe2a8
            if c0 & 0x10:
                c ^= 0x1e4f43e470

        return c ^ 1
