import asyncio
import datetime as dt
from typing import Optional

import aiohttp

from .utils import get_utc_now, get_next_midnight, get_next_minute

timezone = dt.timezone(dt.timedelta(hours=-4))


class FreeHTTPClient:
    MAX_DAY = 500
    MAX_MIN = 5

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            connector: Optional[aiohttp.BaseConnector] = None):
        self.loop = loop
        self.connector = connector
        self._min_count = 0
        self._day_counter = 0
        self._session = aiohttp.ClientSession('https://www.alphavantage.co/query')

    async def request(self, **params):
        for tries in range(5):
            retry_after = self.get_retry_after()  # Immediately check if ratelimiting is necessary
            await asyncio.sleep(retry_after)

            body = {}
            async with self._session.get('', params=params) as resp:
                if resp.status != 200:
                    await asyncio.sleep((1 + tries) * 5)  # Alpha Vantage always returns 200 for everything
                    continue
                body = await resp.json()

            if 'Thank you for using Alpha Vantage!' in body.get('Note', ''):
                await asyncio.sleep(self.get_retry_after())
                continue  # Being rate limited




    def get_retry_after(self):
        if self._day_counter >= FreeHTTPClient.MAX_DAY:
            now = get_utc_now().astimezone(timezone)
            tomorrow = get_next_midnight(now)
            delta = tomorrow - now
            return delta.seconds
        elif self._min_count >= FreeHTTPClient.MAX_MIN:
            now = get_utc_now().astimezone(timezone)
            next_minute = get_next_minute(now)
            delta = next_minute - now
            return delta.seconds
        else:
            return 0
