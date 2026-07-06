"""
URL patterns for the payment app.

Paths are kept byte-for-byte identical to the original Flask
``@app.route(...)`` declarations so the checkout.js integration,
the S2S/webhook callback URL registered with Worldline, and
static/online_transaction.js's hard-coded ``url: "/payment"`` all keep
working without any reconfiguration on the Worldline/Paynimo merchant
dashboard.
"""

from django.urls import path

from . import views

app_name = 'payment'

urlpatterns = [
    path('payment/admin', views.admin_view, name='admin'),
    path('payment/', views.online_transaction, name='online_transaction'),
    path('payment/response', views.response_view, name='response'),
    path('payment/offline-verification', views.offline_verification, name='offline_verification'),
    path('payment/refund', views.refund, name='refund'),
    path('payment/reconcile', views.reconciliation, name='reconciliation'),
    path('payment/s2s', views.s2s, name='s2s'),

    path('emandate-si/mandate-verification', views.mandate_verification, name='mandate_verification'),
    path('emandate-si/transaction-scheduling', views.transaction_scheduling, name='transaction_scheduling'),
    path('emandate-si/transaction-verification', views.transaction_verification, name='transaction_verification'),
    path('emandate-si/stop-payment', views.stop_payment, name='stop_payment'),
    path('emandate-si/mandate-deactivation', views.mandate_deactivation, name='mandate_deactivation'),
]
