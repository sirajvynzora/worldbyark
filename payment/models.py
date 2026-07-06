"""
Models for the payment app.

The original Flask application did not use a database at all - the
Worldline/Paynimo merchant configuration edited on the admin page was
persisted directly to ``worldline_configuration.json`` on disk (see
``payment/utils.py``: ``read_config()`` / ``write_config()``).

To keep this Django port a faithful, drop-in replacement of that behaviour,
no Django models/ORM tables are required for the core checkout.js flows.
This file is intentionally left without model classes, but is kept in the
app (as Django expects) in case you later want to log transactions,
persist reconciliation results, etc. in the database instead of/along
with the JSON file.

Example of how you could start tracking transactions in the DB instead:

    class Transaction(models.Model):
        txn_id = models.CharField(max_length=64, unique=True)
        amount = models.DecimalField(max_digits=12, decimal_places=2)
        status_code = models.CharField(max_length=16, blank=True)
        status_message = models.CharField(max_length=255, blank=True)
        raw_response = models.JSONField(blank=True, null=True)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.txn_id} ({self.status_code})"
"""

from django.db import models  # noqa: F401
