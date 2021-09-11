from core.Cryptocurrency import Cryptocurrency as Crypto
from exceptions import InBonusException, NoMoneyException, OutOfBoundsLinesException, UnhandledException
from urllib.parse import parse_qs, urlparse, unquote
from typing import NewType
import core.http.pragmatic as prag_http
import core.http.stake as stake_http
import util
import logging
import json

MgcKey = NewType('MgcKey', str)

log = logging.getLogger(__name__ + '-main')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/bonus_hunt/PragmaticPlay.log')
fh.setLevel(logging.DEBUG)
log.addHandler(fh)


class PragmaticPlay:
    symbol = ''
    slug = ''
    mgckey = ''
    stake_api_key = ''
    idx = 1
    counter = 1
    line = 1  # total $ amount = line * credit
    repeat = 0
    kwargs = {}
    max_lines = None
    min_lines = None
    currency: Crypto = None
    stop_if_bonus = True
    credit = 0.01
    #TODO is tumble

    def __init__(self, currency: Crypto = None, stop_if_bonus=True, key='', credit=0.01):
        self.currency = currency
        self.stop_if_bonus = stop_if_bonus
        self.stake_api_key = key
        self.credit = credit

    def get_id(self):
        return str(self.stake_api_key)[0:6] + '-' + str(self.slug) + '-' + str(self.currency)

    def get_bet(self, credit):
        return float(credit) * float(self.line)

    def has_bonus_luck(self, qs_dict):
        return 'bl' in qs_dict

    def get_symbol_from_url(self, url):
        parsed_url = urlparse(unquote(url))
        qs_dict = parse_qs(parsed_url.query)
        if 'gameSymbol' in qs_dict:
            return qs_dict['gameSymbol'][0]
        elif 'symbol' in qs_dict:
            return qs_dict['symbol'][0]

    def free_spin_is_undefined(self, qs_dict):
        return 'fs' in qs_dict and qs_dict['fs'][0] == ''

    def free_spin_is_a_number(self, qs_dict):
        return 'fs' in qs_dict and int(qs_dict['fs'][0]) > 0

    def next_action_is_bonus(self, qs_dict):
        return 'na' in qs_dict and qs_dict['na'][0] == 'b'

    def next_action_is_spin(self, qs_dict):
        return 'na' in qs_dict and qs_dict['na'][0] == 's'

    def next_action_is_collect(self, qs_dict):
        return 'na' in qs_dict and qs_dict['na'][0] == 'c'

    def next_action_is_free_spin_option(self, qs_dict):
        return 'na' in qs_dict and qs_dict['na'][0] == 'fso'

    def is_in_bonus(self, qs_dict):
        # ('fs' in qs_dict) or
        # fs should be equal to 1
        # sometimes appears in qs
        # 'b' = bonus or fso = 'free spin option'
        # Should address free spin option as its not always a bonus
        #     BVAPI.postGameIdle = params["na"] == "s" && params["fs"] == undefined && params["fs_total"] == undefined && params["rs"] == undefined;
        return self.next_action_is_bonus(qs_dict) \
            or self.next_action_is_free_spin_option(qs_dict)\
            or self.free_spin_is_undefined(qs_dict)\
            or self.free_spin_is_a_number(qs_dict)

    def get_win(self, qs_dict):
        return float(qs_dict['w'][0].replace(',', '')) if 'w' in qs_dict else 0

    def get_tw_win(self, qs_dict):
        return float(qs_dict['tw'][0].replace(',', '')) if 'tw' in qs_dict else 0

    def get_bal(self, qs_dict):
        return float(qs_dict['balance'][0].replace(',', '')) if 'balance' in qs_dict else 0

    def get_line(self, qs_dict):
        return qs_dict['l'][0] if 'l' in qs_dict else self.line

    def inc_counter(self):
        self.counter += 2
        self.idx += 1

    async def get_softswiss_session(self):
        # Start new session and to get mcgkey
        resp = await stake_http.start_softswiss_session(key=self.stake_api_key, currency=self.currency,
                                                        target_currency='usd', slug=self.slug)
        util.check_response(resp)
        r = json.loads(resp)
        util.check_response(r)
        return r['data']['startSoftswissSession']

    async def get_game_config(self, softswiss_url):
        game_config = await prag_http.play_game(softswiss_url)
        self.symbol = self.get_symbol_from_url(softswiss_url)
        self.mgckey: MgcKey = game_config['mgckey']
        self.game_service_url = game_config['gameService']

    async def do_init(self):
        # Get last state
        r = await prag_http.do_init(url=self.game_service_url,
                                    mgckey=self.mgckey, symbol=self.symbol)
        self.inc_counter()
        log.debug(self.get_id() + ' ' + r)
        qs_dict = parse_qs(r)
        log.debug(self.get_id() + ' ' + str(qs_dict))
        # Game will not continue if not collected previous win
        has_bl = self.has_bonus_luck(qs_dict)
        if has_bl:
            self.kwargs['bl'] = 0
        if self.stop_if_bonus and self.is_in_bonus(qs_dict):
            raise InBonusException(self.get_id() + ' In bonus')
        self.line = int(self.get_line(qs_dict))
        if self.max_lines is not None and self.line > self.max_lines:
            raise OutOfBoundsLinesException(
                self.slug, 'lines', self.line,  'max_lines', self.max_lines)
        if self.min_lines is not None and self.line < self.min_lines:
            raise OutOfBoundsLinesException(
                self.slug, 'lines', self.line, 'min_lines', self.min_lines)
        if self.next_action_is_collect(qs_dict) or self.get_win(qs_dict) > 0:
            await self.collect_win()

    async def start_new_session(self):
        print(self.get_id(), 'start_new_session')
        softswiss_url = await self.get_softswiss_session()
        await self.get_game_config(softswiss_url)
        await self.do_init()

    async def start_new_session_demo(self):
        session_data = await stake_http.demo_softswiss_session(
            self.stake_api_key, self.slug)
        session_data_json = json.loads(session_data)
        softswiss_url = session_data_json['data']['startSoftswissDemo']
        await self.get_game_config(softswiss_url)
        await self.do_init()

    async def do_bet(self, credit_override=None):
        credit = credit_override or self.credit
        print(self.get_id(), 'do_bet')
        r = await prag_http.spin(
            url=self.game_service_url,
            mgckey=self.mgckey, symbol=self.symbol,
            index=self.idx, counter=self.counter,
            credit=f'{(credit):.2f}', line=self.line,
            repeat=self.repeat,
            **self.kwargs
        )
        self.inc_counter()
        qs_dict = parse_qs(r)
        log.debug(self.get_id() + ' ' + str(r))
        is_in_bonus = self.is_in_bonus(qs_dict)
        if is_in_bonus and self.stop_if_bonus:
            print('BONUS', self.get_id())
            raise InBonusException(self.get_id(), ' In bonus')

        if len(qs_dict.keys()) == 0:
            print(self.get_id(), 'ERROR NO KEYS IN qs', r, credit, self.counter,
                  self.idx, self.line, self.repeat)
            raise UnhandledException(self.get_id(), r)
            # Attempt to collect win since sometimes no keys indicates status message
            # Which we TODO have to parse
            # self.collect_win()

        # Session aborted
        if 'ext_code' in qs_dict:
            if 'nomoney' in qs_dict:
                raise NoMoneyException(self.get_id())
            print(self.get_id(), qs_dict)
            raise UnhandledException(self.slug)
        else:
            tw_win_amt = self.get_tw_win(qs_dict)
            win_amt = self.get_win(qs_dict)
            balance = self.get_bal(qs_dict)
            pay_multi = win_amt/self.get_bet(credit) if credit > 0 else 0
            logs = [f'{util.cur_date()}'.ljust(20),
                    f'{self.get_id()}'.replace(
                        'pragmatic-', '')[0:20].ljust(20),
                    # f'win ${win_amt:.2f}'.ljust(15),
                    f'{pay_multi:.2f}x'.ljust(20),
                    f'${self.get_bet(credit):.2f}'.ljust(20),
                    f'${tw_win_amt:.2f}'.ljust(20),
                    f'${balance:.2f}'.ljust(20)
                    ]
            if is_in_bonus:
                logs += ['in free spins'.rjust(20)]
            print(' '.join(logs))
            util.write_logs('Wiggle', ' '.join(logs))
            if self.next_action_is_collect(qs_dict) or self.get_win(qs_dict) > 0:
                await self.collect_win()
            return True

    async def collect_win(self):
        print(self.get_id(), 'collect_win')
        w = await prag_http.collect_win(
            url=self.game_service_url,
            mgckey=self.mgckey, symbol=self.symbol,
            index=self.idx, counter=self.counter, repeat=self.repeat)
        self.inc_counter()
        return w

    async def reload_balance(self):
        print(self.get_id(), 'reload_balance')
        r = await prag_http.reload_balance(self.mgckey)
        qs_dict = parse_qs(r)
        balance = self.get_bal(qs_dict)
        return balance
