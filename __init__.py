# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .payment_term import *

def register():
    Pool.register(
        PaymentTermLine,
        Invoice,
        module='account_invoice_maturity_base', type_='model')
