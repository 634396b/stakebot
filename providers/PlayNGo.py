import re
import requests
from core.Cryptocurrency import Cryptocurrency as Crypto
from exceptions import InBonusException
from urllib.parse import parse_qs, urlparse
import core.http.stake as stake_http
import util
import logging
import json
from core.http.util import async_get, async_post

log = logging.getLogger(__name__ + '-main')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/bonus_hunt/PlayNGo.log')
fh.setLevel(logging.DEBUG)
log.addHandler(fh)



class PlayNGo:
    slug = ''
    stake_api_key = ''
    idx = 0
    kwargs = {}
    max_lines = None
    min_lines = None
    currency: Crypto = None
    stop_if_bonus = True
    denom = 1  # coin value
    coins = 10
    lines = 1  # total $ amount = line * credit
    api_url = ''

    def __init__(self, currency: Crypto = None, stop_if_bonus=True, key=''):
        self.currency = currency
        self.stop_if_bonus = stop_if_bonus
        self.stake_api_key = key

    def get_id(self):
        return str(self.slug) + '-' + str(self.currency)

    def inc_counter(self):
        self.idx += 1
        return self.idx

    def fmt_data(self, data):
        post_data = f'd={self.inc_counter()}\r\n'
        post_data += f'{self.sid}\r\n'
        post_data += ' '.join(data)
        print(self.get_id(), post_data)
        return post_data

    async def get_softswiss_session(self):
        # Start new session and to get mcgkey
        res = await stake_http.get_softswiss_launch_options(key=self.stake_api_key, currency=self.currency,
                                                            target_currency='usd', slug=self.slug)
        util.check_response(res)
        r = json.loads(res)
        util.check_response(r)
        print(r)
        launch_opts = json.loads(r['data']['getSoftswissLaunchOptions'])
        self.softswiss_url = launch_opts['desktop_url']
        qs_dict = parse_qs(urlparse(self.softswiss_url).query)
        self.ticket = qs_dict['ticket'][0]  # uuid
        # Check Gameloader for this forumla
        self.pid = int(qs_dict['pid'][0])  # * 10 - 8
        # gid is not the same as game_id, gid is a str representation
        self.gid = qs_dict['gid'][0]
        self.origin = launch_opts['origin']
        self.lang = qs_dict['lang'][0]

    async def get_game_loader(self, practice='1'):
        headers = {'origin': self.origin}
        container_doc = await async_get(self.softswiss_url, headers=headers)
        # print(container_doc)
        game_loader_src = re.search(
            "src = \"(.+?)\"", container_doc).group(1)
        print(self.origin + '/casino/' + game_loader_src)
        game_loader_doc = await async_get(
            self.origin + '/casino/' + game_loader_src, headers=headers)
        self.game_id = re.search("gameid: \"(.+?)\"", game_loader_doc).group(1)
        game_name_json = await async_get(f'https://acccw.playngonetwork.com/games/{self.game_id}')
        self.game_name = json.loads(game_name_json)['name']
        # print(game_loader_doc.text)
        config_url = f'https://acccw.playngonetwork.com/Configuration/v2?pid={self.pid}&gameid={self.game_id}&lang=en_GB&practice={practice}&brand=easygo&ctx=&jurisdiction=CW&platform=megaton&currency=USD&country=&channel=desktop'
        config = await async_get(config_url, headers=headers)
        self.config = json.loads(config) #unused

    async def do_init_session(self):
        COMMAND_SESSION = '103'
        post_data = f'd={self.inc_counter()}\r\n'
        post_data += '0\r\n'
        post_data += ' '.join([COMMAND_SESSION,  # login req
                               f'{self.pid * 10 - 8}',
                               '"en_GB"',
                               f'{self.game_id}',
                               '"Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F92.0.4515.159%20Safari%2F537.36"',
                               f'"{self.game_name}"',
                               '"desktop"'])
        r = await async_post(self.api_url,
                             headers={'origin': self.origin}, data=post_data)
        print(r)
        r = r.split(' ')
        d = [f for f in r if f != '']
        assert d[0].replace('d=', '') == COMMAND_SESSION, d
        self.sid = d[1].replace('\r\n', '').replace('"', '')

    async def do_init_login(self):
        COMMAND_LOGIN = '101'
        post_data = self.fmt_data([COMMAND_LOGIN,
                                   f'"{self.ticket}"', '""', '""', '""', '""'])
        print(post_data)
        r = await async_post(self.api_url,
                             headers={'origin': self.origin}, data=post_data)
        print(r)
        row = r.split('\r\n')
        row_0 = row[0].split(' ')
        d = row_0[0].replace('d=', '')
        assert d == '103', d
        self.sid = row_0[1].replace('"', '')

    async def start_game(self):
        GAME_STARTED = 104
        post_data = self.fmt_data(
            [
                f'{GAME_STARTED}',
                f'{self.game_id}'
                '0'  # is practice mode?
            ]
        )
        r = await async_post(self.api_url,
                             headers={'origin': self.origin}, data=post_data)
        print(r)
        rows = r.split('\r\n')
        row_0 = rows[0].split(' ')
        d = row_0[0].replace('d=', '')
        assert d == '104', d
        for row in rows:
            row = row.split(' ')
            if row[0] == '54':  # Bet config
                i = int(row[1])
                self.denoms = row[2:2+i]
            elif row[0] == '83':  # FREE SPIN STATUS
                if row[1] == '1':  # IN FREE SPINS
                    raise InBonusException(rows)

    async def do_spin(self):
        post_data = self.fmt_data(['1', f'{self.coins}',
                                   f'{self.lines}', f'{self.denom}', '1'])
        r = await async_post(self.api_url,
                             headers={'origin': self.origin}, data=post_data)
        self.handle_response(r)

    async def do_bonus_opt(self, opt):
        post_data = self.fmt_data(['2', '3', str(opt)])
        r = await async_post(self.api_url,
                             headers={'origin': self.origin}, data=post_data)

    async def do_collect(self):
        post_data = self.fmt_data(['4', '0'])
        r = await async_post(self.api_url,
                             headers={'origin': self.origin}, data=post_data)
        self.handle_response(r)

    async def do_collect_mini(self):
        post_data = self.fmt_data(['2', '6'])
        r = await async_post(self.api_url,
                             headers={'origin': self.origin}, data=post_data)
        self.handle_response(r)

    async def collect_free_spin(self, free_spin_number):
        post_data = self.fmt_data(['7', f'{free_spin_number}'])
        r = await async_post(self.api_url,
                             headers={'origin': self.origin}, data=post_data)
        self.handle_response(r)

    async def handle_response(self, r: str):
        rows = [f for f in r.split('\r\n') if f != '']
        print(self.get_id(), r)
        rows[0] = rows[0].replace('d=', '')
        for row in rows:
            row = row.split(' ')
            if row[0] == '111':
                raise Exception(self.get_id(), rows)
            if row[0] == '1':  # status of reels
                pass
            elif row[0] == '2':
                if len(row) == 2:
                    if row[1] == '6':  # 2 6
                        return self.collect_free_spin('0')
                if len(row) < 4:
                    continue
                if row[3] == '8':  # mini-feature
                    print(self.get_id(), 'mini-feature', row)
                    return self.do_collect_mini()
                elif row[3] == '9':
                    raise InBonusException(self.get_id(), rows)
                elif row[3] == '10':
                    return self.do_collect_mini()
                elif row[3] == '11':  # raging rex (choice)
                    # last row has options indexes
                    # options = rows[-1].split(' ')
                    # self.do_bonus_opt(random.choice(options))
                    # return self.do_collect_mini()
                    raise InBonusException(self.get_id(), rows)
            elif row[0] == '3':  # winning reel
                if len(row) < 3:
                    continue
                if row[1] == '0':
                    if row[2] == '0':  # no win
                        pass
                    else:
                        return self.do_collect()
            elif row[0] == '6':  # win amount
                pass
            elif row[0] == '4':  # gamble amount
                pass
            elif row[0] == '83':  # free spin status
                return self.do_collect()
            elif row[0] == '52':  # balance status
                pass
            return None
    async def start_new_session(self):
        self.api_url = 'https://accfly.playngonetwork.com'
        print(self.get_id(), 'start_new_session')
        await self.get_softswiss_session()
        await self.get_game_loader()
        await self.do_init_session()
        await self.do_init_login()
        await self.start_game()

    async def start_new_session_demo(self):
        self.api_url = 'https://accflyp.playngonetwork.com'
        print(self.get_id(), 'start_new_session')
        await self.get_softswiss_session()
        await self.get_game_loader()
        await self.do_init_session()
        await self.do_init_login()
        await self.start_game()
