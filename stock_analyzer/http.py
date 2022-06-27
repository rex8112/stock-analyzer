import datetime as dt
from typing import Optional

import aiohttp
import asyncio

from .utils import get_utc_now, get_next_midnight, get_next_minute
from .exceptions import BadParameters, ErrorResponse

timezone = dt.timezone(dt.timedelta(hours=-4))
INTRADAY_INTERVALS = [
            '1min',
            '5min',
            '15min',
            '30min',
            '60min'
        ]


# noinspection SpellCheckingInspection
class FreeHTTPClient:
    MAX_DAY = 500
    MAX_MIN = 5

    def __init__(
            self,
            apikey: str,
            *,
            loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.apikey = apikey
        self._min_count = 0
        self._day_counter = 0
        self._session = aiohttp.ClientSession(
            'https://www.alphavantage.co',
            loop=self.loop)

        self.loop.create_task(self.reset_day_counter())
        self.loop.create_task(self.reset_min_counter())

    async def request(self, **params):
        params['apikey'] = self.apikey
        limited_amt = 0
        for tries in range(5):
            retry_after = self.get_retry_after()  # Immediately check if ratelimiting is necessary
            await asyncio.sleep(retry_after)

            body = {}
            async with self._session.get('/query', params=params) as resp:
                if resp.status != 200:
                    await asyncio.sleep((1 + tries) * 5)  # Alpha Vantage always returns 200 for everything
                    continue
                body = await resp.json()

            if 'Thank you for using Alpha Vantage!' in body.get('Note', ''):
                limited_amt += 1
                await asyncio.sleep(self.get_retry_after())
                continue  # Being rate limited

            self._min_count += 1
            self._day_counter += 1

            if body.get('Error Message'):
                raise ErrorResponse(body.get('Error Message'))
            return body
        if limited_amt >= 5:
            self._day_counter = FreeHTTPClient.MAX_DAY

    async def reset_min_counter(self):
        while True:
            now = get_utc_now().astimezone(timezone)
            next_minute = get_next_minute(now)
            delta = next_minute - now
            await asyncio.sleep(delta.seconds)

            self._min_count = 0

    async def reset_day_counter(self):
        while True:
            now = get_utc_now().astimezone(timezone)
            tomorrow = get_next_midnight(now)
            delta = tomorrow - now
            await asyncio.sleep(delta.seconds)

            self._day_counter = 0

    async def get_intraday(
            self,
            symbol: str,
            interval: str,
            *,
            adjusted: str = 'true',
            outputsize: str = 'compact',
            datatype: str = 'json') -> dir:
        """
        Fetch data from the Intraday API.
        From API Documentation: This API returns intraday time series of the equity specified, covering extended trading
        hours where applicable (e.g., 4:00am to 8:00pm Eastern Time for the US market). The intraday data is derived
        from the Securities Information Processor (SIP) market-aggregated data. You can query both raw (as-traded) and
        split/dividend-adjusted intraday data from this endpoint.

        This API returns the most recent 1-2 months of intraday data and is best suited for short-term/medium-term
        charting and trading strategy development. If you are targeting a deeper intraday history, please use the
        Extended Intraday API.`
        :param symbol: The name of the equity of your choice. For example: symbol=IBM
        :param interval: Time interval between two consecutive data points in the time series. The following values are
        supported: 1min, 5min, 15min, 30min, 60min
        :param adjusted: By default, adjusted=true and the output time series is adjusted by historical split and
        dividend events. Set adjusted=false to query raw (as-traded) intraday values.
        :param outputsize: By default, outputsize=compact. Strings compact and full are accepted with the following
        specifications: compact returns only the latest 100 data points in the intraday time series; full returns the
        full-length intraday time series. The "compact" option is recommended if you would like to reduce the data size
        of each API call.
        :param datatype: By default, datatype=json. Strings json and csv are accepted with the following specifications:
        json returns the intraday time series in JSON format; csv returns the time series as a CSV
        (comma separated value) file.
        :return:
        """
        if interval not in INTRADAY_INTERVALS:
            raise BadParameters(f'Parameter `interval` must be one of: {INTRADAY_INTERVALS}')

        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'adjusted': adjusted,
            'outputsize': outputsize,
            'datatype': datatype
        }

        resp_body = await self.request(**params)

        return resp_body

    async def close(self):
        await self._session.close()
        await asyncio.sleep(0.1)

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
