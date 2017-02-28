# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import payment_term

def register():
    Pool.register(
        payment_term.PaymentTermLine,
        payment_term.Invoice,
        module='account_invoice_maturity_base', type_='model')
