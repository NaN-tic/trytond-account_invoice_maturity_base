# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.sale.tests.test_account_invoice_maturity_base import suite
except ImportError:
    from .test_account_invoice_maturity_base import suite

__all__ = ['suite']
