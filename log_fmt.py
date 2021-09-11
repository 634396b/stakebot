from core.User import User
from datetime import datetime, date
import pytz
# def fmt_user_data(user: User, price_mgr):
#     return '\t'.join([
#         f'{date.strftime(datetime.now(tz=pytz.timezone("US/Eastern")), "%Y-%m-%d %I:%M %p")}'.rjust(20),
#         f'{user.name}'.rjust(15),
#         f'{user.bal.amt:.6f}'.rjust(15),
#         f'{user.bal.currency}'.center(10),
#         f'${user.bal.usd(price):.4f}'.center(10)
#     ])


def fmt_totals_data(balance_sum, currency, price):
    return '\t'.join([
        f'{date.strftime(datetime.now(tz=pytz.timezone("US/Eastern")), "%Y-%m-%d %I:%M %p %Z")}'.rjust(20),
        'Total On All Accounts',
        f'{balance_sum:.6f}'.rjust(10),
        f'{currency}'.center(10),
        f'${balance_sum*price:.6f}'.rjust(10)
    ])


def fmt_spin(name, pay_multi, game, bet_multi, bal, amount, payout, price, *args, **kwargs):
    c = ' '
    extra_kwargs = [f'{arg}'.rjust(15, c)
                    for arg in kwargs.values()] if kwargs else []
    extra_args = [f'{arg}'.rjust(15,c) for arg in args.values()] if args else []

    game = 'Blue Samurai' if game=='slotsSamuraiBet' else game
    game = 'Scarab Spin' if game=='slotsBet' else game

    arr_logs = [
        f'{date.strftime(datetime.now(tz=pytz.timezone("US/Eastern")), "%d %b %I:%M:%S %p %Z")}'.center(20, c),
        # f'{name}'.center(18, '\t'),
        f'{game.replace("Bet","").title()}'.center(20, c),
        f'{float(pay_multi):.2f}x'.center(20, c),
        # f'/{int(bet_multi)}'.center(10),
        # f'{(float(pay_multi)/float(bet_multi))*100:.2f}%'.center(10, '\t'),
        # f'{float(bal):.2e}'.center(10),
        # f'${float(bal)*price:.8f}'.center(10),
        # f'{float(amount):.8f}'.center(15, c),
        f'${float(amount)*price:.6f}'.center(15, c),
        # f'{float(payout):.8f}'.center(15),
        f'${float(payout)*price:.6f}'.center(15),
        # f'{seed}'.center(15, c),
        # *extra_kwargs,
        # *extra_args,
    ]
    str_logs = ''.join(arr_logs)
    return arr_logs, str_logs
