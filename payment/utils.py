"""
Utility helpers for the payment app.

Ports of the small helper functions that lived in the Flask
``forms.py``/``worldline.py`` modules:

    * forms.py:read_data()      -> utils.read_config()
    * worldline.py:check_data() -> utils.check_config()
    * worldline.py:string_to_bool -> utils.string_to_bool()
"""

import json
import os

from django.conf import settings

# Mirrors the Flask app's `string_to_bool = {'true': True, True: True, ...}`
# lookup used to coerce the string 'true'/'false' values stored in the JSON
# config file into real Python booleans.
string_to_bool = {'true': True, True: True, 'false': False, False: False}

# Fields that must be non-empty for the merchant configuration to be
# considered "complete" (mirrors the Flask `check_data()` check).
REQUIRED_CONFIG_FIELDS = ('merchantCode', 'SALT', 'merchantSchemeCode', 'currency')


string_to_bool = {
    "true": True,
    True: True,
    "false": False,
    False: False,
}

REQUIRED_CONFIG_FIELDS = (
    "merchantCode",
    "SALT",
    "merchantSchemeCode",
    "currency",
)


def read_config():
    config_path = settings.WORLDLINE_CONFIG_FILE

    print("CONFIG PATH:", config_path)

    if not os.path.exists(config_path):
        print("Configuration file not found.")
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print("CONFIG DATA:", data)

        return data

    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        return {}

    except Exception as e:
        print("READ CONFIG ERROR:", e)
        return {}


def write_config(data):
    """
    Persist a dict as the Worldline/Paynimo merchant configuration JSON
    file (equivalent to the inline file-writing code in the Flask
    admin() view).
    """
    config_path = settings.WORLDLINE_CONFIG_FILE
    # csrfmiddlewaretoken is a Django-only artifact of the POSTed form and
    # was never part of the original merchant configuration schema, so it
    # is stripped out before persisting (the Flask app's CSRF token was
    # unintentionally saved into the file - we avoid replicating that bug).
    clean_data = {k: v for k, v in data.items() if k != 'csrfmiddlewaretoken'}
    with open(config_path, 'w') as f:
        f.write(json.dumps(clean_data, indent=4))
    return clean_data


def check_config():
    config_data = read_config()

    if not config_data:
        return False

    for field in REQUIRED_CONFIG_FIELDS:
        if not config_data.get(field):
            return False

    return config_data
