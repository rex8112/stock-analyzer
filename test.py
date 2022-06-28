import asyncio

import pandas as pd

import stock_analyzer


async def main():
    a = stock_analyzer.Analyzer('')
    try:
        t = stock_analyzer.Ticker(a, 'SPY')

        max_high = 0
        high_count = 0
        total = 0
        increases_sum = 0
        percentage_sum = 0
        async for d in t.bulk_extended(interval='30min'):
            for index, row in d.iterrows():
                if '09:30:00' in row['time']:
                    total += 1
                    op = row['open']
                    high = row['high']
                    close = row['close']
                    if high > op:
                        max_high += 1
                    if close > op:
                        high_count += 1
                    increases_sum += high - op
                    percentage_sum += (high - op) / op
        max_prob = max_high / total
        prob = high_count / total
        avg = increases_sum / total
        avg_p = percentage_sum / total
        d = pd.Series(
            [prob, max_prob, avg, avg_p, total],
            ['Higher %', 'Max %', 'Avg High Increase', 'Avg % Increase', 'Total'],
            name='SPY'
        )
        print(d)
    except Exception as e:
        raise e
    finally:
        await a.http.close()
        await asyncio.sleep(0.5)

asyncio.run(main())
