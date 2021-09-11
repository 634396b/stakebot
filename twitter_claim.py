import twitter
from claim import get_solved_captcha, report_bad, report_good
import core.http.stake as stake_http
import stake_keys
import time
import logging
import sys
import asyncio
from datetime import datetime
import typing
import json

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fhe = logging.FileHandler('logs/claim/twitter_claim_errors.log')
fh = logging.FileHandler('logs/claim/twitter_claim.log')
fhd = logging.StreamHandler(sys.stdout)

fhe.setLevel(logging.ERROR)
fh.setLevel(logging.DEBUG)
fhd.setLevel(logging.INFO)

log.addHandler(fhd)
log.addHandler(fh)
log.addHandler(fhe)


def get_code_page(code):
    return f'https://stake.com/?code={code}&modal=redeemBonus'


async def claim_code(key, code):
    try:
        captcha, id = await get_solved_captcha(get_code_page(code))
        # Should not need check_response because claim reload should never be called if ip restricted is_ready() handles this
        result = await stake_http.claim_bonus(
            key=key, code=code, captcha=captcha)
        r = json.loads(result)
        if 'errors' in r:
            log.error(
                '\t'.join([f'{result.text}', f'{code}',  f'{captcha[:30]}']))
            if r['errors'][0]['errorType'] == 'notFound':
                raise Exception('No code found')
            else:
                await report_bad(id)
        else:
            await report_good(id)
            log.info(str(result))
    except Exception as e:
        log.error(e, exc_info=1)
        return False
    return True


async def main(key):
    await asyncio.sleep(10)
    # Prevent attempting to claim after x seconds of claiming
    # This is used to prevent attempting to claim multiple times while already claiming
    # Probably from captcha pending
    claims: typing.Dict[str, datetime] = {}
    for key in keys:
        claims[key] = datetime.now()
    while True:
        await asyncio.sleep(15)
        try:
            codes = twitter.get_codes()
            if len(codes) > 0:
                for code in codes:
                    if code in claims and (datetime.now() - claims[code]).seconds > 120:
                        claims[code] = datetime.now()
                        asyncio.ensure_future(claim_code(key, code))
        except Exception as e:
            log.error(e, exc_info=1)
        finally:
            await asyncio.sleep(15)

if __name__ == "__main__":
    time.sleep(10)
    keys = stake_keys.load_keys(path='data/api_keys_twitter.txt')
    for key in keys:
        time.sleep(1)
        asyncio.get_event_loop().create_task(main(key))
    asyncio.get_event_loop().run_forever()
