"""
Django admin site registrations for the payment app.

There are no ORM models to register (see payment/models.py) - the merchant
configuration is managed through the custom /payment/admin view, not the
Django admin site. This file is kept for structure/future use.
"""

# from django.contrib import admin
# from .models import Transaction
#
# @admin.register(Transaction)
# class TransactionAdmin(admin.ModelAdmin):
#     list_display = ('txn_id', 'amount', 'status_code', 'created_at')
#     search_fields = ('txn_id',)
