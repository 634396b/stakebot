import asyncio
from providers.PlayNGo import PlayNGo
from providers.PlayNGoSlots import RagingRex, ThreeClownMonty, RiseofMerlin, TheGreenKnight, LegacyofDead, AnkhofAnubis
from main import Bot
import random

async def main(slot: PlayNGo):
    await asyncio.sleep(5)
    slot.start_new_session()
    while True:
        slot.denom = 4 if random.randint(1,5) == 1 else 2
        await asyncio.sleep(random.randint(0, 1))
        slot.do_spin()

bot = Bot()
user = bot.users[0]

slots = [
    # ThreeClownMonty,
    RagingRex,
    # RiseofMerlin,
    # TheGreenKnight,
    # AnkhofAnubis,
    # LegacyofDead
]

slots = [slot(currency='btc', key=user.key) for slot in slots]

for slot in slots:
    asyncio.get_event_loop().create_task(main(slot))
asyncio.get_event_loop().run_forever()
# d=1 10 1 1 8 5 7 6 4 5 3 8 8 8 5 7 2 6 2 7 0 3 1 4 6 4 30 3 6 0 3 7 8 9 13 5 3 24 8 7 0 1 5 7 8 9 10 4 3 9 3 5 0 4 7 8 9 3 3 6 3 5 0 6 7 8 9
# 2 0 3 8 4 0
# 2 2 10 4 0 7 8 9
# 2 5 1

# d=1 10 1 1 2 8 2 4 1 2 3 2 0 9 0 2 4 2 4 8 0 4 1 1 2 5 36 6 8 0 1 2 5 7 11 13 15
# 2 0 3 8 2 0
# 2 2 10 2 1 15
# 2 5 1

# d=1 10 1 1 6 8 1 8 2 0 3 5 3 5 4 1 5 0 1 3 0 3 1 3 5 4 12 2 5 1 3 7 9 12 3 3 4 2 4 1 3 6 8 4 3 3 1 3 1 3 10
# 2 0 3 8 2 0
# 2 2 10 2 1 3
# 2 5 1

# the 8 (2038) probably means mini feature
# d=1 10 1 1 4 7 9 1 3 1 2 3 5 3 8 8 3 1 9 6 2 9 2 0
# 2 0 3 8 2 0
# 2 2 10 2 10 11
# 2 5 1
# d=1 10 1 1 6 7 9 8 8 2 0 8 8 8 8 6 1 2 5 9 3 0 1 2 6 4 80 8 8 0 3 4 7 8 9 10 11 7 3 80 8 7 1 3 4 7 8 9 10
# 2 0 3 8 6 0
# 2 2 10 6 3 4 7 8 9 10
# 2 5 1

# the 9 probably means bonus free spins and the number after it is count maybe
# d=2 6
# 2 0 0 9 3 0
# 2 2 1 10
# 2 5 1
# d=2 6
# 3 0 0 0 10 1
# 1 10 1 1 1 0 3 2 1 5 3 9 1 7 2 7 5 2 3 1 3 2 1 1 1 3 1 1 3 0 4 8
# 2 0 2 2 2 0
# 2 2 8 2
# 2 5 1


# Merlin
# d=1 1 10 1 1 9 3 3 9 4 1 2 9 5 4 3 2 6 4 1 3 0 9 2 2 10 3 1 3 2 5 6 4 3 2 5 4 2 0 5 7 1 0 8 8 0
# 2 0 0 9 3 0
# 2 2 0 20
# 2 2 1 8
# 2 2 6 2
# 2 5 1
