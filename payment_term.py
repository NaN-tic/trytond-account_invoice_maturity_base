# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from decimal import Decimal


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
        value = super().get_value(remainder, amount, currency)
        if self.type == 'percent_on_untaxed_amount':
            untaxed_amount = Transaction().context.get('untaxed_amount', Decimal(0))
            pouamount = currency.round(untaxed_amount * self.ratio)
            return pouamount
        return value


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'

    def get_move(self):
        with Transaction().set_context(untaxed_amount=self.untaxed_amount,
                invoice_type=self.type):
            return super().get_move()
