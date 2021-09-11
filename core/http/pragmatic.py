from core.http.util import async_get, async_post, async_post_url_form
import json
import re

def get_headers(**kwargs):
  return {
      "accept": "*/*",
      "accept-language": "en-US,en;q=0.9,pt;q=0.8",
      "cache-control": "no-cache",
      "content-type": "application/json",
      "pragma": "no-cache",
      'origin': 'https://softswiss.pragmaticplay.net',
      "sec-ch-ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"92\"",
      "sec-ch-ua-mobile": "?0",
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "same-site",
      "sec-gpc": "1",
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
      **kwargs # Overwrite any parameters
  }



async def play_game(url):
    headers = get_headers()
    r = await async_get(url, headers=headers)
    # load player from location
    game_config_str = re.search("gameConfig: '(.+?)',", r).group(1)
    game_config = json.loads(game_config_str)
    return game_config

# spin
# action: doSpin
# symbol: vs1masterjoker
# c: 0.01 (coin prob)
# l: 1 (line)
# index: 3
# counter: 5
# repeat: 0
# mgckey:


def do_init(mgckey, url, symbol, index=1, cver=82703, repeat=0, counter=1):
    headers = get_headers(**{'content-type': 'application/x-www-form-urlencoded'})
    data = {'action': 'doInit', 'symbol': symbol, 'cver': cver,
            'index': index, 'counter': counter, 'repeat': repeat, 'mgckey': mgckey}
    return async_post_url_form(url, headers=headers, data=data)


def spin(mgckey, url, symbol, index, counter, credit, line, repeat, **kwargs):
    headers = get_headers(**{'content-type': 'application/x-www-form-urlencoded'})
    data = {'action': 'doSpin', 'symbol': symbol, 'c': credit, 'l': line, **kwargs,
            'index': index, 'counter': counter, 'repeat': repeat, 'mgckey': mgckey}
    return async_post_url_form(url, headers=headers, data=data)

# Communicates with stake to collect win

def collect_win(mgckey, url, symbol, index, counter, repeat):
    headers = get_headers(**{'content-type': 'application/x-www-form-urlencoded'})
    data = {'action': 'doCollect', 'symbol': symbol,
            'index': index, 'counter': counter, 'repeat': repeat, 'mgckey': mgckey}
    return async_post_url_form(url, headers=headers, data=data)


def reload_balance(mgckey):
    headers = get_headers(**{'content-type': 'application/x-www-form-urlencoded'})

    return async_get(f'https://softswiss.pragmaticplay.net/gs2c/reloadBalance.do?mgckey={mgckey}', headers=headers)
