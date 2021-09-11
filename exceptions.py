class BetTooBigException(Exception):
    pass

class ZeroBalanceException(Exception):
    pass

class SlotError(Exception):
    pass

class InBonusException(Exception):
    pass

# Min or max lines on a slot
class OutOfBoundsLinesException(Exception):
    pass

class NoMoneyException(Exception):
    pass

class UnhandledException(Exception):
    pass

class CaptchaException(Exception):
    pass

class InitCaptchaException(Exception):
    pass
