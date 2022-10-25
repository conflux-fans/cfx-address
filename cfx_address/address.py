from typing import (
    Any,
    Literal,
    Optional,
    Type, 
    Union,
    cast,
    get_args,
    ClassVar
)

import functools

from hexbytes import (
    HexBytes
)
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
    base32
)
from cfx_address._utils import (
    validate_hex_address,
    validate_network_id
)
from cfx_address.types import (
    AddressType,
    Base32AddressParts,
    NetworkPrefix,
)
from cfx_utils.exceptions import (
    InvalidAddress,
    InvalidBase32Address,
    InvalidConfluxHexAddress,
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
from cfx_address._utils import (
    public_key_to_cfx_hex
)

default = object()

class Base32AddressMeta(type):
    @property
    def default_network_id(self) -> Union[int, None]:
        """
        Default network id of Base32Address.
        Base32Address constructor, Base32Address.encode, and Base32Address.zero_address will use this variable if network_id parameter is not specified.
        For most cases, it is recommended not to directly set this variable but use the `cfx_address.address.get_base32_address_factory(default_network_id)` to specify default_network_id 
        
        >>> Base32Address.zero_address()
        Traceback (most recent call last):
            ...
        cfx_utils.exceptions.InvalidNetworkId: Expected network_id to be a positive integer. Receives None of type <class 'NoneType'>
        >>> from cfx_address.address import get_base32_address_factory
        >>> base32_address_factory = get_base32_address_factory(default_network_id=1)
        >>> base32_address_factory.zero_address()
        'cfxtest:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa6f0vrcsw'
        """ 
        return self._default_network_id
    
    @default_network_id.setter
    def default_network_id(cls, new_default: Union[None, int]) -> None: 
        """
        Set default network id of Base32Address by setting class variable `default_network_id`.
        For most cases, it is recommended not to directly set this variable but use the `cfx_address.address.get_base32_address_factory(default_network_id)` to specify default_network_id 

        :param Union[None, int] new_default: new default network id, could be None or positive int
        """   
        if new_default is not None:
            validate_network_id(new_default)
        cls._default_network_id = new_default

class Base32Address(str, metaclass=Base32AddressMeta):
    """
    Class Base32Address can be used to create Base32Address instances and provides useful class methods to deal with base32 format addresses.
    ## Base32Address inherits from str, so the Base32Address can be trivially used as strings
    
    :examples:
    
    >>> address = Base32Address("0x1ecde7223747601823f7535d7968ba98b4881e09", network_id=1)
    >>> address
    'cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4'
    >>> [
    ...     address.address_type,
    ...     address.network_id,
    ...     address.hex_address,
    ...     address.verbose_address,
    ...     address.abbr,
    ...     address.mapped_evm_space_address,
    ...     address.eth_checksum_address,
    ... ]
    ['user', 1, '0x1ecde7223747601823f7535d7968ba98b4881e09', 'CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4', 'cfxtest:aat...95j4', '0x349f086998cF4a0C5a00b853a0E93239D81A97f6', '0x1ECdE7223747601823f7535d7968Ba98b4881E09']
    """
    _default_network_id: ClassVar[Optional[int]] = None
    
    def __new__(cls, address: Union["Base32Address", HexAddress, str], network_id: Optional[int]=cast(int, default), verbose: Optional[bool] = None, *, _from_trust: bool = False, _ignore_invalid_type: bool = False) -> "Base32Address":
        """
        :param Union[Base32Address, HexAddress, str] address: a base32-or-hex format address
        :param Optional[int] network_id: target network_id of the address, defaults to `Base32Address.default_network_id`. Can be None if first argument is a base32 address, which means don't change network id
        :param Optional[bool] verbose: whether the return value will be encoded in verbose mode, defaults to None (will be viewed as None)
        :param bool _from_trust: whether the value is a verified Base32Address, if true, network_id and verbose option should be None, and the verification and encoding process will be skipped. Not recommended to set unless preformance is critical. Defaults to False
        :param bool _ignore_invalid_type: whether the address type is validated, defaults to False
        :raises InvalidAddress: address is neither base32 address nor hex address
        :raises InvalidNetworkId: network_id argument is not a positive integer or is None when address argument is a hex address
        :return Base32Address: an encoded base32 object, which can be trivially used as python str, specially, if from_trusted_source is true, the input value will be directly used as the encoded value
        
        :examples:
        
        >>> address = Base32Address("0x1ecde7223747601823f7535d7968ba98b4881e09", network_id=1)
        >>> address
        'cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4'
        >>> address_ = Base32Address(address, network_id=1029, verbose=True)
        >>> address_
        'CFX:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE7GGP3VPU'
        >>> isinstance(address_, str)
        True
        """
        if network_id is default:
            # if network_id is not specified (default),
            # # network_id will be cls.default_network_id, which defaults to None
            network_id = cls.default_network_id
        # if _from_trust is True, 
        # it requires network_id is None and verbose is None
        # the new Base32Address will be initialized without validating, which means you can do
        # Base32Address("hello world", network_id=None, verbose=None, _from_trust=True)
        # so this API should be used carefully 
        if _from_trust:
            if network_id is None and verbose is None:
                return str.__new__(cls, address)
            else:
                raise ValueError("Invalid argument: `network_id` and `verbose` should be None if from_trusted_source is True")
        
        try:
            parts = cls.decode(address) # this line might raise exception if the address is not valid
            if verbose is None:
                # if verbose is None, the new address verbose is determined by the original address
                verbose = (address[0] == "N" or address[0] == "C")
            if network_id is None:
                # if network_id is None, the new address verbose is determined by the original address
                network_id = parts["network_id"]

            validate_network_id(network_id)  
            val = cls._encode(parts["hex_address"], network_id, verbose, _ignore_invalid_type=_ignore_invalid_type)
        except InvalidBase32Address:
            if verbose is None:
                verbose = False
            if is_hex_address(address):
                validate_network_id(network_id)
                val = cls._encode(address, network_id, verbose, _ignore_invalid_type=_ignore_invalid_type) # type: ignore
            else:
                raise InvalidAddress("Address should be either base32 or hex, "
                                f"receives {address}")
        
        return str.__new__(cls, val)
    
    def __eq__(self, _address: object) -> bool:
        """
        invoked when a base32 address is compared to another object (or Base32Address typed object),
        
        :param str _address: value compared to, which is supposed to be encoded in Base32 format (else return false)
        :return bool: True if self and _address are of same hex_address and network_id
        :raises InvalidBase32Address: _address is not encoded in base32 format
        :examples:
        
        >>> address = Base32Address("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")
        >>> assert address == "CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4"
        >>> assert "CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4" == address
        >>> assert "cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4" == address
        """
        try:
            parts = self.__class__.decode(_address) # type: ignore
            return self.hex_address == parts["hex_address"] and self.network_id == parts["network_id"]
        except:
            return False
        
    def __ne__(self, _address: object) -> bool:
        return not (self == _address)

    def __hash__(self) -> int:
        return super().__hash__()

    @classmethod
    def from_public_key(
        cls, 
        public_key: Union[str, bytes],
        network_id: int,
        verbose: bool = False
    ) -> "Base32Address":
        """
        create a Base32Address from public key

        :param Union[str, bytes] public_key: str or bytes representation of public key
        :param int network_id: network id of the return Base32Address, defaults to None
        :param bool verbose: whether the address will be represented in verbose mode, defaults to False
        :return Base32Address: Base32 representation of the address
        
        >>> Base32Address.from_public_key("0xdacdaeba8e391e7649d3ac4b5329ca0e202d38facd928d88b5f729b89a497e43cc4ad3816fcfdb241497b3b43862afb4c899bc284bf60feca4ee66ff868d1feb", 1)
        'cfxtest:aamw4kj6g41pgedw1efjnsm59fbz0b9r1awbp8k2p2'
        """
        hex_address = public_key_to_cfx_hex(public_key)
        return cls(hex_address, network_id, verbose)

    @functools.cached_property
    def network_id(self) -> int:
        """
        :return int: network_id of the address
        :examples:
        
        >>> address = Base32Address("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")
        >>> address.network_id
        1
        """        
        return self.__class__._decode_network_id(self)

    @functools.cached_property
    def hex_address(self) -> HexAddress:
        """
        :return HexAddress: hex address of the address.
        
        >>> address = Base32Address("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")
        >>> address.hex_address
        '0x1ecde7223747601823f7535d7968ba98b4881e09'
        """        
        return self.__class__._decode_hex_address(self)

    @functools.cached_property
    def address_type(self) -> AddressType:
        """
        :return Literal["null", "builtin", "user", "contract", "invalid"]: address type of an address. 
        
        :examples:
        
        >>> address = Base32Address("cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu")
        >>> address.address_type
        'user'
        """      
        return self.__class__._detect_address_type(HexBytes(self.hex_address))

    @functools.cached_property
    def eth_checksum_address(self) -> ChecksumAddress:
        """
        :return ChecksumAddress: self.hex_address in ethereum checksum address format
        
        >>> address = Base32Address("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")
        >>> address.hex_address
        '0x1ecde7223747601823f7535d7968ba98b4881e09'
        >>> address.eth_checksum_address
        '0x1ECdE7223747601823f7535d7968Ba98b4881E09'
        """        
        return to_checksum_address(self.hex_address)

    @functools.cached_property
    def verbose_address(self) -> "Base32Address":
        """
        :return Base32Address: self presented in verbose mode
        
        >>> address = Base32Address("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")
        >>> address.verbose_address
        'CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4'
        """        
        return self.__class__.encode(self.hex_address, self.network_id, True)
    
    @functools.cached_property
    def abbr(self) -> str:
        """
        :return str: abbreviation of the address, as mentioned in https://forum.conflux.fun/t/voting-results-for-new-address-abbreviation-standard/7131
        
        :examples:
        
        >>> Base32Address("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4").abbr
        'cfxtest:aat...95j4'
        >>> Base32Address("cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu").abbr
        'cfx:aat...7ggp3vpu'
        """        
        return self.__class__._shorten_base32_address(self)
    
    @functools.cached_property
    def compressed_abbr(self) -> str:
        """
        :return str: compressed abbreviation of the address, same as property "abbr" except for mainnet address
             
        :examples:
        
        >>> address = Base32Address("cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu")
        >>> address.abbr
        'cfx:aat...7ggp3vpu'
        >>> address.compressed_abbr
        'cfx:aat...3vpu'
        """ 
        return self.__class__._shorten_base32_address(self, True)
    
    @functools.cached_property
    def mapped_evm_space_address(self) -> HexAddress:
        """
        :return HexAddress: the address of mapped account for EVM space as defined in https://github.com/Conflux-Chain/CIPs/blob/master/CIPs/cip-90.md#mapped-account
        
        >>> address = Base32Address("cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu")
        >>> address.mapped_evm_space_address
        '0x349f086998cF4a0C5a00b853a0E93239D81A97f6'
        """
        return self.__class__._mapped_evm_address_from_hex(self.hex_address)

    @classmethod
    def encode( # type: ignore
        cls, hex_address: str, network_id: int=cast(int, default), verbose: bool=False, *, _ignore_invalid_type: bool=False
    ) -> "Base32Address":
        """
        encode hex address to base32 address

        :param str hex_address: hex address begins with 0x
        :param int network_id: address network id, e.g., 1 for testnet and 1029 for mainnet, defaults to `Base32Address.default_network_id`
        :param bool verbose: whether the address will be presented in verbose mode, defaults to False
        :param bool _ignore_invalid_type: whether the address type is validated, defaults to False
        :return Base32Address: an encoded base32 object, which can be trivially used as python str
        
        :examples:
        
        >>> Base32Address.encode("0x1ecde7223747601823f7535d7968ba98b4881e09", 1)
        'cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4'
        >>> Base32Address.encode("0x1ecde7223747601823f7535d7968ba98b4881e09", 1029, verbose=True)
        'CFX:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE7GGP3VPU'
        """ 
        if network_id is default:
            network_id = cast(int, cls.default_network_id)
        validate_hex_address(hex_address)
        validate_network_id(network_id)
        return cls(hex_address, network_id, verbose, _ignore_invalid_type=_ignore_invalid_type)

    @classmethod
    def _encode(
        cls, hex_address: str, network_id: int, verbose: bool, *, _ignore_invalid_type: bool=False
    ) -> str:
        network_prefix = cls._encode_network_prefix(network_id)
        address_bytes = HexBytes(hex_address)
        payload = base32.encode(VERSION_BYTE + address_bytes)
        checksum = cls._create_checksum(network_prefix, payload)
        parts = [network_prefix]
        address_type = cls._detect_address_type(address_bytes)
        if address_type == TYPE_INVALID and not _ignore_invalid_type:
            raise InvalidConfluxHexAddress(f"The hex address should start with 0x0, 0x1 or 0x8, received {hex_address}."
                                        "Check your code logic or set _ignore_invalid_type=True")
        if verbose:
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
    
    @classmethod
    def decode(cls, base32_address: str) -> Base32AddressParts:
        """
        Decode a base32 address string and get its hex_address, address_type, and network_id

        :param str base32_address: address encoded in base32 format
        :raises InvalidBase32Address:
        :return Base32AddressParts: a dict object with field "hex_address", "address_type" and "network_id"
        
        :examples:
        
        >>> Base32Address.decode("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")
        {'network_id': 1, 'hex_address': '0x1ecde7223747601823f7535d7968ba98b4881e09', 'address_type': 'user'}
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
                    "Address needs to be encode in Base32 format, such as cfx:aaejuaaaaaaaaaaaaaaaaaaaaaaaaaaaajrwuc9jnb. "
                    "Received: {}".format(base32_address))

            # if exception occurs, outer try-except will handle
            address_parts = cls._decode(base32_address)

            # check address type
            address_type = address_parts["address_type"]
            # it is ok to decode an address whose type is invalid
            # if address_type == TYPE_INVALID:
            #     raise InvalidBase32Address(f"Invalid address type: the hex address of the provided address is {address_parts['hex_address']}, "
            #                             "while valid conflux address is supposed to start with 0x0, 0x1 or 0x8")
            
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
            address_bytes = HexBytes(hex_address)
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
        address_type = cls._detect_address_type(HexBytes(hex_address))
        return {
            "network_id": network_id,
            "hex_address": hex_address,
            "address_type": address_type
        }

    @classmethod
    def is_valid_base32(cls, value: Any) -> bool:
        """
        Whether a value is a valid string-typed base32 address
        
        :return bool: True if valid, else False
        """        
        try:
            cls.decode(value)
            return True
        except:
            return False

    @classmethod
    def validate(cls, value: Any) -> Literal[True]:
        """
        validate if a value is a valid string-typed base32_address, raises an exception if not

        :param str value: value to validate 
        :raises InvalidBase32Address: raises an exception if the address is not a valid base32 address
        :return Literal[True]: returns True only if address is valid
        """
        # an exception will be raised if decode failure
        cls.decode(value)
        return True
  
    @classmethod
    def equals(cls, address1: str, address2: str) -> bool:
        """
        check if two addresses share same hex_address and network_id

        :param str address1: base32 address to compare
        :param str address2: base32 address to compare
        :raises InvalidBase32Address: either address is not a valid base32 address
        :return bool: whether two addresses share same hex_address and network_id
        """
        return cls(address1) == cls(address2)
    
    @classmethod
    def zero_address(cls, network_id: int=cast(int, default), verbose: bool = False) -> "Base32Address":    
        """
        Get zero address of the target network.

        :param int network_id: target network_id, defaults to `Base32Address.default_network_id`
        :param bool verbose: whether the zero address is presented in verbose mode, defaults to False
        :return Base32Address: base32 format zero address of the target network 
        :examples:
        
        >>> Base32Address.zero_address(network_id=1)
        'cfxtest:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa6f0vrcsw'
        """        
        if network_id is default:
            network_id = cast(int, cls.default_network_id)
        return cls.encode("0x0000000000000000000000000000000000000000", network_id, verbose)
    
    @classmethod
    def shorten_base32_address(cls, base32_address: str, compressed: bool=False) -> str:
        """
        returns the abbreviation of the address

        :param str base32_address: address to shorten
        :raises InvalidBase32Address: raised if address is invalid
        :param bool compressed: whether the abbreviation will be presented in compressed form,\
            which only affects mainnet addresses, defaults to False
        :return str: the abbreviation string
        
        >>> Base32Address.shorten_base32_address("cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu")
        'cfx:aat...7ggp3vpu'
        >>> Base32Address.shorten_base32_address("cfx:aatp533cg7d0agbd87kz48nj1mpnkca8be7ggp3vpu", compressed=True)
        'cfx:aat...3vpu'
        """        
        cls.validate(base32_address)
        return cls._shorten_base32_address(base32_address, compressed)
    
    @classmethod
    def _shorten_base32_address(cls, base32_address: str, compressed: bool=False) -> str:
        lowcase = base32_address.lower()
        splits = lowcase.split(DELIMITER)
        prefix = splits[0]
        payload = splits[-1]
        if splits[0] != MAINNET_PREFIX or compressed:
            return f"{prefix}{DELIMITER}{payload[:3]}...{payload[-4:]}"
        else:
            return f"{prefix}{DELIMITER}{payload[:3]}...{payload[-8:]}"
    
    @classmethod
    def calculate_mapped_evm_space_address(cls, base32_address: str) -> HexAddress:
        """
        calculate the address of mapped account for EVM space as defined in https://github.com/Conflux-Chain/CIPs/blob/master/CIPs/cip-90.md#mapped-account

        :raises InvalidBase32Address: raised when address is not a valid base32 address
        :examples:
        
        >>> Base32Address.calculate_mapped_evm_space_address("CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4")
        '0x349f086998cF4a0C5a00b853a0E93239D81A97f6'
        """        
        hex_address = cls.decode(base32_address)["hex_address"]
        return cls._mapped_evm_address_from_hex(hex_address)

    @classmethod
    def _mapped_evm_address_from_hex(cls, hex_address: HexAddress) -> HexAddress:
        # do not check hex_address validity here
        mapped_hash = keccak(HexBytes(hex_address)).hex()
        mapped_evm_space_address = to_checksum_address(HEX_PREFIX + mapped_hash[-40:])
        return cast(HexAddress, mapped_evm_space_address)

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
    def _create_checksum(cls, prefix: NetworkPrefix, payload: str) -> str:
        """
        create checksum from prefix and payload
        :param prefix: network prefix (string)
        :param payload: bytes
        :return: string
        """
        delimiter = VERSION_BYTE
        template = CHECKSUM_TEMPLATE
        mod = cls._poly_mod(cls._prefix_to_words(prefix) + delimiter + base32.decode_to_words(payload) + template)
        return base32.encode(cls._checksum_to_bytes(mod))

    @classmethod
    def _detect_address_type(cls, hex_address_buf: bytes) -> AddressType:
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
    def _prefix_to_words(cls, prefix: NetworkPrefix) -> bytearray:
        words = bytearray()
        for v in bytes(prefix, 'ascii'):
            words.append(v & 0x1f)
        return words

    @classmethod
    def _checksum_to_bytes(cls, data: int) -> bytearray:
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

def get_base32_address_factory(default_network_id: int) -> Type[Base32Address]:
    """
    Generate a `Base32Address` Class object with `default_network_id`
    
    >>> base32_address_factory = get_base32_address_factory(default_network_id=1)
    >>> base32_address_factory.zero_address()
    'cfxtest:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa6f0vrcsw'

    :param int default_network_id: default network 
    :return Type[Base32Address]: a Class object of Base32Address with default_network_id
    """
    return type(
        "Base32Address",
        (Base32Address,),
        {
            "_default_network_id": default_network_id
        }
    )
