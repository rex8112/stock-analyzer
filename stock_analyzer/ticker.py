from .analyzer import Analyzer
from .response import IntraDayResponse
import pandas as pd
from io import StringIO


class Ticker:
    def __init__(self, analyzer: 'Analyzer', symbol: str):
        self.symbol = symbol
        self.analyzer = analyzer

    async def get_intraday(self, interval='60min', outputsize: str = 'compact'):
        resp = await self.analyzer.http.get_intraday(self.symbol, interval, outputsize=outputsize)
        response = IntraDayResponse(resp)
        return response

    async def bulk_extended(self, interval='60min'):
        slices = (
            'year1month1',
            'year1month2',
            'year1month3',
            'year1month4',
            'year1month5',
            'year1month6',
            'year1month7',
            'year1month8',
            'year1month9',
            'year1month10',
            'year1month11',
            'year1month12',
            'year2month1',
            'year2month2',
            'year2month3',
            'year2month4',
            'year2month5',
            'year2month6',
            'year2month7',
            'year2month8',
            'year2month9',
            'year2month10',
            'year2month11',
            'year2month12',
        )

        for s in slices:
            resp = await self.analyzer.http.get_intraday_extended(self.symbol, interval, s)
            yield pd.read_csv(StringIO(resp))
