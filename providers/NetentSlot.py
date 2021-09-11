import stake_http
import util
from urllib.parse import parse_qs
from typing import NewType
import json
session_id = NewType('session_id', str)


class NetentSlot:
    symbol = ''
    slug = ''
    session_id: session_id = ''
    bet_lines = ''
    bet_level = 1  # multiplies denom
    bet_denom = 1  # in cents
    game_id = ''  # To be filled from stake config

    def get_win(self, qs_dict):
        return float(qs_dict['game.win.amount'][0]) if 'game.win.amount' in qs_dict else 0

    def get_bal(self, qs_dict):
        return float(qs_dict['balance'][0]) if 'balance' in qs_dict else 0

    def is_in_free_spin(self, qs_dict):
        return qs_dict['gamestate.current'][0] == 'freespin' if 'gamestate.current' in qs_dict else False

    def is_in_free_spin_initial(self, qs_dict):
        return qs_dict['freespins.initial'][0] == '1' if 'freespins.initial' in qs_dict else False

    def free_spins_win(self, qs_dict):
        return int(qs_dict['freespins.totalwin.cents'][0]) if 'freespins.totalwin.cents' in qs_dict else 0

    def inc_counter(self):
        self.counter += 2
        self.idx += 1

    def get_softswiss_session(self, key, currency):
        # Start new session and to get mcgkey
        r = stake_http.get_softswiss_launch_options(
            key=key, currency=currency, target_currency='usd', slug=self.slug)
        util.check_response(r)
        r = r.json()
        launch_opts = json.loads(r['data']['getSoftswissLaunchOptions'])
        self.game_id = launch_opts['configuration']['gameId']
        return launch_opts['configuration']['sessionId']

    def do_free_spin(self):
        r_fs = stake_http.schudamore_do_free_spin(
            sess_id=self.session_id, game_id=self.game_id)
        qs_dict = parse_qs(r_fs.text)
        while self.is_in_free_spin(qs_dict):
            r_fs = stake_http.schudamore_do_free_spin(
                sess_id=self.session_id, game_id=self.game_id)
            qs_dict = parse_qs(r_fs.text)
        return r_fs

    def do_init(self):
        # Get last state
        r = stake_http.netent_init(
            sessid=self.session_id, game_id=self.game_id)
        qs_dict = parse_qs(r.text)
        if self.is_in_free_spin_initial(qs_dict):
            r_fs = self.select_horse(1)
            if 'errordata' in r_fs.text:
                r_fs = self.do_free_spin()
            print(r_fs.text)
        print(r.text)

    def start_new_session(self, key, currency):
        self.session_id = self.get_softswiss_session(key, currency)
        print(self.session_id)
        self.do_init()

    def select_horse(self, horse_idx):
        return stake_http.scudamore_select_horse(sess_id=self.session_id, game_id=self.game_id, horse_idx=horse_idx)

    def do_bet(self):
        r = stake_http.do_netent_spin(
            sess_id=self.session_id, game_id=self.game_id,
            bet_denom=self.bet_denom, bet_lines=self.bet_lines,
            bet_level=self.bet_level)
        qs_dict = parse_qs(r.text)
        credit = (self.bet_denom * self.bet_level)/10
        if self.is_in_free_spin(qs_dict):
            r_fs = self.select_horse(1)
            r_fs = self.do_free_spin()
            qs_dict = parse_qs(r_fs)
            fs_win = self.free_spins_win(qs_dict)
            print(f'{fs_win:.2f}'.ljust(10), f'{fs_win/credit:.2f}x'.ljust(10))
        win_amt = self.get_win(qs_dict)
        pay_multi = win_amt/credit
        print(f'{win_amt:.2f}'.ljust(10), f'{pay_multi:.2f}x'.ljust(
            10), f'{credit:.2f}'.ljust(10))
        return True


class NetentScudamore(NetentSlot):
    slug = 'netent-scudamore-not-mobile-sw'
    bet_lines = '0-19'

