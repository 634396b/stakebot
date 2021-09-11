from core.stakeoriginals.BaseSlot import BaseSlot
import core.http.stake as stake_http

import random


class KenoSlot(BaseSlot):
    volitility = 0.5
    response_prop = 'kenoBet'

    def bet_fn(self, **kwargs):
        return stake_http.bet_keno(**kwargs)

    def get_args(self):
        self.risk = 'high'
        self.numbers = random.sample(range(40), random.randint(4,10))

        return {'risk': self.risk, 'numbers': self.numbers}
