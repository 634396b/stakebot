from core.Price import currencies
from constants import SMALLEST_BET


class Balance:
    amt = 0
    currency = ''
    vault_amt = 0
    vault_cur = ''

    def __init__(self, currency):
        self.currency = currency

    def __str__(self):
        return ''.join([f'{self.amt:.8f}'.center(10), f'{self.currency}'.center(10), f'{self.vault_amt:.8f}'])

    def __call__(self):
        return self.amt

    def dec(self, amt):
        self.amt -= amt

    def usd(self, price):
        return self.amt * price

    def set_bal(self, vault_balance, available_balance):
        self.vault_amt = vault_balance
        self.amt = available_balance


class User:
    key = ''
    name = ''

    def __init__(self, key: str):
        self.key = key
        self.balances = [Balance(cur) for cur in currencies]

    def get_bal(self, currency):
        for bal in self.balances:
            if bal.currency == currency:
                return bal
        return None

    def __str__(self):
        b = []
        for bal in self.balances:
            if bal.amt > 0 or bal.vault_amt > 0:
                b.append(str(bal))
        return '\n'.join([f'\n{self.key[:8]} - {self.name}', '\n'.join(b)])

    def __repr__(self):
        return self.__str__()

    def has_bal(self, cur, amt = SMALLEST_BET):
        return self.get_bal(cur).amt >= amt
