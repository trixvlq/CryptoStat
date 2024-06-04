from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from .Binance import API_KEY, API_SECRET, get_top_coins, get_data_with_coin_info, get_coin_info
from binance.client import AsyncClient


class CryptoConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        self.coins = []
        # синглтон предотвращает избыточное создание клиентов
        self.spot = await AsyncClient.create(API_KEY, API_SECRET)
        # цепочка обязанностей т.к. одна функция вызывает другую и т.д.
        await self.send_initial_data()

    async def send_initial_data(self):
        await asyncio.gather(self.send_top_coins(), self.send_all_coins())

    async def send_top_coins(self):
        top_coins = await get_top_coins(self.spot)
        for coin in top_coins:
            self.coins.append(coin)
            await self.send(text_data=json.dumps({
                'type': 'top3',
                'content': coin
            }))
            await asyncio.sleep(0)

    async def send_all_coins(self):
        self.start = 0
        self.limit = 10
        all_coins = await get_data_with_coin_info(self.spot, self.start, self.limit)
        for coin in all_coins:
            await self.send(text_data=json.dumps({
                'type': 'coin',
                'content': coin
            }))
            self.coins.append(coin)
            await asyncio.sleep(0)
        self.start = self.limit
        self.limit += 10

    async def disconnect(self, close_code):
        self.coins = []
        self.start = 0
        self.limit = 0
        await self.spot.close_connection()
        await self.close()

    async def receive(self, text_data):
        if json.loads(text_data)['command'] == 'load_more':
            await self.send_all_coins()
        else:
            method = json.loads(text_data)['method']

            valid_coins = []
            for coin in self.coins:
                if 'price' in coin and 'status' in coin and 'price' in coin['price']:
                    valid_coins.append(coin)
            # Стратегия т.к. используются различные стратегии сортировки что позволяет динамически изменять поведение системы
            if method == 'price':
                ordered_coins = sorted(valid_coins, key=lambda x: float(x["price"]["price"]), reverse=True)
            elif method == 'change':
                ordered_coins = sorted(valid_coins, key=lambda x: float(x['status']['priceChangePercent']),
                                       reverse=True)
            elif method == 'last_price':
                ordered_coins = sorted(valid_coins, key=lambda x: float(x['status']['lastPrice']), reverse=True)
            else:
                ordered_coins = valid_coins

            await self.send(text_data=json.dumps({
                'type': 'coin',
                'method': 'rearrange',
                'content': ordered_coins
            }))
