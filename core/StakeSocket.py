import stake_http
import util
import random
import asyncio
import json
import logging
from websockets import client

error_log = logging.getLogger(__name__ + '.errors')
error_log.addHandler(logging.FileHandler('logs/stake_socket/errors.log'))


class StakeSocket:
    uri = 'wss://api.stake.com/subscriptions'
    subprotocols = ['graphql-ws']
    headers = {
        "accept-language": "en-US,en;q=0.9,pt;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
    }
    origin = 'https://stake.com'

    def req_challenge(key):
        r = stake_http.req_ws_challenge(key)
        util.check_response(r)
        r = r.json()
        challenge_key = r['data']['requestWebSocketChallenge']['key']
        challenge = r['data']['requestWebSocketChallenge']['challenge']
        return challenge, challenge_key

    async def connect(self, key, subscriptions):
        try:
            await asyncio.sleep(random.randint(1, 2))
            challenge, challenge_key = self.req_challenge(key)

            ws = await asyncio.wait_for(client.connect(uri=self.uri, subprotocols=self.subprotocols, extra_headers=self.headers, origin=self.origin), 30)
            if not ws:
                return None
            data = self.init_data(key=key, challenge=challenge,
                                    challenge_key=challenge_key)
            await ws.send(json.dumps(data))
            await ws.recv()
            for sub in subscriptions:
                await sub()
            return ws
        except Exception as e:
            error_log.error(e, exc_info=1)
        return None

    def init_data(key, challenge, challenge_key, language='en'):
        data = {'type': 'connection_init', 'payload': {
            "language": language,
            "challenge": challenge,
            "challengeKey": challenge_key,
            "accessToken": key,
            "lockdownToken": ""
        }}
        return data
