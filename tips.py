import balances
import util
import logging
import sys

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fhe = logging.FileHandler('logs/tips/tips_errors.log')
fh = logging.FileHandler('logs/tips/tips.log')
fhd = logging.StreamHandler(sys.stdout)

fhe.setLevel(logging.ERROR)
fh.setLevel(logging.DEBUG)
fhd.setLevel(logging.INFO)

log.addHandler(fhd)
log.addHandler(fh)
log.addHandler(fhe)


def spread_balances(keys, accs, pbals, my_currency, price):
    pass
#TODO UPDATE
    # balance_sums = balances.get_balance_sums(keys=keys, pbals=pbals)
    # bal_per_user = balance_sums/len(keys)
    # for key in keys:
    #     # Account shall be past average tips lower accounts
    #     if pbals[key] < bal_per_user:
    #         continue
    #     for key2 in keys:
    #         if key2 == key:  # Same account
    #             continue
    #         # Recheck both balances because their balances change after tipping
    #         if pbals[key2] < bal_per_user and pbals[key] > bal_per_user:
    #             need_to_tip = abs(bal_per_user - pbals[key2])
    #             if need_to_tip > 0 and need_to_tip >= 0.001:
    #                 logs = '\t'.join([
    #                     f'{str(datetime.utcnow())}'.rjust(20),
    #                     'From',
    #                     accs[key].rjust(15),
    #                     'Sending tip to',
    #                     accs[key2].rjust(15),
    #                     f'{need_to_tip:.4f}'.center(10),
    #                     f'${need_to_tip*price:.4f}'.rjust(10)])
    #                 log.info(logs)
    #                 r = stake_http.send_tip(
    #                     key=key, to=accs[key2], currency=my_currency, amt=need_to_tip)
    #                 util.check_response(r)
    #                 if 'errors' in r:
    #                     log.error(str(r['errors']))
    #                 else:
    #                     pbals[key] -= need_to_tip
    #                     pbals[key2] += need_to_tip
