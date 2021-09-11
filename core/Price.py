import asyncio
import aiohttp

currencies = ['ltc', 'btc', 'eth', 'xrp', 'eos', 'bch', 'doge', 'trx']


class Price:
    prices = {}

    def get_price(self, currency: str):
        if not currency in self.prices:
            raise Exception(f'{currency} not found in {self.prices}')
        return self.prices[currency.lower()]

    async def update_price(self, currency: str = None):
        await asyncio.sleep(0.1)
        if currency is None:
            for c in currencies:
                await asyncio.sleep(0.2)
                await self.update_price(c)
            return True
        currency = currency.lower()
        ce = 'litecoin' if currency == 'ltc' else ''
        ce = 'bitcoin' if currency == 'btc' else ce
        ce = 'tron' if currency == 'trx' else ce
        ce = 'ethereum' if currency == 'eth' else ce
        ce = 'dogecoin' if currency == 'doge' else ce
        ce = 'bitcoin-cash' if currency == 'bch' else ce
        ce = 'ripple' if currency == 'xrp' else ce
        ce = 'eos' if currency == 'eos' else ce
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.coingecko.com/api/v3/coins/{ce}') as response:
                    r_json = await response.json(content_type=None)
                    p = r_json['market_data']['current_price']['usd']
                    self.prices[currency] = p
        except Exception as e:
            print(e)
        finally:
            return True

    def __str__(self):
        return f'\t|\t{self.prices}\t|\t'
