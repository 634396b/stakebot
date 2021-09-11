
from typing import Coroutine
from core.Bet import Bet
from core.Price import Price
from core.User import User
import log_fmt
import logging
import util
import sys
import constants
import asyncio
import json
import core.http.stake as stake_http
from exceptions import BetTooBigException, ZeroBalanceException

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

log.propagate = False

fhstate = logging.FileHandler('logs/bets/state.log')
fhe = logging.FileHandler('logs/bets/bets_errors.log')
fh = logging.FileHandler('logs/bets/bets.log')
fhd = logging.StreamHandler(sys.stdout)

fhe.setLevel(logging.ERROR)
fh.setLevel(logging.INFO)
fhd.setLevel(logging.DEBUG)
fhstate.setLevel(logging.DEBUG)

log.addHandler(fhe)
log.addHandler(fh)
log.addHandler(fhd)


def roundX(x, base=5):
    return base * round(x/base)


class BaseSlot:
    volitility = 0.5
    response_prop = ''

    def get_args(self):
        pass

    def get_volitility(self):
        return self.volitility

    def handle_response(self, r, r_p, **kwargs):
        util.check_response(r)
        r = json.loads(r)
        return util.slot_response(r, r_p)

    def bet_fn(self, *args, **kwargs) -> Coroutine:
        pass
    
    async def bet(self, user: User, price_mgr: Price, bet: float, currency: str):
        r_p = self.response_prop
        try:
            bet = roundX(bet, 1e-8)
            if not user.has_bal(currency, bet):
                raise ZeroBalanceException()

            bet_multi = -1
            bet_args = self.get_args()
            r = await self.bet_fn(key=user.key, bet=bet,
                                  currency=currency, **bet_args)

            pay_multi, data, payout, amount = self.handle_response(
                r, r_p, user=user)
            user.get_bal(currency).dec(bet)
            arr_logs, str_logs = log_fmt.fmt_spin(
                name=user.name,
                pay_multi=pay_multi,
                game=r_p,
                bet_multi=bet_multi,
                payout=payout,
                amount=amount,
                price=price_mgr.get_price(currency),
                bal=user.get_bal(currency).amt,
                **bet_args
            )
            self.check_win(user, str_logs, pay_multi,
                           bet_multi, payout, currency)
            return pay_multi, data
        except ZeroBalanceException as e:
            raise ZeroBalanceException(e)
        except BetTooBigException as e:
            raise BetTooBigException(e)
        except Exception as e:
            log.error(e, exc_info=1)
            raise Exception(e)

    def check_win(self, user: User, str_logs, pay_multi, bet_multi, payout, currency, should_depot=False):
        util.write_logs(user.name, str_logs)
        if pay_multi > constants.MIN_WIN_LOG:
            log.info(str_logs)
            if util.is_big_win(pay_multi=pay_multi, bet_multi=bet_multi):
                util.write_big_win_logs(str_logs)
                if should_depot:
                    vault_depot_amt = payout / 2
                    stake_http.create_vault_deposit(
                        key=user.key, amt=vault_depot_amt, currency=currency)
                    log.debug(
                        f'Depot {vault_depot_amt:.2e} in {currency}')
        return True
