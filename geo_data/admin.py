from django.contrib import admin

from .models import GeoData


@admin.register(GeoData)
class GeoDataAdmin(admin.ModelAdmin):
    pass
