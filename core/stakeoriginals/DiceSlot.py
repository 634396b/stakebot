from core.stakeoriginals.BaseSlot import BaseSlot
import core.http.stake as stake_http

from datetime import datetime


class DiceSlot(BaseSlot):
    # 0 to 1 scale which affects:
    #   * min_div and max_div spread ... bal/(min_div--max_div)
    #   *
    volitility = 0.5
    response_prop = 'diceRoll'
    aob = 'below'
    target = 98
    
    def bet_fn(self, **kwargs):
        return stake_http.bet_dice(**kwargs)

    def get_args(self):
        return {'aob': self.aob, 'target': self.target}
     
     # Returns .2f number
    def get_result(self, data):
        return data[self.response_prop]['state']['result']

    def random_args(self):
        self.aob = 'above' if datetime.now().second % 4 == 0 else 'below'
        self.target = 2 if self.aob == 'above' else 98