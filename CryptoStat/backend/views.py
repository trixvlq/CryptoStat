from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect
from .Binance import get_historical_data, get_data_with_coin_info, API_KEY, API_SECRET
from asgiref.sync import sync_to_async
from binance.client import AsyncClient


def index(request):
    if request.method == 'POST':
        print('yes')
        symbol = request.POST.get('symbol')
        return redirect('coin', symbol=symbol)
    else:
        context = {
            'js': True
        }
        return render(request, 'index.html', context)


def search(request):
    symbol = request.POST.get('symbol')
    return redirect('coin', symbol=symbol)


def get_top_coins(request):
    return render(request, 'get_top_coins.html')


async def get_currency(request, symbol):
    spot = await AsyncClient.create(API_KEY, API_SECRET)
    crypto = await get_data_with_coin_info(spot, 0, 1)
    print(crypto)
    await spot.close_connection()
    context = {
        'crypto': crypto[0],
    }
    return render(request, 'crypto.html', context)


async def get_currency_data(request, symbol):
    data = await get_historical_data(symbol)
    return JsonResponse(data, safe=False)
