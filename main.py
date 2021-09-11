from core.stakeoriginals.LimboSlot import LimboSlot
from core.stakeoriginals.ScarabSlot import ScarabSlot
from core.stakeoriginals.SamSlot import SamSlot
from core.stakeoriginals.DiceSlot import DiceSlot
from core.stakeoriginals.DiamondSlot import DiamondSlot
from core.stakeoriginals.KenoSlot import KenoSlot
from core.stakeoriginals.PlinkoSlot import PlinkoSlot
from core.Price import Price
from core.Bet import Bet
from core.User import User

import typing
import random
import stake_keys
import logging
import time
import balances
import asyncio
import sys
import secrets

from exceptions import ZeroBalanceException
from datetime import datetime


state_log = logging.getLogger(__name__ + '-state')
log = logging.getLogger(__name__ + '-main')
log.setLevel(logging.DEBUG)
state_log.setLevel(logging.DEBUG)

log.propagate = False
state_log.propagate = False

fhstate = logging.FileHandler('logs/bets/state.log')
fhe = logging.FileHandler('logs/bets/main_errors.log')
fh = logging.FileHandler('logs/bets/main.log')
fhd = logging.StreamHandler(sys.stdout)

fhe.setLevel(logging.ERROR)
fh.setLevel(logging.DEBUG)
fhd.setLevel(logging.DEBUG)
fhstate.setLevel(logging.DEBUG)

log.addHandler(fhe)
log.addHandler(fh)
log.addHandler(fhd)
state_log.addHandler(fhstate)


class Bot:
    bet_mgr = Bet()
    price_mgr = Price()
    big_wins = 0
    counter = 0
    total_bet_multi = 1000

    def __init__(self, key_path='data/api_keys_bet.txt'):
        self.key_path = key_path
        self.keys = stake_keys.load_keys(key_path)
        self.users = [User(key=key) for key in self.keys]

    # TODO
    # * Global socket
    #   - Chat manager
    #   - House bets
    #   - Notifications

    def get_first_non_zero_currency(self, user: User, min_bal=0.001):
        for bal in random.choices(user.balances, k=len(user.balances) - 1):
            if bal.amt*self.price_mgr.get_price(bal.currency) > min_bal:
                return bal.currency
        return None

    async def do_bets(self, user: User):
        await asyncio.sleep(len(self.users) + 1)
        fns = [
            # PlinkoSlot(),
            # KenoSlot(),
            SamSlot(),
            # ScarabSlot(),
            # LimboSlot()
            # DiamondSlot(),
            # DiceSlot(),
        ]
        currency = 'ltc'
        bet_queue = random.choices([{'user': secrets.token_hex(
            5), 'bet_amt': 0, 'fn': fn} for fn in fns], k=1)
        delay = 1*1  # ms
        dt_last_loop = datetime.now()
        while True:
            try:
                # currency = self.get_first_non_zero_currency(user)
                if len(bet_queue) == 0 or currency == None:
                    await asyncio.sleep(1)
                    continue
                diff_in_seconds = (dt_last_loop - datetime.now()).seconds
                if diff_in_seconds/1000 < delay:
                    await asyncio.sleep(delay/1000)
                else:
                    dt_last_loop = datetime.now()

                user_bal = user.get_bal(currency)
                price = self.price_mgr.get_price(currency=currency)
                if user_bal == 0.0:
                    continue
                if price == 0.0:
                    continue

                # Debug state
                if random.randint(1, 1000) == 1:
                    state_log.debug((
                                    f'{self.bet_mgr}\t'
                                    f'{self.price_mgr}\t'
                                    f'{self.users}'
                                    f'{self.total_bet_multi}\t'
                                    ))

                for fn in fns:
                    b = {'bet': 0.05/price}
                    if b['bet'] >= 0.01:
                        raise Exception('BET TOO BIG?')
                    pay_multi, _ = await fn.bet(user=user, price_mgr=self.price_mgr,
                                                bet=b['bet'], currency=currency)
                    if pay_multi >= 100:
                        self.counter = 0
                        self.big_wins += 1
                if self.counter < 1000:
                    self.counter = self.counter + 1
                else:
                    self.counter = 0
                    self.big_wins = 0
            except ZeroBalanceException as e:
                log.debug('\t'.join([
                    f'Sleeping because blanace is too low'.ljust(20),
                    f'{e}'.center(35)
                ])
                )
                await asyncio.sleep(5)
            except Exception as e:
                log.error(e, exc_info=1)
                await asyncio.sleep(1)
            finally:
                random.shuffle(fns)
                dt_last_loop = datetime.now()

    async def test(self, slot, user, cur, bet):
        try:
            pay_multi2, data2 = await slot.bet(bet=bet, currency=cur, user=user, price_mgr=self.price_mgr)
            for i, bal in enumerate(user.balances):
                if bal.currency == cur:
                    user.balances[i].amt += float(pay_multi2) * bet
        except Exception as e:
            await asyncio.sleep(1)
            log.error(e, exc_info=1)

    async def grind_vip(self, user: User, bet_usd):
        plinko_slot = PlinkoSlot(rows=9, risk='low')
        init_user_bal = {}
        user_bal_timer: typing.Dict[str, datetime] = {}
        i = 0
        while True:
            try:
                # self.get_first_non_zero_currency(user, min_bal=bet_usd * 1.03)
                cur = 'btc'
                if cur is None:
                    continue
                await asyncio.sleep(1/1000)
                user_bal = user.get_bal(cur).amt
                price = self.price_mgr.get_price(currency=cur)
                bet = bet_usd/price
                await self.test(slot=plinko_slot, user=user, cur=cur, bet=bet)
                # if cur not in init_user_bal:
                #     init_user_bal[cur] = user_bal
                #     user_bal_timer[cur] = datetime.now()

                # if user_bal < init_user_bal[cur]:
                #     bet = (bet_usd * 2) / price if i % 4 == 0 or random.randint(1,20) == 1 else bet_usd / price
                #     if (datetime.now() - user_bal_timer[cur]).seconds >= 300:
                #         user_bal_timer[cur] = datetime.now()
                #         init_user_bal[cur] = user_bal
                # else:
                #     bet = 0.5 * bet_usd/price
                #     user_bal_timer[cur] = datetime.now()

            except Exception as e:
                log.error(e, exc_info=1)
                await asyncio.sleep(5)
            finally:
                i += 1

    async def do_price_update(self):
        await asyncio.sleep(0.5)
        while True:
            try:
                await self.price_mgr.update_price()
            except Exception as e:
                log.error(e, exc_info=1)
            finally:
                await asyncio.sleep(60)

    async def do_update_user(self, user: User):
        await asyncio.sleep(0.5)
        while True:
            try:
                await balances.update_user(
                    user=user, price_mgr=self.price_mgr, should_print=True)
            except Exception as e:
                log.error(e, exc_info=1)
                await asyncio.sleep(40)
            finally:
                await asyncio.sleep(60)

    def run_update(self):
        asyncio.get_event_loop().create_task(self.do_price_update())
        for user in self.users:
            asyncio.get_event_loop().create_task(self.do_update_user(user))

    def run(self, do_bet=False):
        self.run_update()
        for user in self.users:
            if do_bet:
                asyncio.get_event_loop().create_task(self.do_bets(user))
            else:
                asyncio.get_event_loop().create_task(self.grind_vip(user=user, bet_usd=0.01))
        asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    time.sleep(1)
    bot = Bot()
    if len(sys.argv) == 2 and sys.argv[1] == 'bet':
        bot.run(do_bet=1)
    else:
        bot.run()
