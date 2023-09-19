from django.contrib import admin

from . import models


@admin.register(models.PayPortal)
class PayPortalAdmin(admin.ModelAdmin):
    list_display = ["name", "code_name", 'backend', "default_currency"]
