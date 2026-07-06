"""
Static constants used across the payment app: the Paynimo/Worldline API
endpoint, request/subtype codes, and dropdown choice lists that were
hard-coded inline in the original Flask forms.py/worldline.py.
"""

from django.conf import settings

# ------------------------------------------------------------------------
# API
# ------------------------------------------------------------------------
WORLDLINE_API_URL = getattr(
    settings, 'WORLDLINE_API_URL', 'https://www.paynimo.com/api/paynimoV2.req'
)

# requestType values used by call_api()
REQUEST_TYPE_DUAL_VERIFICATION = 'S'
REQUEST_TYPE_OFFLINE_VERIFICATION = 'O'
REQUEST_TYPE_REFUND = 'R'
REQUEST_TYPE_SI = 'TSI'

# transaction.type for eMandate / SI on Cards
TXN_TYPE_SI_ON_CARDS = '001'
TXN_TYPE_EMANDATE = '002'

# transaction.subType for the various eMandate/SI operations
SUBTYPE_MANDATE_VERIFICATION = '002'
SUBTYPE_TRANSACTION_SCHEDULING = '003'
SUBTYPE_TRANSACTION_VERIFICATION = '004'
SUBTYPE_MANDATE_DEACTIVATION = '005'
SUBTYPE_STOP_PAYMENT = '006'


# ------------------------------------------------------------------------
# CHOICE LISTS (mirrors wtforms SelectField choices in the Flask forms.py)
# ------------------------------------------------------------------------
YES_NO_CHOICES = [
    ('true', 'Enabled'),
    ('false', 'Disabled'),
]

CURRENCY_CHOICES = [
    ('INR', 'INR'),
    ('USD', 'USD'),
]

TYPE_OF_PAYMENT_CHOICES = [
    ('TEST', 'TEST'),
    ('LIVE', 'LIVE'),
]

PAYMENT_MODE_CHOICES = [
    ('all', 'all'),
    ('cards', 'cards'),
    ('netBanking', 'netBanking'),
    ('UPI', 'UPI'),
    ('imps', 'imps'),
    ('wallets', 'wallets'),
    ('cashCards', 'cashCards'),
    ('NEFTRTGS', 'NEFTRTGS'),
    ('emiBanks', 'emiBanks'),
]

TRANSACTION_TYPE_CHOICES = [
    ('SALE', 'SALE'),
]

TYPE_OF_TRANSACTION_CHOICES = [
    ('eMandate', 'eMandate'),
    ('SIonCards', 'SI on Cards'),
]

AMOUNT_TYPE_CHOICES = [
    ('M', 'Variable'),
    ('F', 'Fixed'),
]

FREQUENCY_CHOICES = [
    ('ADHO', 'As and when presented'),
    ('DAIL', 'Daily'),
    ('WEEK', 'Weekly'),
    ('MNTH', 'Monthly'),
    ('QURT', 'Quarterly'),
    ('MIAN', 'Semi Annually'),
    ('YEAR', 'Yearly'),
    ('BIMN', 'Bi-monthly'),
]

ACCOUNT_TYPE_CHOICES = [
    ('Saving', 'Saving'),
    ('Current', 'Current'),
]
