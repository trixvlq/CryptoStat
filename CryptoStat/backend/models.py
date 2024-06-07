from django.contrib.auth.models import User
from django.db import models


class FavCrypto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.CharField(max_length=12)

    def __str__(self):
        return self.coin