from captcha_bypass import get_solved_captcha, report_bad, report_good
from exceptions import CaptchaException, InitCaptchaException
import time
import datetime
import stake_keys
import util
from datetime import timezone, timedelta, datetime
import logging
import asyncio
import json
import typing
from core.http.stake import claim_rewards, reward_meta, vip_nav_meta

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fh = logging.FileHandler('logs/claim/reload.log')
fhdbg = logging.FileHandler('logs/claim/reload_dbg.log')
fhe = logging.FileHandler('logs/claim/reload_errors.log')
fhd = logging.StreamHandler()

fhe.setLevel(logging.ERROR)
fh.setLevel(logging.INFO)
fhdbg.setLevel(logging.DEBUG)
fhd.setLevel(logging.INFO)

log.addHandler(fhe)
log.addHandler(fh)
log.addHandler(fhd)
log.addHandler(fhdbg)


def fmt_reload_page(currency):
    return f'https://stake.com/settings/general?currency={currency}&modal=vip&tab=reload'


async def is_ready(key):
    date_parse_fmt = '%a, %d %b %Y %H:%M:%S %Z'
    try:
        res = await reward_meta(key)
        util.check_response(res)
        r = json.loads(res)
        util.check_response(r)
        reload_data = r['data']['user']['reload']
        active = reload_data['active']
        expires_at = reload_data['expireAt']
        amt = reload_data['amount']
        claim_interval = reload_data['claimInterval']
        last_claim = reload_data['lastClaim']
        d_lc = None if last_claim == None else datetime.strptime(
            last_claim, date_parse_fmt)
        d_expires_at = datetime.strptime(expires_at, date_parse_fmt)
        d_now = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        d_adjusted_lc = None if d_lc == None else d_lc + \
            timedelta(0, claim_interval/1000)
        logs = ''.join([
            f'{str(d_now)}'.ljust(30),
            f'{str(d_adjusted_lc)}'.center(30),
            f'{str(d_expires_at)}'.center(30),
            f'{amt:.2e}'.center(10)
        ])
        log.debug(logs)
        return (d_adjusted_lc == None and active == True) or (d_adjusted_lc < d_now and d_now < d_expires_at and active == True)
    except Exception as e:
        await asyncio.sleep(10)
        log.error(e, exc_info=1)
    return False


async def claim_reload(key, currency):
    try:
        captcha, id = await get_solved_captcha(fmt_reload_page(currency))
        # Should not need check_response because claim reload should never be called if ip restricted is_ready() handles this
        result = await claim_rewards(key, captcha, currency=currency)
        res_json = json.loads(result)
        if 'errors' in res_json:
            log.error(result)
            await report_bad(id)
        else:
            await report_good(id)
            log.debug(result)
        util.write_reload_logs(result)
    except CaptchaException as e:
        id, *_ = e.args
        log.error(e, exc_info=1)
        util.write_reload_logs(str(e))
        await report_bad(id)
        await asyncio.sleep(10)
    except InitCaptchaException as e:
        id, *_ = e.args
        log.error(e, exc_info=1)
        util.write_reload_logs(str(e))
        await asyncio.sleep(10)
    except Exception as e:
        log.error(e, exc_info=1)
        await asyncio.sleep(10)


def is_not_throttled(dt_last_claim: datetime, s_delay: int) -> bool:
    return (datetime.now() - dt_last_claim).seconds >= s_delay


async def main(loop_delay, currency):
    keys: typing.List[str] = stake_keys.load_keys('data/api_keys_claim.txt')
    # Prevent attempting to claim after x seconds of claiming
    # This is used to prevent attempting to claim multiple times while already claiming
    # Probably from captcha pending
    claims: typing.Dict[str, datetime.datetime] = {}
    for key in keys:
        claims[key] = datetime.now()
    while True:
        await asyncio.sleep(loop_delay/2)
        try:
            for key in keys:
                nav_meta = await vip_nav_meta(key)
                util.check_response(nav_meta)
                nav_meta_json = json.loads(nav_meta)
                util.check_response(nav_meta_json)
                is_active = nav_meta_json['data']['user']['faucet']['active']
                if is_active and await is_ready(key) and is_not_throttled(claims[key], 120):
                    claims[key] = datetime.now()
                    await claim_reload(key, currency)
        except Exception as e:
            log.error(e, exc_info=1)
            await asyncio.sleep(10)
        finally:
            await asyncio.sleep(loop_delay/2)

if __name__ == "__main__":
    time.sleep(10)
    asyncio.get_event_loop().create_task(main(loop_delay=20, currency='ltc'))
    asyncio.get_event_loop().run_forever()
