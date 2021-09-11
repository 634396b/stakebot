from Cryptocurrency import Cryptocurrency as Crypto
from exceptions import InBonusException, NoMoneyException, OutOfBoundsLinesException, UnhandledException
from urllib.parse import parse_qs, urlparse, unquote
import stake_http
import util
import logging


log = logging.getLogger(__name__ + '-main')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/bonus_hunt/Habanero.log')
fh.setLevel(logging.DEBUG)
log.addHandler(fh)


class Habanero:
    symbol = ''
    slug = ''
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

    def __init__(self, currency: Crypto = None, stop_if_bonus=True, key='', credit = 0.01):
        self.currency = currency
        self.stop_if_bonus = stop_if_bonus
        self.stake_api_key = key
        self.credit = credit

    def get_id(self):
        return str(self.slug) + '-' + str(self.currency)

    def get_bet(self, credit):
        return float(credit) * float(self.line)

    def inc_counter(self):
        self.counter += 2
        self.idx += 1

    def get_softswiss_session(self):
        # Start new session and to get mcgkey
        r = stake_http.start_softswiss_session(key=self.stake_api_key, currency=self.currency,
                                               target_currency='usd', slug=self.slug)
        util.check_response(r)
        r = r.json()
        return r['data']['startSoftswissSession']

    def get_game_config(self, softswiss_url):
        game_config = stake_http.pragmatic_play_game(
            softswiss_url)
        self.symbol = self.get_symbol_from_url(softswiss_url)
        self.game_service_url = game_config['gameService']

    def do_init(self):
        pass
    
    def start_new_session(self):
        print(self.get_id(), 'start_new_session')
        softswiss_url = self.get_softswiss_session()
        self.get_game_config(softswiss_url)
        self.do_init()

    def start_new_session_demo(self):
        softswiss_url_json = stake_http.demo_softswiss_session(
            self.stake_api_key, slug=self.slug).json()
        softswiss_url = softswiss_url_json['data']['startSoftswissDemo']
        self.get_game_config(softswiss_url)
        self.do_init()

    def do_bet(self):
        pass

