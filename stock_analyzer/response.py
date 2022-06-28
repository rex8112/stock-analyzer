import datetime
import pandas as pd
from typing import Union


class ResponseMeta:
    def __init__(self, body: dict):
        self.meta: dict = body.get('Meta Data')
        self.symbol = None
        self.last_refreshed = None
        self.interval = None
        self.output_size = None
        self.parse_meta()

    def parse_meta(self):
        for key, value in self.meta.items():
            if 'Symbol' in key:
                self.symbol = value
            elif 'Last Refreshed' in key:
                date = datetime.datetime.strptime(value+'-0400', '%Y-%m-%d %H:%M:%S%z')
                self.last_refreshed = date
            elif 'Interval' in key:
                self.interval = value
            elif 'Output Size' in key:
                self.output_size = value


class IntraDayResponse(ResponseMeta):
    def __init__(self, body: dict):
        super().__init__(body)
        self.data: pd.DataFrame = pd.DataFrame()
        self.parse_data(body.get(f'Time Series ({self.interval})'))

    def parse_data(self, data: dict):
        df = []
        for key, value in data.items():
            date = datetime.datetime.strptime(key+'-0400', '%Y-%m-%d %H:%M:%S%z')
            labels = []
            values = []
            for k, v in value.items():
                labels.append(k)
                values.append(float(v))
            series = pd.Series(values, labels, name=date)
            df.append(series)
        self.data = pd.DataFrame(df)
