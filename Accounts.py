from datetime import date, datetime
from typing import List, Optional, Dict
from pydantic import (
    BaseModel,
    Field,
    SecretStr,
    HttpUrl,
    SecretBytes,
    Json,
    ValidationError,
    validator,
)
from pydantic.types import PaymentCardBrand, PaymentCardNumber, constr
import orjson
from mock_account import external_data


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
    credit_card_number: PaymentCardNumber = Field(alias="account_num")
    expiration: date
    cvv: str

    @validator("cvv")
    def cvv_must_be_3_numbers(cls, v):
        if (len(str(v)) != 3) & int(v) >= 0:
            raise ValidationError("CVV is invalid")
        return str(v)

    @property
    def brand(self) -> PaymentCardBrand:
        return self.credit_card_number.brand


class Debit(BaseModel):
    bank_name: constr(strip_whitespace=True, min_length=4) = Field(alias="name")
    bank_address: str
    as_of: datetime


class BankingService(BaseModel):
    bank_name: constr(strip_whitespace=True, min_length=4) = Field(alias="name")
    username: SecretStr
    password: SecretStr
    account_number: Optional[SecretStr]
    expiration_date: Optional[date]
    credit_card_number: Optional[PaymentCardNumber]
    contact: Dict[str, str] = None
    url: Optional[HttpUrl]
    debit_accounts: Optional[List[Debit]]
    credit_accounts: Optional[List[CreditCard]]
    security: Optional[List[Dict[str, SecretStr]]]

    @validator("security")
    def blah(cls, v):
        if {"question", "answer"} == v.keys():
            raise ValidationError("Security Question/Answer Conflict")
        else:
            return v

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


me = MyAccount(external_data)
print(dir(me))
