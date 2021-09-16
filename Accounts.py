from datetime import date, datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, SecretStr, HttpUrl, SecretBytes, Json, ValidationError, validator
from pydantic.types import PaymentCardBrand, PaymentCardNumber, constr
from pprint import pprint
import orjson

def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Checking(BaseModel):
    current_balance: float
    pending_balance: float
    as_of: date


class CreditCard(BaseModel):
    current_balance: float
    pending_balance: float
    as_of: date
    minimum_payment: float
    payment_due_date: date
    apr: float
    remaining_balance: float
    credit_card_number: PaymentCardNumber = Field(alias='account_num')
    expiration: date
    cvv: str

    @validator('cvv')
    def cvv_must_be_3_numbers(cls, v):
        if (len(str(v)) !=3) & int(v) >= 0:
            raise ValidationError('CVV is invalid')
        return str(v)    
    
    @property
    def brand(self) -> PaymentCardBrand:
        return self.credit_card_number.brand


class Debit(BaseModel):
    bank_name: constr(strip_whitespace=True, min_length=4) = Field(alias='name')
    bank_address: str
    as_of: datetime

class BankingService(BaseModel):
    bank_name: constr(strip_whitespace=True, min_length=4) = Field(alias='name')
    username: SecretStr
    password: SecretStr
    account_number: Optional[SecretStr] 
    expiration_date: Optional[date]
    credit_card_number: Optional[PaymentCardNumber]
    contact: Dict[str, str] = None
    url: Optional[HttpUrl]
    data: Optional[Json[List[int]]]
    debit_accounts: Optional[List[Debit]]
    credit_accounts: Optional[List[CreditCard]]


    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None,
            SecretBytes: lambda v: v.get_secret_value() if v else None,
        }
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class MyAccount:
    def __init__(self, kwarg) -> None:
        self.__dict__.update(BankingService(**kwarg))

external_data = {
    'name': 'MyAwesomeBank ',
    'username': 'myusername',
    'password': 'paswword',
    'account_num': '123',
    'credit_card_number': '4000000000000002',
    'cvv': 5124,
    'contact': {
        'phone': '859-345-3453'
    },
}

def test_BankingService_schema():
    try:
        BankingService(**external_data)
    except ValidationError as e:
        print(e.json())

me = MyAccount(external_data)
print(dir(me))