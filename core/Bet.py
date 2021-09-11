from core.Price import Price
from core.User import User
from random import randint
from constants import MAX_BET_USD, SMALLEST_BET
from exceptions import BetTooBigException
import random


class Bet:
    min_bet_div = 10
    max_bet_div = 100
    luck_bet_usd = 0.01
    luck_bet_min = 1
    luck_bet_max = 100

    def create_bet(self, user: User, price: float, currency: str):
        bet_div = self.rand_bet_div(self.min_bet_div, self.max_bet_div, 0) / 10

        bet = bet_div/price#user.get_bal(currency).amt/bet_div
        if randint(self.luck_bet_min, self.luck_bet_max) == self.luck_bet_min:
            bet = self.luck_bet_usd/price

        if not self.is_gt_min_bet(bet=bet):
            bet = SMALLEST_BET
        if bet < 0.0002/price:
            bet = 0.0002/price
        if bet * price > MAX_BET_USD:
            bet = MAX_BET_USD/price
        bet_div = user.get_bal(currency).amt/bet
        self.check_bet_bal(bal=user.get_bal(currency).amt, bet=bet)

        return {'bet': bet, 'bet_multi': bet_div}

    def rand_bet_div(self, min_bet, max_bet, bal):
        bet_div = randint(min_bet, max_bet)
        bet_div += bal * bet_div if bal >= 1 else (1 + bal) * bet_div
        bet_div = max(bet_div, min_bet)
        bet_div = min(bet_div, max_bet)
        return bet_div

    def is_gt_min_bet(self, bet: float):
        return bet >= SMALLEST_BET

    def check_bet_bal(self, bal, bet):
        if bet > bal:
            raise BetTooBigException(bal, bet)

    def __str__(self) -> str:
        return f'\t|\t{self.min_bet_div}\t{self.max_bet_div}\t{self.luck_bet_max}\t{self.luck_bet_min}\t{self.luck_bet_usd}\t|\t'