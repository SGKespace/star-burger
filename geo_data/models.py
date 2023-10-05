from django.db import models
from django.utils.timezone import now


class GeoData(models.Model):
    address = models.CharField(
        'адрес',
        max_length=200,
        unique=True,
        db_index=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
    )
    created_at = models.DateTimeField(
        default=now,
    )
