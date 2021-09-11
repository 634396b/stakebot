import uuid
from time import time
from core.http.util import async_get

netent_headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,pt;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "pragma": "no-cache",
    'origin': 'https://softswiss-static.casinomodule.com',
    "sec-ch-ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"92\"",
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}


def netent_init(sessid, game_id):
    qs = f'action=init&sessid={sessid}&gameId={game_id}&wantsfreerounds=true&freeroundmode=false&wantsreels=true&no-cache={time()}'
    url = f'https://softswiss-api.casinomodule.com/servlet/CasinoGameServlet;jsession={sessid}?' + qs
    return async_get(url, headers=netent_headers)


def do_netent_spin(sess_id, game_id, bet_level, bet_denom, bet_lines):
    qs = f'action=spin&sessid={sess_id}&gameId={game_id}&wantsreels=true&wantsfreerounds=true&freeroundmode=false&bet.betlevel={bet_level}&bet.denomination={bet_denom}&bet.betlines={bet_lines}&no-cache={uuid.uuid4()}'
    url = f'https://softswiss-api.casinomodule.com/servlet/CasinoGameServlet;jsession={sess_id}?' + qs
    return async_get(url, headers=netent_headers)


def scudamore_select_horse(sess_id, game_id, horse_idx):
    qs = f'action=selecthorse&sessid={sess_id}&gameId={game_id}&wantsreels=true&wantsfreerounds=true&freeroundmode=false&freespins.horse.selected={horse_idx}&no-cache={uuid.uuid4()}'
    url = f'https://softswiss-api.casinomodule.com/servlet/CasinoGameServlet;jsession={sess_id}?' + qs
    return async_get(url, headers=netent_headers)


def schudamore_do_free_spin(sess_id, game_id):
    qs = f'action=freespin&sessid={sess_id}&gameId={game_id}&wantsreels=true&wantsfreerounds=true&freeroundmode=false&no-cache={uuid.uuid4()}'
    url = f'https://softswiss-api.casinomodule.com/servlet/CasinoGameServlet;jsession={sess_id}?' + qs
    return async_get(url, headers=netent_headers)

