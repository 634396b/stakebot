from core.DiceSlot import DiceSlot

class DiceChallenge:
  def start(self, user, price_mgr, currency, target_result):
    self.game = DiceSlot()
    pay_multi, data = self.game.bet(user=user, price_mgr=price_mgr, bet=float(0), currency=currency)
    result = self.game.get_result(data)
    if result == target_result:
      return True
    