from django.urls import path
from .consumers import *

ws_urlpatterns = [
    path('ws/crypto/', CryptoConsumer.as_asgi()),
]
