import asyncio
import aiohttp


class Analyzer:
    MINUTE_RATELIMIT = 5
    DAY_RATELIMIT = 500

    def __init__(self, api='https://www.alphavantage.co/query'):
        self.api = api
        self.requests_minute = 0
        self.requests_day = 0
        self._loop = None
        self._http = None  # TODO: Implement HTTP Class
