from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    companies = models.ManyToManyField(
        "pos.Company",
        related_name="companies",
        blank=True,
        null=True,
    )
    freshbooks_access_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="FreshBooks OAuth Token",
    )
    freshbooks_refresh_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="FreshBooks OAuth Refresh Token",
    )
    freshbooks_token_expires = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="FreshBooks OAuth Token Expiration",
    )

    class Meta:
        db_table = "auth_user"
