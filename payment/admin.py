from django.contrib import admin

from . import models


@admin.register(models.PayPortal)
class PayPortalAdmin(admin.ModelAdmin):
    list_display = ["name", "code_name", 'backend', "default_currency"]


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "create_date", "status", 'shaparak_tracking_code']
    search_fields = ["user__username", "user__first_name", "user__last_name", "amount", "currency", "create_date",
                     "status", 'shaparak_tracking_code', 'description']
    list_filter = [
        'status',
        'currency',
        ('portal', admin.RelatedOnlyFieldListFilter)
    ]
    date_hierarchy = 'create_date'
    show_facets = admin.ShowFacets.ALWAYS
