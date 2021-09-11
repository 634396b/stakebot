import stake_keys
import core.http.stake as stake_http 
import logging
import util
import asyncio
import json
import random
from websockets import client, exceptions
import logging
import re
from datetime import datetime, date
import time
import pytz

tips_log = logging.getLogger(__name__ + '.tips')
rain_log = logging.getLogger(__name__ + '.rain')
main_log = logging.getLogger(__name__ + '.main')
error_log = logging.getLogger(__name__ + '.errors')

main_log.setLevel(logging.INFO)
error_log.setLevel(logging.ERROR)
tips_log.setLevel(logging.INFO)
rain_log.setLevel(logging.INFO)

rain_log.addHandler(logging.FileHandler('logs/chat/chat_rain.log'))
tips_log.addHandler(logging.FileHandler('logs/chat/chat_tips.log'))
error_log.addHandler(logging.FileHandler('logs/chat/chat_errors.log'))

main_log.addHandler(logging.FileHandler('logs/chat/chat.log'))
main_log.addHandler(logging.StreamHandler())


class NotTimeYetException(Exception):
    pass

async def req_challenge(key):
    res = await stake_http.req_ws_challenge(key)
    r = json.loads(res)
    util.check_response(r)
    challenge_key = r['data']['requestWebSocketChallenge']['key']
    challenge = r['data']['requestWebSocketChallenge']['challenge']
    return challenge, challenge_key
# params from req_challenge


async def send_ack(ws, type):
    await ws.send(json.dumps({'type': type}))
    return True


def ws_con_init(key, challenge, challenge_key, language='en'):
    data = {'type': 'connection_init', 'payload': {
        "language": language,
        # "challenge": challenge,
        # "challengeKey": challenge_key,
        "accessToken": key,
        "lockdownToken": ""
    }}
    return data

# id is auto increment for each message sent to server


def ws_subscribe_chat_id(key, chat_id, id, language='en'):
    data = {
        "id": id,
        "type": "start",
        "payload": {
            "variables": {
                "chatId": chat_id
            },
            "extensions": {},
            "operationName": "ChatMessages",
            "query": "subscription ChatMessages($chatId: String!) {\n  chatMessages(chatId: $chatId) {\n    ...ChatMessage\n    __typename\n  }\n}\n\nfragment ChatMessage on ChatMessage {\n  id\n  data {\n    ... on ChatMessageDataRace {\n      race {\n        name\n        status\n        startTime\n        leaderboard(limit: 10) {\n          ...RacePosition\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    ... on ChatMessageDataTrivia {\n      status\n      question\n      answer\n      currency\n      amount\n      winner {\n        id\n        name\n        __typename\n      }\n      __typename\n    }\n    ... on ChatMessageDataText {\n      message\n      __typename\n    }\n    ... on ChatMessageDataBot {\n      message\n      __typename\n    }\n    ... on ChatMessageDataTip {\n      tip {\n        id\n        amount\n        currency\n        sender: sendBy {\n          id\n          name\n          __typename\n        }\n        receiver: user {\n          id\n          name\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    ... on ChatMessageDataRain {\n      rain {\n        amount\n        currency\n        rainUsers {\n          user {\n            id\n            name\n            __typename\n          }\n          __typename\n        }\n        giver: sendBy {\n          id\n          name\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  createdAt\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment RacePosition on RacePosition {\n  position\n  user {\n    id\n    name\n    __typename\n  }\n  wageredAmount\n  payoutAmount\n  percentage\n  currency\n  __typename\n}\n",
            "accessToken": key,
            "language": language
        }
    }
    return data


async def get_chat_rooms(key):
    res = await stake_http.public_chats(key)
    r = json.loads(res)
    util.check_response(r)
    chats = []
    for public_chat in r['data']['publicChats']:
        name = public_chat['name']
        id = public_chat['id']
        is_public = public_chat['isPublic']
        chat_obj = {'name': name, 'id': id, 'is_public': is_public}
        chats.append(chat_obj)
    return chats


msgs = ['gtz', 'nice']

lm_dt = datetime.now()


async def send_rdm_msg(key, chat_id, delay = 600):
    global lm_dt
    if (datetime.now() - lm_dt).seconds < delay:
        raise NotTimeYetException(f'Cannot send any messages yet {str(lm_dt)}')
    else:
        lm_dt = datetime.now()
    await asyncio.sleep(random.randint(10, 30))
    return await stake_http.send_message(key, chat_id, random.choice(msgs))


async def receive_data_loop(ws, key, chat_id, should_print=False, should_chat=False):
    global lm_dt
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
            if not 'payload' in r or not 'data' in r['payload'] or not 'chatMessages' in r['payload']['data']:
                raise Exception(r)
            cm = r['payload']['data']['chatMessages']
            chat_message_data = cm['data']
            username: str = str(cm['user']['name'])
            if username.lower() == 'wiggle':
                lm_dt = datetime.now()
            if 'rain' in chat_message_data:
                amt = float(chat_message_data['rain']['amount'])
                rain_currency = chat_message_data['rain']['currency']
                rain_users = chat_message_data['rain']['rainUsers']
                str_tipped = ','.join([user['user']['name']
                                      for user in rain_users])
                logs = ' '.join(['($)',
                                 util.cur_date(),
                                 username, 'tipped', str(
                                     amt), str(rain_currency), 'to', str_tipped])
                if should_print:
                    rain_log.info(logs)
                    util.write_chat(logs)
                    if should_chat:
                        await send_rdm_msg(key=key, chat_id=chat_id, delay = 300)
            elif 'tip' in chat_message_data:
                tip = chat_message_data['tip']
                amt = tip['amount']
                cur = tip['currency']
                sender = tip['sender']['name']
                recvr = tip['receiver']['name']
                if should_print:
                    logs = ' '.join([
                        f'($) {sender}'.ljust(20), 'tipped',
                        recvr, str(amt), str(cur)])
                    tips_log.info(logs)
                    util.write_chat(logs)
                    if should_chat:
                        await send_rdm_msg(key=key, chat_id=chat_id, delay = 600)
            elif 'message' in chat_message_data:
                m = str(chat_message_data['message'])
                if should_print:
                    chat = '\t'.join(
                        [util.cur_date(), username.ljust(20), m])
                    util.write_chat(chat)
                    main_log.info(chat)
            else:
                if should_print:
                    main_log.info(r)
        except NotTimeYetException:
            pass
        except exceptions.ConnectionClosedError:
            pass
        except Exception as e:
            await asyncio.sleep(0.01)
            error_log.error(e, exc_info=1)

    return False


async def connect(key, challenge, challenge_key):
    try:
        await asyncio.sleep(1)
        headers = {
            "accept-language": "en-US,en;q=0.9,pt;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
        }
        ws = await asyncio.wait_for(client.connect(uri='wss://api.stake.com/subscriptions', subprotocols=['graphql-ws'], extra_headers=headers, origin='https://stake.com'), 30)
        if not ws:
            return None
        data = ws_con_init(key=key, challenge=challenge,
                           challenge_key=challenge_key)
        await ws.send(json.dumps(data))
        await ws.recv()
        return ws
    except exceptions.InvalidStatusCode:
        pass
    except exceptions.ConnectionClosedError:
        pass
    except Exception as e:
        error_log.error(e, exc_info=1)
    return None


async def subscribe_chat_rooms(ws, key, chat_rooms, id, idx):
    try:
        for chat_room in chat_rooms:
            chat_name = chat_room['name']
            valid_rooms = ['en']
            if not chat_name in valid_rooms:
                continue
            chat_id = chat_room['id']
            data = ws_subscribe_chat_id(key=key, chat_id=chat_id, id=len(id))
            await ws.send(json.dumps(data))
            id += [1]
            asyncio.ensure_future(receive_data_loop(
                ws=ws, key=key, chat_id=chat_id, should_print=idx == 0, should_chat=chat_name == 'en'))
        return ws
    except Exception as e:
        error_log.error(e, exc_info=1)
    return None


async def main(key, idx):
    chat_rooms = await get_chat_rooms(key)
    while True:
        try:
            id = [1]
            await asyncio.sleep(1)
            challenge, challenge_key = (None, None) #await req_challenge(key)
            ws = await asyncio.wait_for(connect(key=key, challenge=challenge,
                                                challenge_key=challenge_key), 30)
            if ws:
                await subscribe_chat_rooms(ws=ws, key=key, chat_rooms=chat_rooms, id=id, idx=idx)
                await ws.wait_closed()
        except exceptions.InvalidStatusCode:
            pass
        except exceptions.ConnectionClosedError:
            pass
        except Exception as e:
            error_log.error(e, exc_info=1)
        finally:
            await asyncio.sleep(1)

if __name__ == '__main__':
    time.sleep(5)
    lm_dt = datetime.now()
    keys = stake_keys.load_keys('data/api_keys_twitter.txt')

    for idx, key in enumerate(keys):
        asyncio.get_event_loop().create_task(main(key, idx))
    asyncio.get_event_loop().run_forever()
