import asyncio
import aiohttp

from .http import FreeHTTPClient
from typing import Optional


class Analyzer:
    MINUTE_RATELIMIT = 5
    DAY_RATELIMIT = 500

    def __init__(self, token=''):
        self.requests_minute = 0
        self.requests_day = 0
        self._loop = None
        self.http = FreeHTTPClient(token)
