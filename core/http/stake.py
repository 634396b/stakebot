import secrets
from core.http.util  import async_post
from constants import STAKE_GQL_ENDPOINT

def get_headers(key):
    return {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,pt;q=0.8",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "pragma": "no-cache",
        "x-access-token": key,
        "x-language": "en",
        "x-lockdown-token": "",
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1'
    }


def sam_next(key):
    data = {"operationName": "slotsSamuraiNext", "variables": {},
            "query": "mutation slotsSamuraiNext($identifier: String) {\n  slotsSamuraiNext(identifier: $identifier) {\n    ...CasinoBetFragment\n    state {\n      ...SamuraiSlotsStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment SamuraiSlotsStateFragment on CasinoGameSlotsSamurai {\n  nextSpinType\n  bonusSpinsRemaining\n  rounds {\n    id\n    type\n    data {\n      ... on CasinoGameSlotsSamuraiRegularSpin {\n        spinMultiplier\n        roundMultiplier\n        view\n        paylines {\n          payline\n          count\n          symbol\n          multiplier\n          __typename\n        }\n        __typename\n      }\n      ... on CasinoGameSlotsSamuraiSpecialSpin {\n        spinMultiplier\n        roundMultiplier\n        view\n        roundWins {\n          x\n          y\n          __typename\n        }\n        spinWins {\n          x\n          y\n          __typename\n        }\n        __typename\n      }\n      ... on CasinoGameSlotsSamuraiBonusSpin {\n        spinMultiplier\n        roundMultiplier\n        view\n        paylines {\n          payline\n          count\n          symbol\n          multiplier\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"}
    headers = get_headers(key)
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def bet_scarab(key, bet=0, lines=20, currency='ltc'):
    headers = get_headers(key)
    data = {"operationName": "slotBet", "variables": {"currency": currency, "amount": bet, "lines": lines, "identifier": secrets.token_hex(10)},
            "query": "mutation slotBet($amount: Float!, $lines: Int!, $currency: CurrencyEnum!, $identifier: String!) {\n  slotsBet(amount: $amount, currency: $currency, lines: $lines, identifier: $identifier) {\n    ...CasinoBetFragment\n    state {\n      ...SlotsStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment SlotsStateFragment on CasinoGameSlots {\n  lines\n  rounds {\n    offsets\n    paylines {\n      payline\n      hits\n      multiplier\n      symbol\n      __typename\n    }\n    scatterMultiplier\n    roundMultiplier\n    totalMultiplier\n    bonusRemaining\n    bonusTotal\n    __typename\n  }\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def bet_sam(key, bet=0, currency='ltc'):
    headers = get_headers(key)
    data = {"operationName": "slotsSamuraiBet", "variables": {"currency": currency, "amount": bet, "identifier": secrets.token_hex(10)}, "query": "mutation slotsSamuraiBet($amount: Float!, $currency: CurrencyEnum!, $identifier: String) {\n  slotsSamuraiBet(amount: $amount, currency: $currency, identifier: $identifier) {\n    ...CasinoBetFragment\n    state {\n      ...SamuraiSlotsStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment SamuraiSlotsStateFragment on CasinoGameSlotsSamurai {\n  nextSpinType\n  bonusSpinsRemaining\n  rounds {\n    id\n    type\n    data {\n      ... on CasinoGameSlotsSamuraiRegularSpin {\n        spinMultiplier\n        roundMultiplier\n        view\n        paylines {\n          payline\n          count\n          symbol\n          multiplier\n          __typename\n        }\n        __typename\n      }\n      ... on CasinoGameSlotsSamuraiSpecialSpin {\n        spinMultiplier\n        roundMultiplier\n        view\n        roundWins {\n          x\n          y\n          __typename\n        }\n        spinWins {\n          x\n          y\n          __typename\n        }\n        __typename\n      }\n      ... on CasinoGameSlotsSamuraiBonusSpin {\n        spinMultiplier\n        roundMultiplier\n        view\n        paylines {\n          payline\n          count\n          symbol\n          multiplier\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def bet_plinko(key='', rows=16, risk='high', bet=0, currency='ltc'):
    headers = get_headers(key)
    data = {"operationName": "PlinkoBet", "variables": {"currency": currency, "amount": bet, "rows": rows, "risk": risk, "identifier": secrets.token_hex(10)},
            "query": "mutation PlinkoBet($amount: Float!, $currency: CurrencyEnum!, $risk: CasinoGamePlinkoRiskEnum!, $rows: Int!, $identifier: String!) {\n  plinkoBet(amount: $amount, currency: $currency, risk: $risk, rows: $rows, identifier: $identifier) {\n    ...CasinoBetFragment\n    state {\n      ...PlinkoStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment PlinkoStateFragment on CasinoGamePlinko {\n  risk\n  rows\n  point\n  path\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def get_balance(key):
    headers = get_headers(key)
    data = {"operationName": "initialUserRequest", "variables": {}, "query": "query initialUserRequest {\n  user {\n    ...UserAuth\n    __typename\n  }\n}\n\nfragment UserAuth on User {\n  id\n  name\n  email\n  hasPhoneNumberVerified\n  hasEmailVerified\n  hasPassword\n  intercomHash\n  createdAt\n  hasTfaEnabled\n  mixpanelId\n  hasOauth\n  isKycBasicRequired\n  isKycExtendedRequired\n  isKycFullRequired\n  kycBasic {\n    id\n    status\n    __typename\n  }\n  kycExtended {\n    id\n    status\n    __typename\n  }\n  kycFull {\n    id\n    status\n    __typename\n  }\n  flags {\n    flag\n    __typename\n  }\n  roles {\n    name\n    __typename\n  }\n  balances {\n    ...UserBalanceFragment\n    __typename\n  }\n  activeClientSeed {\n    id\n    seed\n    __typename\n  }\n  previousServerSeed {\n    id\n    seed\n    __typename\n  }\n  activeServerSeed {\n    id\n    seedHash\n    nextSeedHash\n    nonce\n    blocked\n    __typename\n  }\n  __typename\n}\n\nfragment UserBalanceFragment on UserBalance {\n  available {\n    amount\n    currency\n    __typename\n  }\n  vault {\n    amount\n    currency\n    __typename\n  }\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def reward_meta(key, currency='ltc'):
    headers = get_headers(key)
    data = {"operationName": "ClaimReloadMeta", "variables": {"currency": currency},
            "query": "query ClaimReloadMeta($currency: CurrencyEnum!) {\n  user {\n    id\n    flags {\n      flag\n      __typename\n    }\n    flagProgress {\n      flag\n      __typename\n    }\n    reload: faucet {\n      id\n      amount(currency: $currency)\n      active\n      claimInterval\n      lastClaim\n      expireAt\n      createdAt\n      updatedAt\n      __typename\n    }\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def bet_diamond(key, bet, currency='ltc'):
    headers = get_headers(key)
    data = {"operationName": "DiamondsBet", "variables": {"amount": bet, "currency": currency, "identifier": secrets.token_hex(10)},
            "query": "mutation DiamondsBet($amount: Float!, $currency: CurrencyEnum!, $identifier: String) {\n  diamondsBet(amount: $amount, currency: $currency, identifier: $identifier) {\n    ...CasinoBetFragment\n    state {\n      ...DiamondsStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment DiamondsStateFragment on CasinoGameDiamonds {\n  hand\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def bet_dice(key, bet, target, aob, currency='ltc'):
    headers = get_headers(key)
    data = {"operationName": "DiceRoll", "variables": {"target": target, "condition": aob, "identifier": secrets.token_hex(10), "amount": bet, "currency": currency},
            "query": "mutation DiceRoll($amount: Float!, $target: Float!, $condition: CasinoGameDiceConditionEnum!, $currency: CurrencyEnum!, $identifier: String!) {\n  diceRoll(amount: $amount, target: $target, condition: $condition, currency: $currency, identifier: $identifier) {\n    ...CasinoBetFragment\n    state {\n      ...DiceStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment DiceStateFragment on CasinoGameDice {\n  result\n  target\n  condition\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def bet_keno(key, bet, numbers, risk, currency='ltc'):
    headers = get_headers(key)
    # 0 to 39
    # 10 numbers
    data = {"operationName": "KenoBet", "variables": {"numbers": numbers, "risk": risk, "amount": bet, "currency": currency, "identifier": secrets.token_hex(
        10)}, "query": "mutation KenoBet($amount: Float!, $currency: CurrencyEnum!, $numbers: [Int!]!, $identifier: String!, $risk: CasinoGameKenoRiskEnum) {\n  kenoBet(amount: $amount, currency: $currency, numbers: $numbers, risk: $risk, identifier: $identifier) {\n    ...CasinoBetFragment\n    state {\n      ...KenoStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment KenoStateFragment on CasinoGameKeno {\n  drawnNumbers\n  selectedNumbers\n  risk\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def bet_limbo(key, bet, target_multi, currency='ltc'):
    headers = get_headers(key)
    data = {"operationName": "LimboBet", "variables": {"amount": bet, "currency": currency, "identifier": secrets.token_hex(
        10), "multiplierTarget": target_multi}, "query": "mutation LimboBet($amount: Float!, $multiplierTarget: Float!, $currency: CurrencyEnum!, $identifier: String!) {\n  limboBet(amount: $amount, currency: $currency, multiplierTarget: $multiplierTarget, identifier: $identifier) {\n    ...CasinoBetFragment\n    state {\n      ...LimboStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment LimboStateFragment on CasinoGameLimbo {\n  result\n  multiplierTarget\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def claim_rewards(key, captcha, currency='ltc'):
    headers = get_headers(key)
    data = {"operationName": "ClaimReload", "variables": {"currency": currency, "captcha": captcha},
            "query": "mutation ClaimReload($currency: CurrencyEnum!, $captcha: String!) {\n  claimReload: claimFaucet(currency: $currency, captcha: $captcha) {\n    reload: faucet {\n      user {\n        id\n        reload: faucet {\n          id\n          amount(currency: $currency)\n          active\n          claimInterval\n          lastClaim\n          expireAt\n          createdAt\n          updatedAt\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def get_tip_meta(key, user):
    headers = get_headers(key)
    data = {"operationName": "SendTipMeta", "variables": {"name": user},
            "query": "query SendTipMeta($name: String) {\n  user(name: $name) {\n    id\n    name\n    __typename\n  }\n  self: user {\n    id\n    hasTfaEnabled\n    isTfaSessionValid\n    balances {\n      available {\n        amount\n        currency\n        __typename\n      }\n      vault {\n        amount\n        currency\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


async def send_tip(key, to, currency, amt=0, user_id=None):
    headers = get_headers(key)
    if not user_id:
        user_id = json.loads(await get_tip_meta(key, to))['data']['user']['id']

    data = {"operationName": "SendTip", "variables": {"name": to, "amount": amt, "isPublic": False, "userId": user_id, "chatId": "f0326994-ee9e-411c-8439-b4997c187b95", "currency": currency},
            "query": "mutation SendTip($userId: String!, $amount: Float!, $currency: CurrencyEnum!, $isPublic: Boolean, $chatId: String!, $tfaToken: String) {\n  sendTip(userId: $userId, amount: $amount, currency: $currency, isPublic: $isPublic, chatId: $chatId, tfaToken: $tfaToken) {\n    id\n    amount\n    currency\n    user {\n      id\n      name\n      __typename\n    }\n    sendBy {\n      id\n      name\n      balances {\n        available {\n          amount\n          currency\n          __typename\n        }\n        vault {\n          amount\n          currency\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def vip_nav_meta(key):
    headers = get_headers(key)
    data = {"operationName": "VipNavMeta", "variables": {}, "query": "query VipNavMeta {\n  user {\n    id\n    faucet {\n      active\n      __typename\n    }\n    rakeback {\n      enabled\n      __typename\n    }\n    flags {\n      flag\n      __typename\n    }\n    activeRollovers {\n      id\n      __typename\n    }\n    __typename\n  }\n  activeRaffles {\n    id\n    endTime\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def claim_bonus(key, code, captcha, currency='ltc'):
    headers = get_headers(key)
    data = {"operationName": "ClaimBonusCode", "variables": {"code": code, "currency": currency, "captcha": captcha},
            "query": "mutation ClaimBonusCode($code: String!, $currency: CurrencyEnum!, $captcha: String!) {\n  claimBonusCode(code: $code, currency: $currency, captcha: $captcha) {\n    bonusCode {\n      id\n      code\n      __typename\n    }\n    amount\n    currency\n    user {\n      id\n      balances {\n        available {\n          amount\n          currency\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    redeemed\n    __typename\n  }\n}\n"}

    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)

# errors.[]
#   .path.[""]
#   .message
#   .errorType


def claim_rakeback(key):
    headers = get_headers(key)
    data = {"operationName": "ClaimRakeback", "variables": {
    }, "query": "mutation ClaimRakeback {\n  claimRakeback {\n    id\n    currency\n    amount\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)

# data.user.rakeback.balances.[]
#   .currency
#   .amount


def available_rakeback(key):
    headers = get_headers(key)
    data = {"operationName": "AvailableRakeback", "variables": {
    }, "query": "query AvailableRakeback {\n  user {\n    id\n    rakeback {\n      balances {\n        currency\n        amount: availableAmount\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


# data.requestWebSocketChallenge
#   .challenge
#   .key
def req_ws_challenge(key):
    headers = get_headers(key)
    data = {"operationName": "requestWebSocketChallenge", "variables": {
    }, "query": "mutation requestWebSocketChallenge {\n  requestWebSocketChallenge {\n    challenge\n    key\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)

# data.publicChats.[]
#   .id
#   .isPublic
#   .name


def public_chats(key):
    headers = get_headers(key)
    data = {"operationName": "PublicChats", "variables": {
    }, "query": "query PublicChats {\n  publicChats {\n    id\n    name\n    isPublic\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def send_message(key, chat_id, message=':umbrella:'):
    if len(message) > 20 or not chat_id:
        raise Exception(message, chat_id)
    headers = get_headers(key)
    data = {"operationName": "SendMessage", "variables": {"chatId": chat_id, "message": message},
            "query": "mutation SendMessage($chatId: String!, $message: String!) {\n  sendMessage(chatId: $chatId, message: $message) {\n    id\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def user_statistics(key, name):
    headers = get_headers(key)
    data = {"operationName": "UserStatistics", "variables": {"name": name},
            "query": "query UserStatistics($name: String) {\n  user(name: $name) {\n    id\n    statistic {\n      bets\n      game\n      wins\n      losses\n      ties\n      betAmount\n      currency\n      __typename\n    }\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def house_bet_list(key, offset=0, limit=50):
    if offset > 1000:
        raise Exception('Offset shall be <= 1000')
    if limit > 50:
        raise Exception('Limit shall be <= 50')
    headers = get_headers(key)
    data = {"operationName": "houseBetList", "variables": {"offset": offset, "limit": limit},
            "query": "query houseBetList($offset: Int = 0, $limit: Int = 10, $game: BetHouseEnum, $name: String) {\n  user(name: $name) {\n    id\n    houseBetList(offset: $offset, limit: $limit, game: $game) {\n      ...BetFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment BetFragment on Bet {\n  id\n  iid\n  type\n  scope\n  game {\n    name\n    icon\n    __typename\n  }\n  bet {\n    ... on CasinoBet {\n      ...CasinoBetFragment\n      __typename\n    }\n    ... on MultiplayerCrashBet {\n      ...MultiplayerCrashBet\n      __typename\n    }\n    ... on MultiplayerSlideBet {\n      ...MultiplayerSlideBet\n      __typename\n    }\n    ... on SoftswissBet {\n      ...SoftswissBet\n      __typename\n    }\n    ... on SportBet {\n      ...SportBet\n      __typename\n    }\n    ... on EvolutionBet {\n      ...EvolutionBet\n      __typename\n    }\n    ... on PlayerPropBet {\n      ...PlayerPropBetFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment MultiplayerCrashBet on MultiplayerCrashBet {\n  id\n  user {\n    id\n    name\n    __typename\n  }\n  payoutMultiplier\n  gameId\n  amount\n  payout\n  currency\n  result\n  updatedAt\n  cashoutAt\n  btcAmount: amount(currency: btc)\n  __typename\n}\n\nfragment MultiplayerSlideBet on MultiplayerSlideBet {\n  id\n  user {\n    id\n    name\n    __typename\n  }\n  payoutMultiplier\n  gameId\n  amount\n  payout\n  currency\n  slideResult: result\n  updatedAt\n  cashoutAt\n  btcAmount: amount(currency: btc)\n  active\n  createdAt\n  __typename\n}\n\nfragment SoftswissBet on SoftswissBet {\n  id\n  amount\n  currency\n  updatedAt\n  payout\n  payoutMultiplier\n  user {\n    id\n    name\n    __typename\n  }\n  softswissGame: game {\n    id\n    name\n    edge\n    extId\n    provider {\n      id\n      name\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SportBet on SportBet {\n  id\n  amount\n  active\n  currency\n  status\n  payoutMultiplier\n  potentialMultiplier\n  cashoutMultiplier\n  payout\n  createdAt\n  user {\n    id\n    name\n    __typename\n  }\n  outcomes {\n    odds\n    status\n    outcome {\n      id\n      name\n      active\n      odds\n      __typename\n    }\n    market {\n      ...MarketFragment\n      fixture {\n        id\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    fixture {\n      ...FixturePreviewFragment\n      __typename\n    }\n    __typename\n  }\n  adjustments {\n    id\n    payoutMultiplier\n    updatedAt\n    createdAt\n    __typename\n  }\n  __typename\n}\n\nfragment MarketFragment on SportMarket {\n  id\n  name\n  status\n  extId\n  specifiers\n  outcomes {\n    id\n    active\n    name\n    odds\n    __typename\n  }\n  __typename\n}\n\nfragment FixturePreviewFragment on SportFixture {\n  id\n  extId\n  status\n  slug\n  marketCount(status: [active, suspended])\n  data {\n    ...FixtureDataMatchFragment\n    ...FixtureDataOutrightFragment\n    __typename\n  }\n  eventStatus {\n    ...FixtureEventStatus\n    __typename\n  }\n  tournament {\n    ...TournamentTreeFragment\n    __typename\n  }\n  ...LiveStreamExistsFragment\n  __typename\n}\n\nfragment FixtureDataMatchFragment on SportFixtureDataMatch {\n  startTime\n  competitors {\n    ...CompetitorFragment\n    __typename\n  }\n  __typename\n}\n\nfragment CompetitorFragment on SportFixtureCompetitor {\n  name\n  extId\n  countryCode\n  abbreviation\n  __typename\n}\n\nfragment FixtureDataOutrightFragment on SportFixtureDataOutright {\n  name\n  startTime\n  endTime\n  __typename\n}\n\nfragment FixtureEventStatus on SportFixtureEventStatus {\n  homeScore\n  awayScore\n  matchStatus\n  clock {\n    matchTime\n    remainingTime\n    __typename\n  }\n  periodScores {\n    homeScore\n    awayScore\n    matchStatus\n    __typename\n  }\n  currentServer {\n    extId\n    __typename\n  }\n  homeGameScore\n  awayGameScore\n  statistic {\n    yellowCards {\n      away\n      home\n      __typename\n    }\n    redCards {\n      away\n      home\n      __typename\n    }\n    corners {\n      home\n      away\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment TournamentTreeFragment on SportTournament {\n  id\n  name\n  slug\n  category {\n    id\n    name\n    slug\n    sport {\n      id\n      name\n      slug\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment LiveStreamExistsFragment on SportFixture {\n  abiosStream {\n    exists\n    __typename\n  }\n  betradarStream {\n    exists\n    __typename\n  }\n  diceStream {\n    exists\n    __typename\n  }\n  __typename\n}\n\nfragment EvolutionBet on EvolutionBet {\n  id\n  amount\n  currency\n  createdAt\n  payout\n  payoutMultiplier\n  user {\n    id\n    name\n    __typename\n  }\n  softswissGame: game {\n    id\n    name\n    edge\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropBetFragment on PlayerPropBet {\n  active\n  amount\n  cashoutMultiplier\n  createdAt\n  currency\n  id\n  lineType\n  odds\n  payout\n  payoutMultiplier\n  updatedAt\n  status\n  user {\n    id\n    name\n    __typename\n  }\n  playerPropLine {\n    ...PlayerPropLineFragment\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropLineFragment on PlayerPropLine {\n  id\n  line\n  over\n  under\n  suspended\n  balanced\n  name\n  player {\n    id\n    name\n    __typename\n  }\n  market {\n    id\n    stat {\n      name\n      value\n      __typename\n    }\n    game {\n      id\n      fixture {\n        id\n        name\n        data {\n          ... on SportFixtureDataMatch {\n            competitors {\n              ...CompetitorFragment\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              name\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def create_vault_deposit(key, amt, currency):
    if not amt or not currency:
        raise Exception(f'!amt {str(amt)} || !currency {str(currency)}')
    headers = get_headers(key)
    data = {"operationName": "CreateVaultDeposit", "variables": {"currency": currency, "amount": amt},
            "query": "mutation CreateVaultDeposit($amount: Float!, $currency: CurrencyEnum!) {\n  createVaultDeposit(amount: $amount, currency: $currency) {\n    id\n    amount\n    currency\n    user {\n      id\n      balances {\n        available {\n          amount\n          currency\n          __typename\n        }\n        vault {\n          amount\n          currency\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def create_vault_withdrawl(key, amt, currency, pw):
    if not amt or not currency or not pw:
        raise Exception(f'!amt {str(amt)} || !currency {str(currency)}')
    headers = get_headers(key)
    data = {"operationName": "CreateVaultWithdrawal", "variables": {"amount": amt, "password": pw, "currency": currency},
            "query": "mutation CreateVaultWithdrawal($amount: Float!, $currency: CurrencyEnum!, $password: String, $tfaToken: String, $oauthToken: String) {\n  createVaultWithdrawal(amount: $amount, currency: $currency, password: $password, tfaToken: $tfaToken, oauthToken: $oauthToken) {\n    id\n    currency\n    amount\n    user {\n      id\n      hasEmailVerified\n      email\n      balances {\n        ...UserBalanceFragment\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment UserBalanceFragment on UserBalance {\n  available {\n    amount\n    currency\n    __typename\n  }\n  vault {\n    amount\n    currency\n    __typename\n  }\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def rot_seed(key, seed=None):
    seed = secrets.token_hex(16) if seed is None else seed
    headers = get_headers(key)
    data = {"operationName": "RotateSeedPair", "variables": {"seed": seed},
            "query": "mutation RotateSeedPair($seed: String!) {\n  rotateSeedPair(seed: $seed) {\n    clientSeed {\n      user {\n        id\n        activeClientSeed {\n          id\n          seed\n          __typename\n        }\n        activeServerSeed {\n          id\n          nonce\n          seedHash\n          nextSeedHash\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def bet_mines(key, amt, fields, mines_count, currency):
    headers = get_headers(key)
    data = {"operationName": "MinesBet", "variables": {"amount": amt, "currency": currency, "identifier": secrets.token_hex(
        10), "minesCount": mines_count, "fields": fields}, "query": "mutation MinesBet($amount: Float!, $currency: CurrencyEnum!, $minesCount: Int!, $fields: [Int!], $identifier: String) {\n  minesBet(amount: $amount, currency: $currency, minesCount: $minesCount, fields: $fields, identifier: $identifier) {\n    ...CasinoBetFragment\n    state {\n      ...MinesStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment MinesStateFragment on CasinoGameMines {\n  mines\n  minesCount\n  rounds {\n    field\n    payoutMultiplier\n    __typename\n  }\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def video_poker_bet(key, amt, currency):
    headers = get_headers(key)
    data = {"operationName": "VideoPokerBet", "variables": {"currency": currency, "amount": amt},
            "query": "mutation VideoPokerBet($amount: Float!, $currency: CurrencyEnum!) {\n  videoPokerBet(amount: $amount, currency: $currency) {\n    ...CasinoBetFragment\n    state {\n      ...VideoPokerStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment VideoPokerStateFragment on CasinoGameVideoPoker {\n  playerHand {\n    suit\n    rank\n    __typename\n  }\n  initialHand {\n    suit\n    rank\n    __typename\n  }\n  handResult\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def video_poker_next(key, held):
    headers = get_headers(key)
    data = {"operationName": "VideoPokerNext", "variables": {"held": held, "identifier": secrets.token_hex(
        10)}, "query": "mutation VideoPokerNext($held: [VideoPokerNextHeldInput]!, $identifier: String!) {\n  videoPokerNext(held: $held, identifier: $identifier) {\n    ...CasinoBetFragment\n    state {\n      ...VideoPokerStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment VideoPokerStateFragment on CasinoGameVideoPoker {\n  playerHand {\n    suit\n    rank\n    __typename\n  }\n  initialHand {\n    suit\n    rank\n    __typename\n  }\n  handResult\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)

# start_card = {suit, rank}


def hilo_start(key, start_card, amt, currency):
    headers = get_headers(key)
    data = {"operationName": "HiloBet", "variables": {"currency": currency, "amount": amt, "startCard": start_card},
            "query": "mutation HiloBet($amount: Float!, $currency: CurrencyEnum!, $startCard: HiloBetStartCardInput!) {\n  hiloBet(amount: $amount, currency: $currency, startCard: $startCard) {\n    ...CasinoBetFragment\n    state {\n      ...HiloStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment HiloStateFragment on CasinoGameHilo {\n  startCard {\n    suit\n    rank\n    __typename\n  }\n  rounds {\n    card {\n      suit\n      rank\n      __typename\n    }\n    guess\n    payoutMultiplier\n    __typename\n  }\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def hilo_next(key, guess):
    headers = get_headers(key)
    data = {"operationName": "HiloNext", "variables": {"guess": guess}, "query": "mutation HiloNext($guess: CasinoGameHiloGuessEnum!) {\n  hiloNext(guess: $guess) {\n    ...CasinoBetFragment\n    state {\n      ...HiloStateFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment HiloStateFragment on CasinoGameHilo {\n  startCard {\n    suit\n    rank\n    __typename\n  }\n  rounds {\n    card {\n      suit\n      rank\n      __typename\n    }\n    guess\n    payoutMultiplier\n    __typename\n  }\n  __typename\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def slug_kurator_group(key, limit=50, filter_ids=[], offset=0, sort="userCount", slug="slots", show_providers=True, show_games=True):
    data = {"operationName": "SlugKuratorGroup", "variables": {"showGames": show_games, "sort": "userCount", sort: show_providers, "slug": slug,
                                                               "limit": limit, "filterIds": filter_ids, "offset": offset},
            "query": "query SlugKuratorGroup($slug: String!, $limit: Int!, $offset: Int!, $showGames: Boolean = true, $sort: GameKuratorGroupGameSortEnum = popular, $showProviders: Boolean = false, $filterIds: [String!]) {\n  slugKuratorGroup(slug: $slug) {\n    ...GameKuratorGroup\n    gameCount(filterIds: $filterIds)\n    groupGamesList(limit: $limit, offset: $offset, sort: $sort, filterIds: $filterIds) @include(if: $showGames) {\n      ...GameKuratorGroupGame\n      __typename\n    }\n    filtersProvider: filters(type: provider) @include(if: $showProviders) {\n      count\n      group {\n        id\n        translation\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment GameKuratorGroup on GameKuratorGroup {\n  id\n  name\n  slug\n  translation\n  icon\n  thumbnailUrl\n  type\n  __typename\n}\n\nfragment GameKuratorGroupGame on GameKuratorGroupGame {\n  id\n  rank\n  game {\n    ...GameKuratorGame\n    __typename\n  }\n  __typename\n}\n\nfragment GameKuratorGame on GameKuratorGame {\n  id\n  name\n  slug\n  type\n  thumbnailUrl\n  edge\n  description\n  active\n  icon\n  isFavourite\n  showMultiplierLeaderboard\n  showProfitLeaderboard\n  data {\n    ... on SoftswissGame {\n      ...SoftswissGame\n      __typename\n    }\n    ... on EvolutionGame {\n      ...EvolutionGame\n      __typename\n    }\n    __typename\n  }\n  groupGames {\n    id\n    group {\n      id\n      translation\n      type\n      slug\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SoftswissGame on SoftswissGame {\n  id\n  edge\n  extId\n  isDemoEnabled\n  availableCurrencies\n  provider {\n    ...SoftswissProvider\n    __typename\n  }\n  __typename\n}\n\nfragment SoftswissProvider on SoftswissProvider {\n  id\n  name\n  __typename\n}\n\nfragment EvolutionGame on EvolutionGame {\n  id\n  name\n  category {\n    id\n    name\n    __typename\n  }\n  edge\n  currencies: availableCurrencies\n  __typename\n}\n"}
    headers = get_headers(key)
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


"""
For third party slots
"""
def start_softswiss_session(key, currency, target_currency='usd', slug='pragmatic-master-joker'):
    headers = get_headers(key)
    data = {"operationName": "StartSoftswissSession", "variables": {"currency": currency, "target": target_currency, "slug": slug},
            "query": "mutation StartSoftswissSession($slug: String!, $currency: CurrencyEnum!, $target: SoftswissCurrencyEnum!) {\n  startSoftswissSession(slug: $slug, currency: $currency, target: $target)\n}\n"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def demo_softswiss_session(key, slug='pragmatic-master-joker'):
    headers = get_headers(key)
    data = {"query": "mutation StartSoftswissDemo($slug: String!) {\n  startSoftswissDemo(slug: $slug)\n}\n",
            "operationName": "StartSoftswissDemo", "variables": {"slug": slug}}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)

# returns json within json
# getSoftswissLaunchOptions.strjson
def get_softswiss_launch_options(key, currency, slug, target_currency):
    headers = get_headers(key)
    data = {"variables": {"slug": slug, "currency": currency, "target": target_currency},
            "query": "mutation GetSoftswissLaunchOptions($slug: String!, $currency: CurrencyEnum!, $target: SoftswissCurrencyEnum!) {\n  getSoftswissLaunchOptions(slug: $slug, currency: $currency, target: $target)\n}\n", "operationName": "GetSoftswissLaunchOptions"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)


def get_softswiss_demo_launch_options(key, slug,):
    headers = get_headers(key)
    data = {"variables": {"slug": slug},
            "query": "mutation GetSoftswissDemoLaunchOptions($slug: String!) {\n  getSoftswissDemoLaunchOptions(slug: $slug)\n}\n", "operationName": "GetSoftswissDemoLaunchOptions"}
    return async_post(STAKE_GQL_ENDPOINT, headers=headers, data=data)
