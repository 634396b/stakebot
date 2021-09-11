from core.stakeoriginals.BaseSlot import BaseSlot
import core.http.stake as stake_http

import random


class ScarabSlot(BaseSlot):
    volitility = 0.5
    response_prop = 'slotsBet'

    def bet_fn(self, **kwargs):
        return stake_http.bet_scarab(**kwargs)

    def get_args(self):
        lines = random.randint(1, 20)

        return {'lines': lines}
