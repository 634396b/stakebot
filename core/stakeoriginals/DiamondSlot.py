from core.stakeoriginals.BaseSlot import BaseSlot
import core.http.stake as stake_http


class DiamondSlot(BaseSlot):
    # 0 to 1 scale which affects:
    #   * min_div and max_div spread ... bal/(min_div--max_div)
    #   *
    volitility = 0.5
    response_prop = 'diamondsBet'

    def bet_fn(self, **kwargs):
        return stake_http.bet_diamond(**kwargs)

    def get_args(self):
        return {}
