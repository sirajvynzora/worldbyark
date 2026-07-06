"""
Worldline / Paynimo payload builders.

This module is a direct port of the request-building logic that lived
inline inside the Flask app's ``worldline.py`` view functions. Keeping it
separate from ``views.py`` mirrors the original file's name and purpose
while fitting Django's views/services separation.
"""

import hashlib

from .utils import string_to_bool


# ------------------------------------------------------------------------
# Online transaction (checkout.js) hashing + consumerData payload
# ------------------------------------------------------------------------
def get_datastring(data):
    """Build the pipe-delimited string that gets SHA-512 hashed to
    produce the checkout.js `token`. Port of Flask's get_datastring()."""
    return (
        data['merchantCode'] + '|' + data['txn_id'] + '|' + data['amount'] + '|'
        + data['accNo'] + '|' + data['custID'] + '|' + data['mobNo'] + '|'
        + data['email'] + '|'
        + '-'.join(reversed(data['debitStartDate'].split('-'))) + '|'
        + '-'.join(reversed(data['debitEndDate'].split('-'))) + '|'
        + data['maxAmount'] + '|' + data['amountType'] + '|' + data['frequency'] + '|'
        + data['cardNumber'] + '|' + data['expMonth'] + '|' + data['expYear'] + '|'
        + data['cvvCode'] + '|' + data['SALT']
    )


def hash_datastring(data_string):
    """SHA-512 hex digest of the built data string."""
    return hashlib.sha512(data_string.encode()).hexdigest()


def get_hash_object(hashed_data, data, config_data):
    """Build the full checkout.js `consumerData` request object that gets
    returned to the browser and passed to $.pnCheckout(). Port of Flask's
    get_hash_object()."""
    prepared_object = {
        'tarCall': False,
        'features': {
            'showPGResponseMsg': True,
            'enableMerTxnDetails': True,
            'enableAbortResponse': False,
            'enableSI': string_to_bool[config_data['enableSI']],
            'siDetailsAtMerchantEnd': string_to_bool[config_data.get('siDetailsAtMerchantEnd', 'false')],
            'enableNewWindowFlow': string_to_bool[config_data['enableNewWindowFlow']],
            'enableExpressPay': string_to_bool[config_data['enableExpressPay']],
            'enableInstrumentDeRegistration': string_to_bool[config_data['enableInstrumentDeRegistration']],
            'hideSavedInstruments': string_to_bool[config_data['hideSavedInstruments']],
            'separateCardMode': string_to_bool[config_data['separateCardMode']],
            'payWithSavedInstrument': string_to_bool[config_data['saveInstrument']],
            'hideSIDetails': string_to_bool[config_data['hideSIDetails']],
            'hideSIConfirmation': string_to_bool[config_data['hideSIConfirmation']],
            'expandSIDetails': string_to_bool[config_data['expandSIDetails']],
            'enableDebitDay': string_to_bool[config_data['enableDebitDay']],
            'showSIResponseMsg': string_to_bool[config_data['showSIResponseMsg']],
            'showSIConfirmation': string_to_bool[config_data['showSIConfirmation']],
            'enableTxnForNonSICards': string_to_bool[config_data['enableTxnForNonSICards']],
            'showAllModesWithSI': string_to_bool[config_data['showAllModesWithSI']],
        },
        'consumerData': {
            'deviceId': 'WEBSH2',  # possible values 'WEBSH1', 'WEBSH2' and 'WEBMD5'
            'token': hashed_data,
            'returnUrl': data['returnUrl'],
            'paymentMode': config_data['paymentMode'],
            'paymentModeOrder': config_data['paymentModeOrder'].replace(' ', '').split(','),
            'checkoutElement': '#worldline_embeded_popup' if string_to_bool[config_data['embedPaymentGatewayOnPage']] else '',
            'merchantLogoUrl': config_data['logoURL'],
            'merchantId': data['merchantCode'],
            'merchantMsg': config_data['merchantMessage'],
            'disclaimerMsg': config_data['disclaimerMessage'],
            'currency': data['currency'],
            'consumerId': data['custID'],
            'consumerMobileNo': data['mobNo'],
            'consumerEmailId': data['email'],
            'txnId': data['txn_id'],
            'items': [{
                'itemId': data['merchantSchemeCode'],
                'amount': data['amount'],
                'comAmt': '0',
            }],
            'customStyle': {
                'PRIMARY_COLOR_CODE': config_data['primaryColor'],
                'SECONDARY_COLOR_CODE': config_data['secondaryColor'],
                'BUTTON_COLOR_CODE_1': config_data['buttonColor1'],
                'BUTTON_COLOR_CODE_2': config_data['buttonColor2'],
            },
        },
    }

    if string_to_bool[data['siDetailsAtMerchantEndCond']]:
        prepared_object['consumerData']['accountNo'] = data['accNo']
        prepared_object['consumerData']['accountHolderName'] = data['accountHolderName']
        prepared_object['consumerData']['ifscCode'] = data['ifscCode']
        prepared_object['consumerData']['accountType'] = data['accountType']
        prepared_object['consumerData']['debitStartDate'] = '-'.join(reversed(data['debitStartDate'].split('-')))
        prepared_object['consumerData']['debitEndDate'] = '-'.join(reversed(data['debitEndDate'].split('-')))
        prepared_object['consumerData']['maxAmount'] = data['maxAmount']
        prepared_object['consumerData']['amountType'] = data['amountType']
        prepared_object['consumerData']['frequency'] = data['frequency']
    elif string_to_bool[config_data['enableSI']] and not string_to_bool[data['siDetailsAtMerchantEndCond']]:
        prepared_object['consumerData']['debitStartDate'] = '-'.join(reversed(data['debitStartDate'].split('-')))
        prepared_object['consumerData']['debitEndDate'] = '-'.join(reversed(data['debitEndDate'].split('-')))
        prepared_object['consumerData']['maxAmount'] = data['maxAmount']
        prepared_object['consumerData']['amountType'] = data['amountType']
        prepared_object['consumerData']['frequency'] = data['frequency']

    return prepared_object


def verify_s2s_hash(data_parts, salt):
    """Recompute the SHA-512 hash of the pipe-delimited S2S callback
    fields (all but the last, which IS the hash) and compare it against
    the hash sent by the gateway. Port of Flask's s2s() view logic."""
    data_string = '|'.join(data_parts[:-1]) + '|' + salt
    result = hashlib.sha512(data_string.encode()).hexdigest()
    return data_parts[-1] == result


# ------------------------------------------------------------------------
# Dual verification (response.html POST-back handler)
# ------------------------------------------------------------------------
def build_dual_verification_payload(config_data, token, date_time):
    return {
        'merchant': {
            'identifier': config_data['merchantCode'],
        },
        'transaction': {
            'deviceIdentifier': 'S',
            'currency': config_data['currency'],
            'dateTime': date_time,
            'token': token,
            'requestType': 'S',
        },
    }


# ------------------------------------------------------------------------
# Offline verification / Reconciliation
# ------------------------------------------------------------------------
def build_offline_verification_payload(config_data, merchant_txn_id, date_str):
    return {
        'merchant': {
            'identifier': config_data['merchantCode'],
        },
        'transaction': {
            'deviceIdentifier': 'S',
            'currency': config_data['currency'],
            'identifier': merchant_txn_id,
            'dateTime': date_str,
            'requestType': 'O',
        },
    }


# ------------------------------------------------------------------------
# Refund
# ------------------------------------------------------------------------
def build_refund_payload(config_data, token, amount, date_str):
    return {
        'merchant': {
            'identifier': config_data['merchantCode'],
        },
        'cart': {},
        'transaction': {
            'deviceIdentifier': 'S',
            'amount': amount,
            'currency': config_data['currency'],
            'token': token,
            'dateTime': date_str,
            'requestType': 'R',
        },
    }


# ------------------------------------------------------------------------
# eMandate / SI: Mandate verification
# ------------------------------------------------------------------------
def build_mandate_verification_payload(config_data, type_of_transaction, merchant_txn_id, customer_id, date_str):
    type_data = '002' if type_of_transaction == 'eMandate' else '001'
    return {
        'merchant': {
            'identifier': config_data['merchantCode'],
        },
        'payment': {
            'instruction': {},
        },
        'transaction': {
            'deviceIdentifier': 'S',
            'type': type_data,
            'currency': config_data['currency'],
            'identifier': merchant_txn_id,
            'dateTime': date_str,
            'subType': '002',
            'requestType': 'TSI',
        },
        'consumer': {
            'identifier': customer_id,
        },
    }


# ------------------------------------------------------------------------
# eMandate / SI: Transaction scheduling
# ------------------------------------------------------------------------
def build_transaction_scheduling_payload(config_data, transaction_id, type_of_transaction, amount, end_date_ddmmyyyy, mandate_reg_id):
    type_data = '002' if type_of_transaction == 'eMandate' else '001'
    return {
        'merchant': {
            'identifier': config_data['merchantCode'],
        },
        'payment': {
            'instrument': {
                'identifier': config_data['merchantSchemeCode'],
            },
            'instruction': {
                'amount': amount,
                'endDateTime': end_date_ddmmyyyy,
                'identifier': mandate_reg_id,
            },
        },
        'transaction': {
            'deviceIdentifier': 'S',
            'type': type_data,
            'currency': config_data['currency'],
            'identifier': transaction_id,
            'subType': '003',
            'requestType': 'TSI',
        },
    }


# ------------------------------------------------------------------------
# eMandate / SI: Transaction verification
# ------------------------------------------------------------------------
def build_transaction_verification_payload(config_data, type_of_transaction, merchant_txn_id, date_str):
    type_data = '002' if type_of_transaction == 'eMandate' else '001'
    return {
        'merchant': {
            'identifier': config_data['merchantCode'],
        },
        'payment': {
            'instruction': {},
        },
        'transaction': {
            'deviceIdentifier': 'S',
            'type': type_data,
            'currency': config_data['currency'],
            'identifier': merchant_txn_id,
            'dateTime': date_str,
            'subType': '004',
            'requestType': 'TSI',
        },
    }


def normalize_transaction_verification_status(response):
    """Translate the single-letter statusMessage code into a readable
    label, exactly like the Flask view did in-place."""
    status_map = {'I': 'Initiated', 'D': 'Success', 'F': 'Failure'}
    try:
        code = response['paymentMethod']['paymentTransaction']['statusMessage']
        if code in status_map:
            response['paymentMethod']['paymentTransaction']['statusMessage'] = status_map[code]
    except (KeyError, TypeError):
        pass
    return response


# ------------------------------------------------------------------------
# eMandate / SI: Stop payment & Mandate deactivation
# ------------------------------------------------------------------------
def _empty_cart_item():
    return {
        'description': '',
        'providerIdentifier': '',
        'surchargeOrDiscountAmount': '',
        'amount': '',
        'comAmt': '',
        'sKU': '',
        'reference': '',
        'identifier': '',
    }


def _empty_instrument(identifier=''):
    return {
        'expiry': {'year': '', 'month': '', 'dateTime': ''},
        'provider': '',
        'iFSC': '',
        'holder': {
            'name': '',
            'address': {
                'country': '', 'street': '', 'state': '',
                'city': '', 'zipCode': '', 'county': '',
            },
        },
        'bIC': '',
        'type': '',
        'action': '',
        'mICR': '',
        'verificationCode': '',
        'iBAN': '',
        'processor': '',
        'issuance': {'year': '', 'month': '', 'dateTime': ''},
        'alias': '',
        'identifier': identifier,
        'token': '',
        'authentication': {'token': '', 'type': '', 'subType': ''},
        'subType': '',
        'issuer': '',
        'acquirer': '',
    }


def _empty_instruction(amount=''):
    return {
        'occurrence': '',
        'amount': amount,
        'frequency': '',
        'type': '',
        'description': '',
        'action': '',
        'limit': '',
        'endDateTime': '',
        'identifier': '',
        'reference': '',
        'startDateTime': '',
        'validity': '',
    }


def build_stop_payment_payload(config_data, transaction_id, tpsl_transaction_id):
    return {
        'merchant': {
            'webhookEndpointURL': '',
            'responseType': '',
            'responseEndpointURL': '',
            'description': '',
            'identifier': config_data['merchantCode'],
            'webhookType': '',
        },
        'cart': {
            'item': [_empty_cart_item()],
            'reference': '',
            'identifier': '',
            'description': '',
            'Amount': '',
        },
        'payment': {
            'method': {'token': '', 'type': ''},
            'instrument': _empty_instrument(identifier=config_data['merchantSchemeCode']),
            'instruction': _empty_instruction(amount='11'),
        },
        'transaction': {
            'deviceIdentifier': 'S',
            'smsSending': '',
            'amount': '',
            'forced3DSCall ': '',
            'type': '001',
            'description': '',
            'currency': config_data['currency'],
            'isRegistration': '',
            'identifier': transaction_id,
            'dateTime': '',
            'token': tpsl_transaction_id,
            'securityToken': '',
            'subType': '006',
            'requestType': 'TSI',
            'reference': '',
            'merchantInitiated': '',
            'merchantRefNo': '',
        },
        'consumer': {
            'mobileNumber': '',
            'emailID': '',
            'identifier': '',
            'accountNo': '',
        },
    }


def build_mandate_deactivation_payload(config_data, transaction_id, type_of_transaction, mandate_reg_id):
    type_data = '002' if type_of_transaction == 'eMandate' else '001'
    return {
        'merchant': {
            'webhookEndpointURL': '',
            'responseType': '',
            'responseEndpointURL': '',
            'description': '',
            'identifier': config_data['merchantCode'],
            'webhookType': '',
        },
        'cart': {
            'item': [_empty_cart_item()],
            'reference': '',
            'identifier': '',
            'description': '',
            'Amount': '',
        },
        'payment': {
            'method': {'token': '', 'type': ''},
            'instrument': _empty_instrument(),
            'instruction': _empty_instruction(),
        },
        'transaction': {
            'deviceIdentifier': 'S',
            'smsSending': '',
            'amount': '',
            'forced3DSCall ': '',
            'type': type_data,
            'description': '',
            'currency': config_data['currency'],
            'isRegistration': '',
            'identifier': transaction_id,
            'dateTime': '',
            'token': mandate_reg_id,
            'securityToken': '',
            'subType': '005',
            'requestType': 'TSI',
            'reference': '',
            'merchantInitiated': '',
            'merchantRefNo': '',
        },
        'consumer': {
            'mobileNumber': '',
            'emailID': '',
            'identifier': '',
            'accountNo': '',
        },
    }


def normalize_mandate_deactivation_response(response):
    """If the gateway returned completely empty status fields, surface a
    friendlier 'Not Found' label - matches the Flask view's in-place fix-up."""
    try:
        status_code = response['paymentMethod']['paymentTransaction']['statusCode']
        error_desc = response['paymentMethod']['error']['desc']
        if status_code == "" and error_desc == "":
            response['paymentMethod']['paymentTransaction']['statusCode'] = "Not Found"
            response['paymentMethod']['error']['desc'] = "Not Found"
    except (KeyError, TypeError):
        pass
    return response
