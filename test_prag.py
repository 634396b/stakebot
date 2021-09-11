from core.Cryptocurrency import Cryptocurrency as Crypto
from exceptions import InBonusException, NoMoneyException, OutOfBoundsLinesException, UnhandledException
from main import Bot
from providers import PragmaticSlots
from providers.PragmaticSlots import BuffaloKing, ExtraJuicy, FloatingDragon, FruitParty, FruitPartyTwo, GatesofOlympus, GemsBonanza, GoldRush, GoldTrain, Hottoburn, JuicyFruits, LuckyGraceandCharm, MadameDestinyMegaways, MasterJoker, PandaFortuneTwo, StarBounty, SuperSevens, SweetBonanza, TheDogHouse, TheDogHouseMegaways, TheHandofMidas, WolfGold
from providers.PragmaticPlay import PragmaticPlay
from typing import List
from traceback import print_exc
import stake_keys
import random
import asyncio
import sys
import inspect


async def do_bets(slot: PragmaticPlay, should_stop_no_bal=False):
    await asyncio.sleep(5)
    try:
        await slot.start_new_session()
    except InBonusException as e:
        print(e)
        with open('done.txt', 'a') as f:
            f.write(slot.get_id() + '\n')
        return slot
    except OutOfBoundsLinesException as e:
        with open('slot_meta.txt', 'a') as f:
            f.write(e.args[0] + ';' + str(e.args[2]) + '\n')
        print(e.args)
        return slot
    while True:
        await asyncio.sleep(random.randint(1,10))
        try:
            await slot.do_bet(credit_override=None)
        except InBonusException as e:
            print(e)
            with open('done.txt', 'a') as f:
                f.write(slot.get_id() + '\n')
            return slot
        except NoMoneyException as e:
            if should_stop_no_bal:
                return 'STOP'
            # Block until we have enough balance
            print(slot.get_id(), 'Blocking until balance')
            while (await slot.reload_balance()) < slot.get_bet(slot.credit):
                await asyncio.sleep(random.randint(30, 60))
        except UnhandledException as e:
            print(e)
            return slot
            # sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)
        finally:
            await asyncio.sleep(1)


async def main(slots: List[PragmaticPlay]):
    random.shuffle(slots)
    futures: List[asyncio.Future] = []
    in_progress = []
    slots_meta = [meta.split(';')
                  for meta in stake_keys.load_keys('slot_meta.txt')]
    while True:
        if len(slots) == 0:
            raise Exception('All bonuses opened')
        slot = random.choice(slots)
        meta = None
        for m in slots_meta:
            meta = m if m[0] == slot.slug else meta
        if meta is not None:
            if slot.max_lines is not None and int(meta[1]) > slot.max_lines:
                continue
            elif slot.min_lines is not None and int(meta[1]) < slot.min_lines:
                continue
        await asyncio.sleep(random.randint(1, 5))
        done = stake_keys.load_keys('done.txt')
        if not slot.get_id() in done and slot.get_id() not in in_progress:
            print('Total Bonuses', len(done))
            in_progress.append(slot.get_id())
            futures.append(asyncio.ensure_future(
                do_bets(slot=slot, should_stop_no_bal=False)))
        while True:
            for future in futures:
                if future.done():
                    try:
                        slot: PragmaticPlay = future.result()
                        if slot == 'STOP':
                            pass
                        elif issubclass(type(slot), PragmaticPlay):
                            in_progress.remove(slot.get_id())
                        else:
                            print('unhandled future end')
                            sys.exit(1)
                    except:
                        # Something went HORRIBLY wrong, please consider critical handling here
                        print_exc()
                    finally:
                        futures.remove(future)
                        break
            if len(futures) < 10:
                break
            await asyncio.sleep(1)
if __name__ == '__main__':
    def get_all_slots(Module):
        return [getattr(Module, m[0])
                for m in inspect.getmembers(Module, inspect.isclass)
                if m[1].__module__ == Module.__name__]

    def all_crypto():
        return [getattr(Crypto(), a) for a in dir(Crypto())
                if
                not a.startswith('__') and not callable(getattr(Crypto(), a))
                ]

    bot = Bot(key_path='data/api_keys_bet.txt')
    PragmaticPlay.min_lines = 10
    PragmaticPlay.max_lines = None
    filter_crypto = [Crypto.LTC]
    filter_slots = [
        # GatesofOlympus, 
        # JuicyFruits,
        # SweetBonanza, 
        # FruitParty,
        #  FruitPartyTwo,
        # FloatingDragon, TheDogHouse, GemsBonanza,
        # StarBounty, 
        # ExtraJuicy,
        # MasterJoker,
        # Hottoburn,
        # SuperSevens
        # GoldTrain,
        # LuckyGraceandCharm,
        # FloatingDragon,
        # PandaFortuneTwo
    ]
    bet_inc = {
        # GatesofOlympus: 0.05,
        # PandaFortuneTwo: 0.02,
        # FruitPartyTwo: 0.03,
        # FruitParty: 0.05,
        # ExtraJuicy: 0.03,
        # MasterJoker: 0.01,
        # SuperSevens: 0.01,
        # Hottoburn: 0.01,
    }
    all_cryptos = all_crypto()
    all_slots = get_all_slots(PragmaticSlots)

    if len(filter_crypto) > 0:
        all_cryptos = filter(lambda c: c in filter_crypto, all_cryptos)

    if len(filter_slots) > 0:
        all_slots = filter(lambda c: c in filter_slots, all_slots)

    slots_and_crypto = [m(currency=crypto, key=user.key, stop_if_bonus=True, credit=bet_inc[m] if m in bet_inc else 0.01)
                            for crypto in all_cryptos
                            for m in all_slots
                            for user in bot.users]
    slots = slots_and_crypto
    print([slot.slug for slot in slots])
    asyncio.get_event_loop().create_task(main(slots))
    asyncio.get_event_loop().run_forever()
