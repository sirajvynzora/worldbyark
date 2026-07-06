import json
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse


SAMPLE_CONFIG = {
    "merchantCode": "T891293",
    "merchantSchemeCode": "FIRST",
    "SALT": "4096964465RLFSUF",
    "currency": "INR",
    "typeOfPayment": "TEST",
    "primaryColor": "#808080",
    "secondaryColor": "#000000",
    "buttonColor1": "#1969bb",
    "buttonColor2": "#FFFFFF",
    "logoURL": "https://www.paynimo.com/CompanyDocs/company-logo-md.png",
    "enableExpressPay": "false",
    "separateCardMode": "false",
    "enableNewWindowFlow": "true",
    "merchantMessage": "",
    "disclaimerMessage": "",
    "paymentMode": "all",
    "paymentModeOrder": "cards,netBanking,imps,wallets,cashCards,UPI,MVISA,debitPin,NEFTRTGS,emiBanks",
    "enableInstrumentDeRegistration": "false",
    "transactionType": "SALE",
    "hideSavedInstruments": "false",
    "saveInstrument": "false",
    "displayTransactionMessageOnPopup": "false",
    "embedPaymentGatewayOnPage": "false",
    "enableSI": "false",
    "hideSIDetails": "false",
    "hideSIConfirmation": "false",
    "expandSIDetails": "false",
    "enableDebitDay": "false",
    "showSIResponseMsg": "false",
    "showSIConfirmation": "false",
    "enableTxnForNonSICards": "false",
    "showAllModesWithSI": "false",
}


class PaymentViewsTests(TestCase):
    def setUp(self):
        self.config_path = self._tmp_config_file()

    def _tmp_config_file(self):
        import tempfile
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(SAMPLE_CONFIG, tmp)
        tmp.close()
        return tmp.name

    def test_admin_page_loads(self):
        with override_settings(WORLDLINE_CONFIG_FILE=self.config_path):
            response = self.client.get(reverse('payment:admin'))
            self.assertEqual(response.status_code, 200)

    def test_online_transaction_page_loads(self):
        with override_settings(WORLDLINE_CONFIG_FILE=self.config_path):
            response = self.client.get(reverse('payment:online_transaction'))
            self.assertEqual(response.status_code, 200)

    def test_mandatory_fields_error_when_config_missing(self):
        with override_settings(WORLDLINE_CONFIG_FILE='/tmp/does-not-exist.json'):
            response = self.client.get(reverse('payment:online_transaction'))
            self.assertContains(response, 'mandatory fields', status_code=200, msg_prefix='', html=False)

    @patch('payment.views.call_api')
    def test_offline_verification_post(self, mock_call_api):
        mock_call_api.return_value = {
            'merchantTransactionIdentifier': 'TXN1',
            'paymentMethod': {
                'paymentTransaction': {
                    'statusCode': '0300',
                    'identifier': 'PGID',
                    'amount': '100',
                    'errorMessage': '',
                    'statusMessage': 'D',
                    'dateTime': '2026-01-01',
                }
            },
        }
        with override_settings(WORLDLINE_CONFIG_FILE=self.config_path):
            response = self.client.post(reverse('payment:offline_verification'), {
                'merchantTxnId': 'TXN1',
                'date': '2026-01-01',
            })
            self.assertEqual(response.status_code, 200)
            mock_call_api.assert_called_once()
