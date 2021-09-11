from core.stakeoriginals.BaseSlot import BaseSlot
import core.http.stake as stake_http

import util

from exceptions import SlotError


class SamSlot(BaseSlot):
    volitility = 0.5
    response_prop = 'slotsSamuraiBet'

    def handle_response(self, r, r_p, **kwargs):
        user = kwargs['user']
        util.check_response(r)
        re = r.json()
        try:
            pay_multi, data, payout, amount = util.slot_response(re, r_p)
            if data[r_p]['state']['nextSpinType'] != 'complete':
                b_pay_multi, b_data, b_payout, b_amount = self.claim_bonus(user.key)
                return float(b_pay_multi) + float(pay_multi), b_data, b_payout + payout, amount + b_amount
            else:
                return pay_multi, data, payout, amount
        except SlotError as e:
            if e.args[0][0]['errorType'] == 'existingGame':
                b_pay_multi, b_data, b_payout, b_amount = self.claim_bonus(user.key)
                return b_pay_multi, b_data, b_payout, b_amount

    def bet_fn(self, **kwargs):
        return stake_http.bet_sam(**kwargs)

    def get_args(self):
        return {}

    def claim_bonus(self, key):
        response_prop = 'slotsSamuraiNext'
        r = stake_http.sam_next(key)
        util.check_response(r)
        r = r.json()
        return util.slot_response(r, response_prop)