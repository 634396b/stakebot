from core.stakeoriginals.BaseSlot import BaseSlot
import core.http.stake as stake_http


class LimboSlot(BaseSlot):
    volitility = 0.5
    response_prop = 'limboBet'
    min_multi = int(1e1)
    max_multi = int(1e6)
    def bet_fn(self, **kwargs):
        return stake_http.bet_limbo(**kwargs)

    def get_args(self):
        target_multi = self.max_multi #random.randint(self.min_multi,self.max_multi)

        return {'target_multi': target_multi}
