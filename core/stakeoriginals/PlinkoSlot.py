from core.stakeoriginals.BaseSlot import BaseSlot
from core.http.stake import bet_plinko


class PlinkoSlot(BaseSlot):
    volitility = 0.5
    response_prop = 'plinkoBet'
    rows = 16
    risk = 'high'
    def __init__(self, rows = 16, risk = 'high'):
        self.rows = rows
        self.risk = risk

    def bet_fn(self, **kwargs):
        return bet_plinko(**kwargs)

    def get_args(self):
        return {'rows': self.rows, 'risk': self.risk}
