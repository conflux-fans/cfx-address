from pydantic import TypeAdapter, BaseModel
from typing_extensions import TypedDict
from cfx_address.address import Base32Address


class NestedTypedDict(TypedDict):
    address: Base32Address

class ModelWithNestedTypedDict(BaseModel):
    nested: NestedTypedDict

def test_pydantic_validator():
    ta = TypeAdapter(Base32Address)
    res = ta.validate_python("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")
    assert res == "cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4"
    res = ta.validate_python(Base32Address("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4"))
    assert res == "cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4"

def test_nested_typed_dict_with_base32address():
    data = {
        "nested": {
            "address": Base32Address("cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4")
        }
    }
    model = ModelWithNestedTypedDict(**data)
    assert model.nested["address"] == "cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4"
