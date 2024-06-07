from django.urls import path

from . import Binance
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('coin/<str:symbol>/', get_currency, name='coin'),
    path('search/', search, name='search'),
    path('get_top_coins/', get_top_coins, name='get_top_coins'),
    path('get_currency_data/<str:symbol>/', get_currency_data, name='get_currency_data'),
    path('signup/', signup_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('cabinet', cabinet, name='cabinet'),
    path('add_to_favs/', add_to_favs, name='add_to_favs'),
]
