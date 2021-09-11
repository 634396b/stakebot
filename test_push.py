from providers.PushGaming import JamminJars2, JamminJars, MountMagmas, MysteryMuseum
from main import Bot
import time
import asyncio
import balances
from core.User import User
import random


def get_scaled_bet(bet, giga_jar_level, giga_jar_collected, i):
    if giga_jar_level == 5:
        if giga_jar_collected < 40:
            bet = 100
        else:
            bet = bet
    elif giga_jar_level == -1:
        bet = 100
    else:
        bet = 20
    return bet


if __name__ == '__main__':
    bot = Bot('data/api_keys_bet.txt')

    async def do_bets(user, delay):
        slots = [MysteryMuseum, MountMagmas]
        last_slot = None
        while True:
            try:
                await asyncio.sleep(1)
                rdm_slot = None
                while last_slot == rdm_slot:
                    rdm_slot = random.choice(slots)
                await start_and_bet(user=user, delay=delay, slot=random.choice(slots))
                await asyncio.sleep(1)
            except Exception as e:
                print(e)

    async def start_and_bet(user: User, delay, slot):
        await balances.update_user(user, price_mgr=None)
        cur = 'btc'  # bot.get_first_non_zero_currency(user, min_bal=0.2)
        if cur == None:
            raise Exception('No currency')
        pg = slot(currency=cur, key=user.key)
        await pg.start_new_session()
        bet = 200
        i = 0
        while True:
            await asyncio.sleep(delay/2)
            await pg.do_bet(bet)
            if i % 10 == 0 and i > 0:
                return True
            i += 1
            await asyncio.sleep(delay/2)
    asyncio.get_event_loop().create_task(bot.do_price_update())
    time.sleep(5)
    for user in bot.users:
        asyncio.get_event_loop().create_task(do_bets(user=user, delay=0))
    asyncio.get_event_loop().run_forever()
