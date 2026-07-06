"""
External service calls to the Worldline / Paynimo payment gateway API.

Port of Flask's worldline.py:call_api().
"""

import json

import requests

from .constants import WORLDLINE_API_URL


def call_api(data):
    raw_response = requests.post(
        url=WORLDLINE_API_URL,
        data=json.dumps(data)
    )
    return raw_response.json()
