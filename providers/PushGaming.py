from core.Cryptocurrency import Cryptocurrency as Crypto
from exceptions import InBonusException, NoMoneyException, OutOfBoundsLinesException, UnhandledException
from urllib.parse import parse_qs, urlparse, unquote
import core.http.stake as stake_http
import core.http.pushgaming as pushgaming_http
import util
import logging
import json
from main import Bot
log = logging.getLogger(__name__ + '-main')
log.propagate = False
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/bonus_hunt/PushGaming.log')
fhsl = logging.FileHandler('logs/bonus_hunt/PushGaming_wins.log')
fhs = logging.StreamHandler()
fh.setLevel(logging.DEBUG)
fhsl.setLevel(logging.INFO)
fhs.setLevel(logging.INFO)
log.addHandler(fh)
log.addHandler(fhs)
log.addHandler(fhsl)


class PushGaming:
    slug = ''
    stake_api_key = ''
    line = 1  # total $ amount = line * credit
    repeat = 0
    kwargs = {}
    currency: Crypto = None
    stop_if_bonus = True
    session_url = ''
    action_url = ''
    game_code = ''
    client_states_url = ''

    def __init__(self, currency: Crypto = None, stop_if_bonus=True, key=''):
        self.currency = currency
        self.stop_if_bonus = stop_if_bonus
        self.stake_api_key = key

    def get_id(self):
        return str(self.stake_api_key)[0:6] + '-' + str(self.slug) + '-' + str(self.currency)

    def get_payload(self, *args, **kwargs):
        pass

    def return_state(self, *args, **kwargs):
        pass

    async def handle_response(self, *args, **kwargs):
        pass

    def log_message(self, *args, **kwargs):
        pass

    async def game_specific_init(self):
        pass

    async def get_softswiss_session(self):
        # Start new session and to get mcgkey
        res = await stake_http.start_softswiss_session(key=self.stake_api_key, currency=self.currency,
                                                       target_currency='usd', slug=self.slug)
        log.debug(res)
        util.check_response(res)
        r = json.loads(res)
        util.check_response(r)

        return r['data']['startSoftswissSession']

    async def get_game_config(self, softswiss_url):
        parsed_url = urlparse(unquote(softswiss_url))
        qs_dict = parse_qs(parsed_url.query)
        payload = self.get_sessions_payload(qs_dict)
        print(payload)
        session_obj = await pushgaming_http.start_session(self.session_url, payload)
        log.debug(session_obj)
        session_json = json.loads(session_obj)
        print(session_json)
        self.session_id = session_json['sessionId']

    def get_sessions_payload(self, qs_dict):
        self.auth_token = qs_dict['token'][0]
        self.player_id = qs_dict['playerId'][0]
        self.game_code = qs_dict['rgsGameId'][0]
        self.igp_code = 'ss-easygo'  # qs_dict['igpCode']
        self.lang = qs_dict['lang'][0]
        self.mode = str(qs_dict['mode'][0]).lower()
        payload = {
            'authToken': self.auth_token,
            'gameCode': self.game_code,
            'igpCode': self.igp_code,
            'lang': self.lang,
            'mode': self.mode,
            'playerId': self.player_id,
            'type': 'playerLogin',
        }
        log.debug(payload)

        return payload

    async def start_new_session(self):
        print(self.get_id(), 'start_new_session')
        softswiss_url = await self.get_softswiss_session()
        await self.get_game_config(softswiss_url)
        await self.game_specific_init()

    async def complete_action(self, action_id, round_over):
        r = await pushgaming_http.put_action(action_url=self.action_url,
                                             action_id=action_id, session_id=self.session_id)
        cs = await pushgaming_http.put_client_states(client_states_url=self.client_states_url, game_code=self.game_code,
                                                     action_id=action_id, round_over=round_over, spin_index=0, session_id=self.session_id)
        return cs

    def spin_payload(self):
        pass

    async def do_bet(self, bet=20):
        res = await pushgaming_http.post_action(
            action_url=self.action_url, payload=self.spin_payload(bet), session_id=self.session_id)
        log.debug(res)
        r = json.loads(res)
        await self.handle_response(r, bet)
        return self.return_state()


class JamminJars2(PushGaming):
    slug = 'pushgaming-jammin-jars-2'
    session_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/jamminjars2/api/sessions'
    action_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/jamminjars2/api/actions'
    client_states_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/jamminjars2/api/client-states'
    get_latest_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/jamminjars2/api/actions/latest'

    giga_jar_level = ''
    giga_jar_needed = ''
    giga_jar_collected = ''

    async def game_specific_init(self):
        action = await self.get_latest()
        if 'actionComplete' in action and action['actionComplete'] == False:
            await self.complete_action(action_id=action['actionId'], round_over=True)

    async def get_latest(self):
        action = await pushgaming_http.get_latest(
            get_latest_url=self.get_latest_url, session_id=self.session_id)
        action = json.loads(action)
        return action

    async def handle_response(self, r, bet):
        if 'actionComplete' in r and r['actionComplete'] == False:
            action_id = r['actionId']
            await self.complete_action(action_id, round_over=True)
        if 'occurrenceId' in r:
            if 'details' in r and 'code' in r['details'] and 'last_action_is_not_completed' in r['details']['code']:
                action_id = r['details']['actionId'][0]
                return await self.complete_action(action_id, round_over=True)
            elif 'code' in r and r['code'] == 'InsufficientFunds':
                raise Exception(r)
            else:
                log.error(r)
                raise Exception(r)
        win = r['cumulativeWin'] if 'cumulativeWin' in r else None
        self.giga_jar = r['state']['gigaJarLevelAfterAction']
        self.giga_jar_collected = self.giga_jar['goldVinylCollected']
        self.giga_jar_needed = self.giga_jar['collectiblesNeededForNextLevel']
        self.giga_jar_level = self.giga_jar['level']
        self.log_message(bet, win)

    def log_message(self, bet, win):
        log_msg = '\t'.join([f'Bet - ${bet/100:.2f}', f'Win - ${win/100:.2f}', f'{win/bet:.2f}x',
                            f'vinyls - {self.giga_jar_collected}', f'vinyls needed - {self.giga_jar_needed}', f'lvl - {self.giga_jar_level}'])
        log.info(log_msg)

    def return_state(self):
        return self.giga_jar_level, self.giga_jar_collected

    def spin_payload(self, bet):
        return {'action': 'spin', 'bet': bet}


class JamminJars(PushGaming):
    slug = 'push-gaming-jammin-jars'
    session_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/jamminjars/api/sessions'
    action_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/jamminjars/api/actions'
    client_states_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/jamminjars/api/client-states'
    get_latest_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/jamminjars/api/actions/latest'

    async def get_latest(self):
        action = await pushgaming_http.get_latest(
            get_latest_url=self.get_latest_url, session_id=self.session_id)
        action = json.loads(action)
        return action

    async def game_specific_init(self):
        action = await self.get_latest()
        if 'actionComplete' in action and action['actionComplete'] == False:
            await self.complete_action(action_id=action['actionId'], round_over=True)
        return True

    def get_payload(self, qs_dict):
        self.auth_token = qs_dict['token'][0]
        self.player_id = qs_dict['playerId'][0]
        self.game_code = qs_dict['rgsGameId'][0]
        self.igp_code = 'ss-easygo'  # qs_dict['igpCode']
        self.lang = qs_dict['lang'][0]
        self.mode = str(qs_dict['mode'][0]).lower()
        payload = {
            'authToken': self.auth_token,
            'gameCode': self.game_code,
            'igpCode': self.igp_code,
            'lang': self.lang,
            'mode': self.mode,
            'playerId': self.player_id,
            'type': 'playerLogin',
        }
        return payload

    async def handle_respone(self, r, bet):
        if 'actionComplete' in r and r['actionComplete'] == False:
            action_id = r['actionId']
            await self.complete_action(action_id, round_over=True)
        if 'occurrenceId' in r:
            if 'details' in r and 'code' in r['details'] and 'last_action_is_not_completed' in r['details']['code']:
                action_id = r['details']['actionId'][0]
                return await self.complete_action(action_id, round_over=True)
            else:
                log.error(r)
                raise Exception(r)
        win = r['cumulativeWin'] if 'cumulativeWin' in r else None
        self.log_message(bet, win)

    def log_message(self, bet, win):
        log_msg = '\t'.join(
            [f'Bet - ${bet/100:.2f}', f'Win - ${win/100:.2f}', f'{win/bet:.2f}x'])
        log.info(log_msg)

    def spin_payload(self, bet):
        return {'action': 'spin', 'bet': bet}


class MountMagmas(PushGaming):
    slug = 'pushgaming-mount-magmas'
    session_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/mountmagmas/api/sessions'
    action_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/mountmagmas/api/actions-v2'
    client_states_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/mountmagmas/api/client-states'
    get_latest_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/mountmagmas/api/plays/latest'

    async def game_specific_init(self):
        actions = await pushgaming_http.get_latest(
            get_latest_url=self.get_latest_url, session_id=self.session_id)
        actions = json.loads(actions)
        print(actions)
        if 'occurrenceId' in actions:
            if 'details' in actions and 'code' in actions['details'] and 'last_action_is_not_completed' in actions['details']['code']:
                action_id = actions['details']['actionId'][0]
                await self.complete_action(action_id=action_id, round_over=True)
                return await self.game_specific_init()
        self.jackpot_states = actions['actions'][-1]['jackpotState']['actual']
        for jp_state in self.jackpot_states:
            if jp_state['type'] == 'timed':
                self.timed_jp_id = jp_state['instanceId']
            elif jp_state['type'] == 'amount':
                self.amount_jp_id = jp_state['instanceId']
            else:
                raise Exception('Invalid JP state', actions)

    def spin_payload(self, bet, action='mtm-spin'):
        return{
            'action': action,
            'amountJpInstanceId': self.amount_jp_id,
            'bet': bet,
            'fundId': None,
            'gameCode': self.game_code,
            'timedJpInstanceId': self.timed_jp_id
        }

    def choice_payload(self, level, option, pick_index, action='mtm-choice'):
        return{
            'action': action,
            'level': level,
            'option': option,
            'pickIndex': pick_index
        }

    async def do_choice(self, action, bet):
        pick_type = None
        line_level = 0
        index = -1
        last_step = action['steps'][-1]
        if 'userSelection' in last_step:
            pick_type = last_step['userSelection']['pick']['code']
            line_level = last_step['userSelection']['lineLevel']
            index = last_step['userSelection']['indexOnLine']
        index += 1
        if pick_type == 'progress-instant' or pick_type == 'progress':
            line_level += 1
            index = 0
        payload = self.choice_payload(
            option=index, pick_index=index, level=line_level)
        res = await pushgaming_http.post_action(
            action_url=self.action_url, payload=payload, session_id=self.session_id)
        r = json.loads(res)
        await self.handle_response(r, bet)

    async def handle_response(self, r, bet):
        if 'occurrenceId' in r:
            if 'details' in r and 'code' in r['details'] and 'last_action_is_not_completed' in r['details']['code']:
                action_id = r['details']['actionId'][0]
                return await self.complete_action(action_id, round_over=True)
            else:
                log.error(r)
                raise Exception(r)
        actions = r['actions']
        action = actions[-1]
        if 'actionComplete' in action and action['actionComplete'] == False:
            action_id = action['actionId']
            await self.complete_action(action_id, round_over=True)
        if 'mtm-choice' in action['availableActions']:
            await self.do_choice(action, bet)
        win = action['cumulativeWin'] if 'cumulativeWin' in action else None
        self.log_message(bet, win)

    def log_message(self, bet, win):
        log_msg = '\t'.join(
            [f'Bet - ${bet/100:.2f}', f'Win - ${win/100:.2f}', f'{win/bet:.2f}x'])
        log.info(log_msg)


class MysteryMuseum(PushGaming):
    slug = 'push-gaming-mystery-museum'
    session_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/mysterymuseum/api/sessions'
    action_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/mysterymuseum/api/actions-v2'
    client_states_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/mysterymuseum/api/client-states'
    get_latest_url = 'https://player.eu.open.sidetechnology.co/hive/b2c/game/mysterymuseum/api/plays/latest'
    gamble_enabled = True
    min_gamble_multi = 5

    async def game_specific_init(self):
        actions = await pushgaming_http.get_latest(
            get_latest_url=self.get_latest_url, session_id=self.session_id)
        actions = json.loads(actions)
        print(actions)
        if 'occurrenceId' in actions:
            if 'details' in actions and 'code' in actions['details'] and 'last_action_is_not_completed' in actions['details']['code']:
                action_id = actions['details']['actionId'][0]
                await self.complete_action(action_id=action_id, round_over=True)
                return await self.game_specific_init()
        action = actions['actions'][-1]
        if 'availableActions' in action and 'mm-money-gamble-choice' in action['availableActions']:
            await self.take_gamble_win()
        if 'availableActions' in action and 'mm-bonus-game-choice' in action['availableActions']:
            await self.take_bonus_win()
    def spin_payload(self, bet, action='mm-spin'):
        return{
            'action': action,
            'minimumGambleMultiplier': self.min_gamble_multi,
            'bet': bet,
            'fundId': None,
            'gambleEnabled': self.gamble_enabled
        }
    
    def gamble_payload(self, option = 0):
        return {
            'action': 'mm-money-gamble-choice',
            'option': option
        }

    def choice_bonus_payload(self, option = 0):
        return {
            'action': 'mm-bonus-game-choice',
            'option': option
        }
    async def take_gamble_win(self):
        payload = self.gamble_payload(0) # take win
        res = await pushgaming_http.post_action(
            action_url=self.action_url, payload=payload, session_id=self.session_id)
        return res

    async def take_bonus_win(self):
        payload = self.choice_bonus_payload(0) # take win
        res = await pushgaming_http.post_action(
            action_url=self.action_url, payload=payload, session_id=self.session_id)
        return res
    async def handle_response(self, r, bet):
        if 'occurrenceId' in r:
            if 'details' in r and 'code' in r['details'] and 'last_action_is_not_completed' in r['details']['code']:
                action_id = r['details']['actionId'][0]
                return await self.complete_action(action_id, round_over=True)
            else:
                log.error(r)
                raise Exception(r)
        actions = r['actions']
        action = actions[-1]
        if 'actionComplete' in action and action['actionComplete']  == False:
            action_id = action['actionId']
            await self.complete_action(action_id, round_over=True)
        if 'availableActions' in action and 'mm-money-gamble-choice' in action['availableActions']:
            await self.take_gamble_win()
        if 'availableActions' in action and 'mm-bonus-game-choice' in action['availableActions']:
            await self.take_bonus_win()
        win = action['cumulativeWin'] if 'cumulativeWin' in action else None
        self.log_message(bet, win)

    def log_message(self, bet, win):
        log_msg = '\t'.join(
            [f'Bet - ${bet/100:.2f}', f'Win - ${win/100:.2f}', f'{win/bet:.2f}x'])
        log.info(log_msg)
