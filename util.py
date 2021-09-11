import constants
from exceptions import SlotError
from atomicwrites import atomic_write
from datetime import date, datetime
import pytz
import aiohttp
import requests

def cur_date():
    return f'{date.strftime(datetime.now(tz=pytz.timezone("US/Eastern")), "%Y-%m-%d %I:%M %p %Z")}'


def write_chat(chat_message):
    f_n = f'logs/data/chat.txt'
    with open(f_n, 'r') as original:
        data = original.read()
    # Need to write atomically to prevent flickering
    with atomic_write(f_n, overwrite=True) as modified:
        modified.write('\n'.join(data.split('\n')[-30:]) + chat_message + '\n')


def write_logs(name, logs):
    f_n = f'logs/data/{name}.txt'
    header = ''.join(['Date'.center(20),
                      'Game'.center(20),
                      'Multiplier Win'.center(20),
                      'Bet Amount'.center(20),
                      'Payout'.center(21),
                      'Balance'.center(21),
                      'In Bonus?'.center(20),
                      ])
    with open(f_n, 'r') as original:
        data = original.read()
    # Need to write atomically to prevent flickering
    with atomic_write(f_n, overwrite=True) as modified:
        modified.write(header + '\n\n' + logs + '\n' +
                       '\n'.join(data.split('\n')[1:40*2]))


def write_errors(logs):
    with open('logs/data/errors.txt', 'a') as f:
        f.write(''.join(logs) + '\n')


def write_big_win_logs(logs):
    f_n = f'logs/data/big-wins.txt'
    header = ''.join(['Date'.center(20),
                      'Game'.center(20),
                      'Multiplier Win'.center(20),
                      'Bet'.center(15),
                      'Payout'.center(15),
                      ])
    with open(f_n, 'r') as original:
        data = original.read()
    # Need to write atomically to prevent flickering
    with atomic_write(f_n, overwrite=True) as modified:
        modified.write(header + '\n\n' + logs + '\n' +
                       '\n'.join(data.split('\n')[2:25]))


def write_totals_logs(logs):
    with open('logs/data/totals.txt', 'a') as f:
        f.write(''.join(logs) + '\n')


def write_tips_logs(logs):
    with open('logs/data/tips.txt', 'a') as f:
        f.write(''.join(logs) + '\n')


def write_bals(logs):
    with open('logs/data/bals.txt', 'a') as f:
        f.write(''.join(logs) + '\n')


def write_reload_logs(logs):
    with open('logs/data/reloads.txt', 'a') as f:
        f.write(''.join(logs).replace('\n', '') + '\n')


def slot_response(r, obj):
    if 'errors' in r:
        raise SlotError(r['errors'])
    data = r['data']
    pay_multi = float(data[obj]['payoutMultiplier'])
    active = data[obj]['active']
    payout = data[obj]['payout']
    amount = data[obj]['amount']
    return pay_multi, data, payout, amount


def check_response(r):
    if isinstance(r, aiohttp.ClientResponse) and r.status != 200:
        raise Exception(r.text())
    elif isinstance(r, requests.Response) and r.status_code != 200:
        raise Exception(r.text)
    elif isinstance(r, dict) and 'errors' in r:
        raise SlotError(r['errors'])

def is_big_win(pay_multi: float, bet_multi: float):
    bet_payout_percent = pay_multi/bet_multi
    return pay_multi >= constants.BIG_WIN_MULTI or bet_payout_percent > 1
