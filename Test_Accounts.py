from pydantic import ValidationError
from Accounts import BankingService
from mock_account import external_data


def test_BankingService_schema():
    try:
        BankingService(**external_data)
    except ValidationError as e:
        print(e.json())
