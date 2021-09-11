from websockets import client
import random
import asyncio
import json
import time
import logging
import stake_keys
from datetime import datetime
from chat import ws_con_init, req_challenge
from core.Price import Price
import util
main_log = logging.getLogger(__name__ + '.main')
my_bets_log = logging.getLogger(__name__ + '.mybets')
big_wins_log = logging.getLogger(__name__ + '.bigwins')
error_log = logging.getLogger(__name__ + '.errors')
high_roller_log = logging.getLogger(__name__ + '.highroller')

big_wins_log.setLevel(logging.INFO)
my_bets_log.setLevel(logging.INFO)
main_log.setLevel(logging.INFO)
error_log.setLevel(logging.ERROR)
high_roller_log.setLevel(logging.INFO)

error_log.addHandler(logging.FileHandler('logs/all_bets/bets_errors.log'))
main_log.addHandler(logging.FileHandler('logs/all_bets/all.log'))
big_wins_log.addHandler(logging.FileHandler('logs/all_bets/big_wins.log'))
my_bets_log.addHandler(logging.FileHandler('logs/all_bets/my_bets.log'))
high_roller_log.addHandler(logging.FileHandler(
    'logs/all_bets/high_rollers.log'))


def ws_subscribe_my_bets(key, id):
    data = {
        "id": id,
        "type": "start",
        "payload": {

            "variables": {},
            "extensions": {},
            "operationName": "houseBets",
            "query": "subscription houseBets {\n  houseBets {\n    ...BetFragment\n    __typename\n  }\n}\n\nfragment BetFragment on Bet {\n  id\n  iid\n  type\n  scope\n  game {\n    name\n    icon\n    __typename\n  }\n  bet {\n    ... on CasinoBet {\n      ...CasinoBetFragment\n      __typename\n    }\n    ... on MultiplayerCrashBet {\n      ...MultiplayerCrashBet\n      __typename\n    }\n    ... on MultiplayerSlideBet {\n      ...MultiplayerSlideBet\n      __typename\n    }\n    ... on SoftswissBet {\n      ...SoftswissBet\n      __typename\n    }\n    ... on SportBet {\n      ...SportBet\n      __typename\n    }\n    ... on EvolutionBet {\n      ...EvolutionBet\n      __typename\n    }\n    ... on PlayerPropBet {\n      ...PlayerPropBetFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment MultiplayerCrashBet on MultiplayerCrashBet {\n  id\n  user {\n    id\n    name\n    __typename\n  }\n  payoutMultiplier\n  gameId\n  amount\n  payout\n  currency\n  result\n  updatedAt\n  cashoutAt\n  btcAmount: amount(currency: btc)\n  __typename\n}\n\nfragment MultiplayerSlideBet on MultiplayerSlideBet {\n  id\n  user {\n    id\n    name\n    __typename\n  }\n  payoutMultiplier\n  gameId\n  amount\n  payout\n  currency\n  slideResult: result\n  updatedAt\n  cashoutAt\n  btcAmount: amount(currency: btc)\n  active\n  createdAt\n  __typename\n}\n\nfragment SoftswissBet on SoftswissBet {\n  id\n  amount\n  currency\n  updatedAt\n  payout\n  payoutMultiplier\n  user {\n    id\n    name\n    __typename\n  }\n  softswissGame: game {\n    id\n    name\n    edge\n    extId\n    provider {\n      id\n      name\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SportBet on SportBet {\n  id\n  amount\n  active\n  currency\n  status\n  payoutMultiplier\n  potentialMultiplier\n  cashoutMultiplier\n  payout\n  createdAt\n  user {\n    id\n    name\n    __typename\n  }\n  outcomes {\n    odds\n    status\n    outcome {\n      id\n      name\n      active\n      odds\n      __typename\n    }\n    market {\n      ...MarketFragment\n      fixture {\n        id\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    fixture {\n      ...FixturePreviewFragment\n      __typename\n    }\n    __typename\n  }\n  adjustments {\n    id\n    payoutMultiplier\n    updatedAt\n    createdAt\n    __typename\n  }\n  __typename\n}\n\nfragment MarketFragment on SportMarket {\n  id\n  name\n  status\n  extId\n  specifiers\n  outcomes {\n    id\n    active\n    name\n    odds\n    __typename\n  }\n  __typename\n}\n\nfragment FixturePreviewFragment on SportFixture {\n  id\n  extId\n  status\n  slug\n  marketCount(status: [active, suspended])\n  data {\n    ...FixtureDataMatchFragment\n    ...FixtureDataOutrightFragment\n    __typename\n  }\n  eventStatus {\n    ...FixtureEventStatus\n    __typename\n  }\n  tournament {\n    ...TournamentTreeFragment\n    __typename\n  }\n  ...LiveStreamExistsFragment\n  __typename\n}\n\nfragment FixtureDataMatchFragment on SportFixtureDataMatch {\n  startTime\n  competitors {\n    ...CompetitorFragment\n    __typename\n  }\n  __typename\n}\n\nfragment CompetitorFragment on SportFixtureCompetitor {\n  name\n  extId\n  countryCode\n  abbreviation\n  __typename\n}\n\nfragment FixtureDataOutrightFragment on SportFixtureDataOutright {\n  name\n  startTime\n  endTime\n  __typename\n}\n\nfragment FixtureEventStatus on SportFixtureEventStatus {\n  homeScore\n  awayScore\n  matchStatus\n  clock {\n    matchTime\n    remainingTime\n    __typename\n  }\n  periodScores {\n    homeScore\n    awayScore\n    matchStatus\n    __typename\n  }\n  currentServer {\n    extId\n    __typename\n  }\n  homeGameScore\n  awayGameScore\n  statistic {\n    yellowCards {\n      away\n      home\n      __typename\n    }\n    redCards {\n      away\n      home\n      __typename\n    }\n    corners {\n      home\n      away\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment TournamentTreeFragment on SportTournament {\n  id\n  name\n  slug\n  category {\n    id\n    name\n    slug\n    sport {\n      id\n      name\n      slug\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment LiveStreamExistsFragment on SportFixture {\n  abiosStream {\n    exists\n    __typename\n  }\n  betradarStream {\n    exists\n    __typename\n  }\n  diceStream {\n    exists\n    __typename\n  }\n  __typename\n}\n\nfragment EvolutionBet on EvolutionBet {\n  id\n  amount\n  currency\n  createdAt\n  payout\n  payoutMultiplier\n  user {\n    id\n    name\n    __typename\n  }\n  softswissGame: game {\n    id\n    name\n    edge\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropBetFragment on PlayerPropBet {\n  active\n  amount\n  cashoutMultiplier\n  createdAt\n  currency\n  id\n  playerProps {\n    id\n    lineType\n    playerProp {\n      ...PlayerPropLineFragment\n      __typename\n    }\n    __typename\n  }\n  odds\n  payout\n  payoutMultiplier\n  updatedAt\n  status\n  user {\n    id\n    name\n    __typename\n  }\n  playerProps {\n    id\n    lineType\n    playerProp {\n      ...PlayerPropLineFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropLineFragment on PlayerPropLine {\n  id\n  line\n  over\n  under\n  suspended\n  balanced\n  name\n  player {\n    id\n    name\n    __typename\n  }\n  market {\n    id\n    stat {\n      name\n      value\n      __typename\n    }\n    game {\n      id\n      fixture {\n        id\n        name\n        data {\n          ... on SportFixtureDataMatch {\n            competitors {\n              ...CompetitorFragment\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              name\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n",            "accessToken": key,
            "language": "en"
        }
    }
    return data


def ws_subscribe_all_house_bets(key, id):
    data = {
        "id": id,
        "type": "start",
        "payload": {
                "variables": {},
                "extensions": {},
                "operationName": "AllHouseBetsSubscription",
                'query': "subscription AllHouseBetsSubscription {\n  allHouseBets {\n    iid\n    ...BetFragment\n    __typename\n  }\n}\n\nfragment BetFragment on Bet {\n  id\n  iid\n  type\n  scope\n  game {\n    name\n    icon\n    __typename\n  }\n  bet {\n    ... on CasinoBet {\n      ...CasinoBetFragment\n      __typename\n    }\n    ... on MultiplayerCrashBet {\n      ...MultiplayerCrashBet\n      __typename\n    }\n    ... on MultiplayerSlideBet {\n      ...MultiplayerSlideBet\n      __typename\n    }\n    ... on SoftswissBet {\n      ...SoftswissBet\n      __typename\n    }\n    ... on SportBet {\n      ...SportBet\n      __typename\n    }\n    ... on EvolutionBet {\n      ...EvolutionBet\n      __typename\n    }\n    ... on PlayerPropBet {\n      ...PlayerPropBetFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment MultiplayerCrashBet on MultiplayerCrashBet {\n  id\n  user {\n    id\n    name\n    __typename\n  }\n  payoutMultiplier\n  gameId\n  amount\n  payout\n  currency\n  result\n  updatedAt\n  cashoutAt\n  btcAmount: amount(currency: btc)\n  __typename\n}\n\nfragment MultiplayerSlideBet on MultiplayerSlideBet {\n  id\n  user {\n    id\n    name\n    __typename\n  }\n  payoutMultiplier\n  gameId\n  amount\n  payout\n  currency\n  slideResult: result\n  updatedAt\n  cashoutAt\n  btcAmount: amount(currency: btc)\n  active\n  createdAt\n  __typename\n}\n\nfragment SoftswissBet on SoftswissBet {\n  id\n  amount\n  currency\n  updatedAt\n  payout\n  payoutMultiplier\n  user {\n    id\n    name\n    __typename\n  }\n  softswissGame: game {\n    id\n    name\n    edge\n    extId\n    provider {\n      id\n      name\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SportBet on SportBet {\n  id\n  amount\n  active\n  currency\n  status\n  payoutMultiplier\n  potentialMultiplier\n  cashoutMultiplier\n  payout\n  createdAt\n  user {\n    id\n    name\n    __typename\n  }\n  outcomes {\n    odds\n    status\n    outcome {\n      id\n      name\n      active\n      odds\n      __typename\n    }\n    market {\n      ...MarketFragment\n      fixture {\n        id\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    fixture {\n      ...FixturePreviewFragment\n      __typename\n    }\n    __typename\n  }\n  adjustments {\n    id\n    payoutMultiplier\n    updatedAt\n    createdAt\n    __typename\n  }\n  __typename\n}\n\nfragment MarketFragment on SportMarket {\n  id\n  name\n  status\n  extId\n  specifiers\n  outcomes {\n    id\n    active\n    name\n    odds\n    __typename\n  }\n  __typename\n}\n\nfragment FixturePreviewFragment on SportFixture {\n  id\n  extId\n  status\n  slug\n  marketCount(status: [active, suspended])\n  data {\n    ...FixtureDataMatchFragment\n    ...FixtureDataOutrightFragment\n    __typename\n  }\n  eventStatus {\n    ...FixtureEventStatus\n    __typename\n  }\n  tournament {\n    ...TournamentTreeFragment\n    __typename\n  }\n  ...LiveStreamExistsFragment\n  __typename\n}\n\nfragment FixtureDataMatchFragment on SportFixtureDataMatch {\n  startTime\n  competitors {\n    ...CompetitorFragment\n    __typename\n  }\n  __typename\n}\n\nfragment CompetitorFragment on SportFixtureCompetitor {\n  name\n  extId\n  countryCode\n  abbreviation\n  __typename\n}\n\nfragment FixtureDataOutrightFragment on SportFixtureDataOutright {\n  name\n  startTime\n  endTime\n  __typename\n}\n\nfragment FixtureEventStatus on SportFixtureEventStatus {\n  homeScore\n  awayScore\n  matchStatus\n  clock {\n    matchTime\n    remainingTime\n    __typename\n  }\n  periodScores {\n    homeScore\n    awayScore\n    matchStatus\n    __typename\n  }\n  currentServer {\n    extId\n    __typename\n  }\n  homeGameScore\n  awayGameScore\n  statistic {\n    yellowCards {\n      away\n      home\n      __typename\n    }\n    redCards {\n      away\n      home\n      __typename\n    }\n    corners {\n      home\n      away\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment TournamentTreeFragment on SportTournament {\n  id\n  name\n  slug\n  category {\n    id\n    name\n    slug\n    sport {\n      id\n      name\n      slug\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment LiveStreamExistsFragment on SportFixture {\n  abiosStream {\n    exists\n    __typename\n  }\n  betradarStream {\n    exists\n    __typename\n  }\n  diceStream {\n    exists\n    __typename\n  }\n  __typename\n}\n\nfragment EvolutionBet on EvolutionBet {\n  id\n  amount\n  currency\n  createdAt\n  payout\n  payoutMultiplier\n  user {\n    id\n    name\n    __typename\n  }\n  softswissGame: game {\n    id\n    name\n    edge\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropBetFragment on PlayerPropBet {\n  active\n  amount\n  cashoutMultiplier\n  createdAt\n  currency\n  id\n  playerProps {\n    id\n    lineType\n    playerProp {\n      ...PlayerPropLineFragment\n      __typename\n    }\n    __typename\n  }\n  odds\n  payout\n  payoutMultiplier\n  updatedAt\n  status\n  user {\n    id\n    name\n    __typename\n  }\n  playerProps {\n    id\n    lineType\n    playerProp {\n      ...PlayerPropLineFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropLineFragment on PlayerPropLine {\n  id\n  line\n  over\n  under\n  suspended\n  balanced\n  name\n  player {\n    id\n    name\n    __typename\n  }\n  market {\n    id\n    stat {\n      name\n      value\n      __typename\n    }\n    game {\n      id\n      fixture {\n        id\n        name\n        data {\n          ... on SportFixtureDataMatch {\n            competitors {\n              ...CompetitorFragment\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              name\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n",
                "accessToken": key,
                "language": "en"
        }
    }
    return data


price_mgr = Price()


async def send_ack(ws, type):
    await ws.send(json.dumps({'type': type}))
    return True


async def receive_data_loop(ws, key):
    while True:
        try:
            if ws == None or ws.closed:
                break
            r = await ws.recv()
            r = json.loads(r)
            if r['type'] == 'ka':
                # await send_ack(ws, 'ka')
                continue
            if r['type'] == 'connection_ack':
                await send_ack(ws, 'connection_ack')
                continue
            data = r['payload']['data']
            all_bets = data['allHouseBets'] if 'allHouseBets' in data else data['houseBets']
            bet = all_bets['bet']
            iid = all_bets['iid']
            game_name = all_bets['game']['name']
            pay_multi = bet['payoutMultiplier']
            amount = bet['amount']
            amount_multi = bet['amountMultiplier'] if 'amountMultiplier' in bet else 1
            payout = bet['payout']
            currency = bet['currency']
            updated_at = bet['updatedAt'] if 'updatedAt' in bet else None
            user_id = bet['user']['id'] if bet['user'] is not None else None
            user_name = bet['user']['name'] if bet['user'] is not None else None
            price = price_mgr.get_price(currency=currency)
            pay_in_usd = price*payout
            bet_in_usd = amount * amount_multi * price
            log = ' '.join([util.cur_date(), iid, game_name.replace(' ', '_').ljust(50), f'{pay_multi:.2f}x'.rjust(20), f'{amount:.5f}'.rjust(
                20), f'{currency}'.ljust(10), f'${bet_in_usd:.4f}'.ljust(15), f'${pay_in_usd:.4f}'.ljust(15), str(user_name).rjust(20)])
            if user_name and user_name.lower() == 'wiggle':
                my_bets_log.info(log)
            main_log.info(log)
            if pay_multi >= 100:
                big_wins_log.info(log)
            if bet_in_usd >= 95:
                high_roller_log.info(log)
        except Exception as e:
            error_log.error(e, exc_info=1)
        finally:
            await asyncio.sleep(0.01)


async def connect(key):
    try:
        await asyncio.sleep(random.randint(1, 2))
        id = 1
        headers = {
            "accept-language": "en-US,en;q=0.9,pt;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
        }
        ws: client.WebSocketClientProtocol = await asyncio.wait_for(client.connect(uri='wss://api.stake.com/subscriptions', subprotocols=['graphql-ws'], extra_headers=headers, origin='https://stake.com'), 30)
        if not ws:
            return None
        data = ws_con_init(key=key, challenge=None,
                           challenge_key=None)
        await ws.send(json.dumps(data))
        await ws.recv()
        data = ws_subscribe_all_house_bets(key=key, id=id)
        await ws.send(json.dumps(data))
        id += 1
        data = ws_subscribe_my_bets(key=key, id=id)
        await ws.send(json.dumps(data))
        asyncio.ensure_future(receive_data_loop(
            ws, key))
        return ws
    except Exception as e:
        error_log.error(e, exc_info=1)
    return None

async def update_price():
    while True:
        try:
            await asyncio.sleep(60)
            await price_mgr.update_price()
        except:
            pass
        
async def main(key, idx):
    while True:
        try:
            await asyncio.sleep(1)
            ws = await asyncio.wait_for(connect(key=key), 30)
            if ws:
                await ws.wait_closed()
        except Exception as e:
            error_log.error(e, exc_info=1)
        finally:
            await asyncio.sleep(1)

if __name__ == '__main__':
    time.sleep(1)
    lm_dt = datetime.now()
    keys = stake_keys.load_keys('data/api_keys_twitter.txt')
    for idx, key in enumerate(keys):
        asyncio.get_event_loop().create_task(main(key, idx))
    asyncio.get_event_loop().create_task(update_price())
    asyncio.get_event_loop().run_forever()
