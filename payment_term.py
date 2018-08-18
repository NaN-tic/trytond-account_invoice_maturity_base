# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from decimal import Decimal

__all__ = ['PaymentTermLine', 'Invoice']


class PaymentTermLine(metaclass=PoolMeta):
    __name__ = 'account.invoice.payment_term.line'

    @classmethod
    def __setup__(cls):
        super(PaymentTermLine, cls).__setup__()
        cls.ratio.states['required'] |= Eval('type') == 'percent_on_untaxed_amount'
        cls.ratio.states['invisible'] &= Eval('type') != 'percent_on_untaxed_amount'
        cls.divisor.states['required'] |= Eval('type') == 'percent_on_untaxed_amount'
        cls.divisor.states['invisible'] &= Eval('type') != 'percent_on_untaxed_amount'
        item = ('percent_on_untaxed_amount', 'Percentage on Untaxed Amount')
        if not item in cls.type.selection:
            cls.type.selection.append(item)

    def get_value(self, remainder, amount, currency):
        value = super(PaymentTermLine, self).get_value(
            remainder, amount, currency)
        if self.type == 'percent_on_untaxed_amount':
            untaxed_amount = Transaction().context.get('untaxed_amount', Decimal('0.0'))
            invoice_type = Transaction().context.get('invoice_type', 'out')
            pouamount = currency.round(untaxed_amount * self.ratio)
            if invoice_type == 'out':
                return pouamount * -1
            return pouamount
        return value


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'

    def get_move(self):
        with Transaction().set_context(untaxed_amount=self.untaxed_amount,
                invoice_type=self.type):
            return super(Invoice, self).get_move()
