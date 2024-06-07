from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect
from .Binance import get_historical_data, get_data_with_coin_info, API_KEY, API_SECRET, get_coin_info
from asgiref.sync import sync_to_async
from binance.client import AsyncClient

from .models import FavCrypto


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


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


async def cabinet(request):
    sync_render = sync_to_async(render)
    sync_favs = sync_to_async(FavCrypto.objects.filter)
    user = request.user
    favs = await sync_favs(user=request.user)
    result = []
    spot = await AsyncClient.create(API_KEY, API_SECRET)
    async for coin in favs:
        new_coin = await get_coin_info(spot, coin.coin)
        result.append(new_coin)
    await spot.close_connection()
    context = {
        'user': user,
        'coins': result
    }
    print('result: ', result)
    return await sync_render(request, 'cabinet.html', context)


def add_to_favs(request):
    user = request.user
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        new_fav = FavCrypto(user=user, coin=symbol)
        new_fav.save()
    return redirect('index')
