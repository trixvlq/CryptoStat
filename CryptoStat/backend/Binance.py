from datetime import datetime, timedelta
from binance.client import AsyncClient
import asyncio

API_KEY = 'твой апи кей'
API_SECRET = 'твой апи секрет'


# фабрика т.к. спот создается один раз и используется в последующихся функциях
async def get_coin_info(spot, symbol):
    coin = await spot.get_symbol_info(symbol=symbol)
    price = await spot.get_symbol_ticker(symbol=symbol)
    status = await spot.get_ticker(symbol=symbol)
    coin_data = {
        'coin': coin,
        'price': price,
        'status': status
    }
    return coin_data

# фабрика т.к. спот создается один раз и используется в последующихся функциях
async def get_data(spot):
    coins = await spot.get_all_tickers()
    return coins

# фабрика т.к. спот создается один раз и используется в последующихся функциях
async def get_data_with_coin_info(spot, start, limit):
    coins = await get_data(spot)
    result = []
    tasks = [get_coin_info(spot, coin['symbol']) for coin in coins[start:limit]]
    result = await asyncio.gather(*tasks)
    return result

# фабрика т.к. спот создается один раз и используется в последующихся функциях
async def get_top_coins(spot):
    coins = await spot.get_all_tickers()
    coins.sort(key=lambda x: float(x['price']), reverse=True)
    result = []
    for coin in coins:
        if 'USDT' in coin['symbol'] and len(result) != 3:
            new_coin = await spot.get_symbol_info(coin['symbol'])
            if new_coin['status'] == 'TRADING':
                result.append(new_coin)
    return result


async def get_historical_data(symbol):
    spot = await AsyncClient.create(API_KEY, API_SECRET)
    end_time = datetime.now().strftime('%Y-%m-%d')
    start_time = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    interval = '1M'

    klines = await spot.get_historical_klines(symbol, interval, start_time, end_time)
    await spot.close_connection()

    if len(klines) == 0:
        price_data = None
    else:
        price_data = [{
            'timestamp': kline[0],
            'price': float(kline[4])
        } for kline in klines]

    return price_data
