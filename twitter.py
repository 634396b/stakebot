from core.http.util import async_get
from datetime import datetime
from constants import TWITTER_BEARER_TOKEN
import json
STAKE_USER_ID = '879543463657615360'


async def get_codes():
    headers = {'Authorization': TWITTER_BEARER_TOKEN}
    url = f'https://api.twitter.com/2/users/{STAKE_USER_ID}/tweets?tweet.fields=created_at,text,entities'
    r = await async_get(url, headers=headers)
    r = json.loads(r)
    tweets = r['data']
    bonus_urls = []
    for tweet in tweets:
        if not 'entities' in tweet:
            continue
        created_at = tweet['created_at']
        date_created = datetime.strptime(
            created_at, '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=None)
        entities = tweet['entities']
        bonus_url = ''
        if not 'urls' in entities:
            continue
        for url in entities['urls']:
            if 'stake.com/?bonus=' in url['expanded_url']:
                bonus_url = url['expanded_url']
                if ((datetime.utcnow() - date_created).total_seconds() <= 60):
                    bonus_urls.append(bonus_url[bonus_url.index('=') + 1:])
                    print(datetime.utcnow(), date_created, bonus_url)
    return bonus_urls
