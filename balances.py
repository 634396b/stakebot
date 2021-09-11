import asyncio
from core.Price import Price
from core.User import User
import core.http.stake as stake_http 
import stake_keys
import util
import logging
import sys
import json

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fhe = logging.FileHandler('logs/balances/balances_errors.log')
fh = logging.FileHandler('logs/balances/balances.log')
fhd = logging.StreamHandler(sys.stdout)

fhe.setLevel(logging.ERROR)
fh.setLevel(logging.DEBUG)
fhd.setLevel(logging.INFO)

log.addHandler(fhe)
log.addHandler(fh)
log.addHandler(fhd)


async def update_user(user: User, price_mgr: Price, should_print=False):
    await asyncio.sleep(0.1)
    try:
        resp = await stake_http.get_balance(user.key)
        util.check_response(resp)
        r = json.loads(resp)
        util.check_response(r)

        json_user = r['data']['user']
        balances = json_user['balances']
        user.name = json_user['name']
        for balance_obj in balances:
            available_currency = balance_obj['available']['currency']
            vault_currency = balance_obj['vault']['currency']

            available_balance = float(balance_obj['available']['amount'])
            vault_balance = float(balance_obj['vault']['amount'])
            if available_balance > 0 and should_print:
                try:
                    price = price_mgr.get_price(currency=available_currency)
                    log.info('\t'.join([f'{user.name}'.rjust(20),
                                        f'{available_currency}'.rjust(10),
                                        f'{available_balance:.8f}'.rjust(15),
                                        f'${available_balance*price:.4f}'.rjust(15)]))
                except:
                    pass
            if available_currency != vault_currency:
                raise Exception('cur != vault_cur',
                                available_currency, vault_currency)
            print(available_currency)
            try:
                user.get_bal(available_currency).set_bal(
                available_balance=available_balance, vault_balance=vault_balance)
            except Exception as e:
                log.error(e, exc_info=1)
    except Exception as e:
        log.error(e, exc_info=1)
    finally:
        return True

if __name__ == '__main__':
    keys = stake_keys.load_keys()
    for key in keys:
        update_user(pbals={}, init_bals={}, my_currency=None,
                    key=key, accs={}, price=None, should_print=True)
