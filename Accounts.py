from datetime import date
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, SecretStr, HttpUrl, SecretBytes, Json, ValidationError
from pydantic.types import PaymentCardBrand, PaymentCardNumber, constr
from pprint import pprint
import orjson

def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()

class BankDebit(BaseModel):
    name: constr(strip_whitespace=True, min_length=4)
    account_number: Optional[SecretStr] = Field(alias='account_num')
    expiration_date: Optional[date]
    credit_card_number: Optional[PaymentCardNumber]
    _name: str = Field(alias='name')
    contact: Dict[str, str] = None
    url: Optional[HttpUrl]
    data: Optional[Json[List[int]]]

    @property
    def brand(self) -> PaymentCardBrand:
        return self.credit_card_number.brand

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None,
            SecretBytes: lambda v: v.get_secret_value() if v else None,
        }
        json_loads = orjson.loads
        json_dumps = orjson_dumps

class Bank(BaseModel):
    bank_name: constr(strip_whitespace=True, min_length=4) = Field(alias='name')
    bank_address: str

class Me:
    def __init__(self, kwarg) -> None:
        self.__dict__.update(BankDebit(**kwarg))

external_data = {
    'name': 'MyAwesomeBank ',
    'account_num': '123',
    'credit_card_number': '4000000000000002',
    'contact': {
        'phone': '859-345-3453'
    },
}

def test_duck():
    try:
        user = BankDebit(**external_data)
    except ValidationError as e:
        print(e.json())

    print(user._name)
    pprint(user.dict())
    print(user.brand)
    print(user.account_number.get_secret_value())
    print(user.json())

me = Me(external_data)
print(dir(me))