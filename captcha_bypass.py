from constants import STAKE_SITE_KEY, TWO_CAPTCHA_API_KEY
from core.http.util import async_get
from exceptions import InitCaptchaException, CaptchaException
import json 
import logging
import asyncio

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fh = logging.FileHandler('logs/captcha/bypass.log')
fhdbg = logging.FileHandler('logs/captcha/bypass_dbg.log')
fherr = logging.FileHandler('logs/captcha/bypass_err.log')
fhstdout = logging.StreamHandler()

fherr.setLevel(logging.ERROR)
fhstdout.setLevel(logging.INFO)
fhdbg.setLevel(logging.DEBUG)
fh.setLevel(logging.INFO)

log.addHandler(fhstdout)
log.addHandler(fherr)
log.addHandler(fh)
log.addHandler(fhdbg)

async def get_solved_captcha(page):
    get_captcha_url = f'http://2captcha.com/in.php?key={TWO_CAPTCHA_API_KEY}&method=hcaptcha&sitekey={STAKE_SITE_KEY}&pageurl={page}&json=1'
    r = await async_get(get_captcha_url)
    d = json.loads(r) 
    status = d['status']
    id = d['request']
    if status == 1:
        log.debug('\t'.join(['Getting captcha key', f'{status}', f'{id}']))
        await asyncio.sleep(5)
        return await check_captcha(id)
    else:
        log.debug('\t'.join(['Status 1', f'{status}', f'{id}']))
        raise InitCaptchaException(id, 'STATUS_1', r.text)


async def check_captcha(id):
    check_captcha_url = f'http://2captcha.com/res.php?key={TWO_CAPTCHA_API_KEY}&action=get&id={id}'
    r:str = await async_get(check_captcha_url)
    log.debug(str(r[:30]))
    if r == 'CAPCHA_NOT_READY':
        await asyncio.sleep(5)
        return await check_captcha(id)
    else:
        if not 'OK|' in r:
            raise CaptchaException(id, 'NOT OK| found', r)
        return r.replace('OK|', ''),  id


def report_bad(id):
    return async_get(f'http://2captcha.com/res.php?key={TWO_CAPTCHA_API_KEY}&action=reportbad&id={id}')


def report_good(id):
    return async_get(f'http://2captcha.com/res.php?key={TWO_CAPTCHA_API_KEY}&action=reportgood&id={id}')
