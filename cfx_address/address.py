from typing import (
    Optional, 
    Union,
    cast,
    get_args
)

from hexbytes import HexBytes
from eth_typing.evm import (
    ChecksumAddress,
    HexAddress,
)
from eth_utils.crypto import (
    keccak
)
from eth_utils.address import (
    to_checksum_address,
    is_hex_address
)

from cfx_address import (
    base32, consts
)
from cfx_address.utils import (
    hex_address_bytes,
    validate_hex_address,
    validate_network_id
)
from cfx_address.types import (
    AddressType,
    Base32AddressParts,
    InvalidAddress,
    InvalidBase32Address,
    NetworkPrefix
)
from cfx_address.consts import (
    MAINNET_NETWORK_ID,
    TESTNET_NETWORK_ID,
    TYPE,
    MAINNET_PREFIX ,
    TESTNET_PREFIX,
    COMMON_NET_PREFIX,

    TYPE_NULL,
    TYPE_BUILTIN,
    TYPE_USER,
    TYPE_CONTRACT,
    TYPE_INVALID,
    HEX_PREFIX,
    DELIMITER,
    
    VERSION_BYTE,
    CHECKSUM_TEMPLATE,
)


class Base32Address(str):
    """Conflux base32 address"""
    
    consts = consts
    
    def __new__(cls, address: Union["Base32Address", HexAddress, str], network_id: Optional[int]=None, verbose: bool = False) -> "Base32Address":
        """
        if network_id is specified, normalize to the specified network

        Raises:
            InvalidAddress: _description_

        Returns:
            _type_: _description_
        """
        try:
            parts = cls.decode(address)
            if network_id is None:
                val = cls._encode(parts["hex_address"], parts["network_id"], verbose)
            else:
                validate_network_id(network_id)    
                val = cls._encode(parts["hex_address"], network_id, verbose)
        except InvalidBase32Address:
            if is_hex_address(address):
                validate_network_id(network_id)
                val = cls._encode(address, network_id, verbose) # type: ignore
            else:
                raise InvalidAddress("Address should be either base32 or hex, "
                                f"receives {address}")
        
        return str.__new__(cls, val)
    
    # @classmethod
    # def normalize(
    #     cls, address: Union["Base32Address", HexAddress, str], network_id: Optional[int]=None, verbose: bool = True
    # ) -> "Base32Address":
    #     return Base32Address(address, network_id, verbose)

    @classmethod
    def zero_address(cls, network_id: int) -> "Base32Address":
        return cls.encode("0x0000000000000000000000000000000000000000", network_id)

    @property
    def network_id(self) -> int:
        return Base32Address._decode_network_id(self)

    @property
    def hex_address(self) -> HexAddress:
        return Base32Address._decode_hex_address(self)

    @property
    def address_type(self) -> AddressType:
        return Base32Address._detect_address_type(hex_address_bytes(self.hex_address))

    @property
    def eth_checksum_address(self) -> ChecksumAddress:
        return to_checksum_address(self.hex_address)

    @property
    def verbose_address(self) -> "Base32Address":
        return Base32Address.encode(self.hex_address, self.network_id, True)
    
    @property
    def abbr(self) -> str:
        return Base32Address._shorten_base32_address(self)
    
    @property
    def compressed_abbr(self) -> str:
        return Base32Address._shorten_base32_address(self, True)
    
    @property
    def mapped_evm_space_address(self) -> HexAddress:
        return Base32Address._mapped_evm_address_from_hex(self.hex_address)

    # def to_network(self, network_id: int) -> "Base32Address":
    #     """returns a new Base32Address object
    #     >>> addr = Base32Address("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")
    #     >>> addr.to_network(1029)
    #     "cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu"
    #     >>> addr
    #     "cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4"
    #     """
    #     return Base32Address(self, network_id)

    def __eq__(self, __x: str) -> bool:
        parts = Base32Address.decode(__x)
        return self.hex_address == parts["hex_address"] and self.network_id == parts["network_id"]

    @classmethod
    def encode(
        cls, hex_address: str, network_id: int, verbose: bool=False
    ) -> "Base32Address":
        validate_hex_address(hex_address)
        validate_network_id(network_id)
        return Base32Address(hex_address, network_id, verbose)

    @classmethod
    def _encode(
        cls, hex_address: str, network_id: int, verbose: bool=False
    ) -> str:
        network_prefix = cls._encode_network_prefix(network_id)
        address_bytes = hex_address_bytes(hex_address)
        payload = base32.encode(VERSION_BYTE + address_bytes)
        checksum = cls._create_checksum(network_prefix, payload)
        parts = [network_prefix]
        if verbose:
            address_type = cls._detect_address_type(address_bytes)
            parts.append(f"{TYPE}.{address_type}")
        parts.append(payload + checksum)
        address = DELIMITER.join(parts)
        if verbose:
            return address.upper()
        return address

    @classmethod
    def _decode_network_id(cls, base32_address: str) -> int:
        base32_address = base32_address.lower()
        parts = base32_address.split(DELIMITER)
        return cls._network_prefix_to_id(parts[0])

    @classmethod
    def _decode_hex_address(cls, base32_address: str) -> HexAddress:
        base32_address = base32_address.lower()
        parts = base32_address.split(DELIMITER)
        return cls._payload_to_hex(parts[-1])

    @classmethod
    def _payload_to_hex(cls, payload: str) -> HexAddress:
        address_buf = base32.decode(payload)
        hex_buf = address_buf[1:21]
        return HEX_PREFIX + hex_buf.hex() # type: ignore

    # @classmethod
    # def _decode_address_type(cls, base32_address: str) -> AddressType:
    #     base32_address = base32_address.lower()
    #     hex_address = cls._decode_hex_address(base32_address)
    #     address_type = cls._detect_address_type(hex_address_bytes(hex_address))
    #     return address_type
    
    @classmethod
    def decode(cls, base32_address: str) -> Base32AddressParts:
        """
        raise an InvalidBase32Address exception if decode failure
        """
        try:
            if not isinstance(base32_address, str):
                raise InvalidBase32Address(f"Receives an argument of type {type(base32_address)}, expected a string")
            if not any([
                str(base32_address) == base32_address.upper(), 
                str(base32_address) == base32_address.lower(), 
            ]):
                raise InvalidBase32Address("Base32 address is supposed to be composed of all uppercase or lower case, "
                                        f"Receives {base32_address}")
            
            base32_address = base32_address.lower()

            splits = base32_address.split(DELIMITER)
            if len(splits) != 2 and len(splits) != 3:
                raise InvalidBase32Address(
                    "Address needs to be encode in Base32 format, such as cfx:aaejuaaaaaaaaaaaaaaaaaaaaaaaaaaaajrwuc9jnb\n"
                    "Received: {}".format(base32_address))

            # if exception occurs, outer try-except will handle
            address_parts = cls._decode(base32_address)

            # check address type
            address_type = address_parts["address_type"]
            if address_type == TYPE_INVALID:
                raise InvalidBase32Address(f"Invalid address type: the hex address of the provided address is {address_parts['hex_address']}, "
                                        "while valid conflux address is supposed to start with 0x0, 0x1 or 0x8")
            
            """
            cip-37 #Decoding
            6.Verify optional fields:

            If the optional fields contain type.*: Verify the address-type according to the specification above.
            Unknown options (options other than type.*) should be ignored.
            
            which means
            if address field is not expected, reject if the address field is a known one, else ignore
            e.g.
            valid CFX:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE7GGP3VPU
            invalid CFX:TYPE.NULL:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE7GGP3VPU
            ignore(but valid) CFX:GOD:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE7GGP3VPU
            """
            if len(splits) == 3 and splits[1] != f"{TYPE}.{address_type}":
                address_field = splits[1]
                if address_field.startswith(f"{TYPE}.") and address_field[5:] in get_args(AddressType):
                    raise InvalidBase32Address(f"Invalid address type field: the address type field does not match expected, "
                                            f"expected {TYPE}.{address_type} but receives {address_field}, which is a known address type")
            
            # check checksum
            hex_address = address_parts["hex_address"]
            address_bytes = hex_address_bytes(hex_address)
            payload = base32.encode(VERSION_BYTE + address_bytes)
            checksum = cls._create_checksum(splits[0], payload)
            if checksum != base32_address[-8:]:
                raise InvalidBase32Address(f"Invalid Base32 address: checksum verification failed")
            return address_parts
        except Exception as e:
            if isinstance(e, InvalidBase32Address):
                raise e
            else:
                # unexpected error
                raise InvalidBase32Address(
                    "Address needs to be a Base32 format string, such as cfx:aaejuaaaaaaaaaaaaaaaaaaaaaaaaaaaajrwuc9jnb\n"
                    f"Received argument {base32_address} of type {type(base32_address)}")
        
    @classmethod
    def _decode(cls, base32_address: str) -> Base32AddressParts:
        """ 
        do not validate unless necessary, used if validity is known
        """
        parts = base32_address.split(DELIMITER)
        network_id = cls._network_prefix_to_id(parts[0])
        hex_address = cls._payload_to_hex(parts[-1])
        address_type = cls._detect_address_type(hex_address_bytes(hex_address))
        return {
            "network_id": network_id,
            "hex_address": hex_address,
            "address_type": address_type
        }

    # @classmethod
    # def _has_network_prefix(cls, base32_address: str):
    #     base32_address = base32_address.lower()
    #     parts = base32_address.split(DELIMITER)
    #     if len(parts) < 2:
    #         return False
    #     if parts[0] in [MAINNET_PREFIX, TESTNET_PREFIX]:
    #         return True
    #     if parts[0].startswith(COMMON_NET_PREFIX):
    #         return True
    #     return False

    @classmethod
    def is_valid_base32(cls, base32_address: str) -> bool:
        try:
            cls.decode(base32_address)
            return True
        except:
            return False

    @classmethod
    def validate(cls, base32_address: str):
        """validate if an address is a valid base32_address, raises an exception if not
        """
        # an exception will be raised if decode failure
        cls.decode(base32_address)
        return True
  
    @classmethod
    def equals(cls, address1: str, address2: str) -> bool:
        """check if two address share same hex_address and network_id
        """
        return Base32Address(address1) == address2
    
    @classmethod
    def shorten_base32_address(cls, base32_address: str, compressed=False) -> str:
        cls.validate(base32_address)
        return cls._shorten_base32_address(base32_address, compressed)
    
    @classmethod
    def _shorten_base32_address(cls, base32_address: str, compressed=False) -> str:
        lowcase = base32_address.lower()
        splits = lowcase.split(DELIMITER)
        prefix = splits[0]
        payload = splits[-1]
        if splits[0] != MAINNET_PREFIX or compressed:
            return f"{prefix}{DELIMITER}{payload[:4]}...{payload[-4:]}"
        else:
            return f"{prefix}{DELIMITER}{payload[:4]}...{payload[-8:]}"
    
    @classmethod
    def calculate_mapped_evm_space_address(cls, base32_address: str) -> HexAddress:
        hex_address = cls.decode(base32_address)["hex_address"]
        return cls._mapped_evm_address_from_hex(hex_address)

    @classmethod
    def _mapped_evm_address_from_hex(cls, hex_address: HexAddress) -> HexAddress:
        # do not check hex_address validity here
        mapped_hash = keccak(HexBytes(hex_address)).hex()
        mapped_address = to_checksum_address(HEX_PREFIX + mapped_hash[-40:])
        return cast(HexAddress, mapped_address)

    @classmethod
    def _encode_network_prefix(cls, network_id: int) -> NetworkPrefix:
        if network_id == MAINNET_NETWORK_ID:
            return MAINNET_PREFIX
        elif network_id == TESTNET_NETWORK_ID:
            return TESTNET_PREFIX
        else:
            return COMMON_NET_PREFIX + str(network_id)

    @classmethod
    def _network_prefix_to_id(cls, network_prefix: NetworkPrefix) -> int:
        network_prefix = network_prefix.lower()
        if network_prefix == MAINNET_PREFIX:
            return MAINNET_NETWORK_ID
        elif network_prefix == TESTNET_PREFIX:
            return TESTNET_NETWORK_ID
        else:
            if not network_prefix.startswith(COMMON_NET_PREFIX):
                raise InvalidBase32Address(f"The network prefix {network_prefix} is invalid")
            try:
                return int(network_prefix[3:])
            except:
                raise InvalidBase32Address(f"The network prefix {network_prefix} is invalid")

    @classmethod
    def _create_checksum(cls, prefix, payload) -> str:
        """
        create checksum from prefix and payload
        :param prefix: network prefix (string)
        :param payload: bytes
        :return: string
        """
        prefix = cls._prefix_to_words(prefix)
        delimiter = VERSION_BYTE
        payload = base32.decode_to_words(payload)
        template = CHECKSUM_TEMPLATE
        mod = cls._poly_mod(prefix + delimiter + payload + template)
        return base32.encode(cls._checksum_to_bytes(mod))

    @classmethod
    def _detect_address_type(cls, hex_address_buf) -> AddressType:
        if hex_address_buf == bytes(20):
            return TYPE_NULL
        first_byte = hex_address_buf[0] & 0xf0
        if first_byte == 0x00:
            return TYPE_BUILTIN
        elif first_byte == 0x10:
            return TYPE_USER
        elif first_byte == 0x80:
            return TYPE_CONTRACT
        else:
            return TYPE_INVALID

    @classmethod
    def _prefix_to_words(cls, prefix) -> bytearray:
        words = bytearray()
        for v in bytes(prefix, 'ascii'):
            words.append(v & 0x1f)
        return words

    @classmethod
    def _checksum_to_bytes(cls, data) -> bytearray:
        result = bytearray(0)
        result.append((data >> 32) & 0xff)
        result.append((data >> 24) & 0xff)
        result.append((data >> 16) & 0xff)
        result.append((data >> 8) & 0xff)
        result.append((data) & 0xff)
        return result

    @classmethod
    def _poly_mod(cls, v: Union[bytes, bytearray]) -> int:
        """
        :param v: bytes
        :return: int64
        """
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
