import datetime
import unittest
from decimal import Decimal

from proteus import Model
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear, create_tax,
                                                 get_accounts)
from trytond.modules.account_invoice.tests.tools import \
    set_fiscalyear_invoice_sequences
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        today = datetime.date.today()

        # Install account_invoice
        activate_modules('account_invoice_maturity_base')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create tax
        tax = create_tax(Decimal('.10'))
        tax.save()

        # Set Cash journal
        Journal = Model.get('account.journal')
        journal_cash, = Journal.find([('type', '=', 'cash')])

        # Create party
        Party = Model.get('party.party')
        party = Party(name='Party')
        party.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.customer_taxes.append(tax)
        account_category.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'service'
        template.list_price = Decimal('40')
        template.account_category = account_category
        product, = template.products
        product.cost_price = Decimal('25')
        template.save()
        product, = template.products

        # Create payment term
        PaymentTerm = Model.get('account.invoice.payment_term')
        payment_term = PaymentTerm(name='Term')
        line = payment_term.lines.new(type='percent_on_untaxed_amount',
                                      ratio=Decimal('0.05'),
                                      divisor=Decimal('20.0'))
        line.relativedeltas.new(days=20)
        line = payment_term.lines.new(type='remainder')
        line.relativedeltas.new(days=40)
        payment_term.save()

        # Create customer invoice
        Invoice = Model.get('account.invoice')
        InvoiceLine = Model.get('account.invoice.line')
        invoice = Invoice()
        invoice.party = party
        invoice.payment_term = payment_term
        line = InvoiceLine()
        invoice.lines.append(line)
        line.product = product
        line.quantity = 5
        line.unit_price = Decimal('40')
        invoice.save()

        # Post customer invoice
        invoice.click('post')
        self.assertEqual(invoice.state, 'posted')
        invoice.reload()
        line1, line2, line3, line4 = sorted(invoice.move.lines,
                                            key=lambda x: (x.debit, x.credit))
        self.assertEqual(line1.debit, Decimal('0'))

        self.assertEqual(line1.credit, Decimal('20.00'))
        self.assertEqual(line2.debit, Decimal('0'))

        self.assertEqual(line2.credit, Decimal('200.00'))
        self.assertEqual(line3.debit, Decimal('10.00'))

        self.assertEqual(line3.credit, Decimal('0'))
        self.assertEqual(line4.debit, Decimal('210.00'))

        self.assertEqual(line4.credit, Decimal('0'))

        # Create supplier invoice
        invoice = Invoice()
        invoice.type = 'in'
        invoice.invoice_date = today
        invoice.party = party
        invoice.payment_term = payment_term
        line = InvoiceLine()
        invoice.lines.append(line)
        line.product = product
        line.quantity = 5
        line.unit_price = Decimal('25')
        invoice.save()

        # Post supplier invoice
        invoice.click('post')
        self.assertEqual(invoice.state, 'posted')
        line1, line2, line3 = sorted(invoice.move.lines,
                                     key=lambda x: (x.debit, x.credit))
        self.assertEqual(line1.debit, Decimal('0'))

        self.assertEqual(line1.credit, Decimal('6.25'))
        self.assertEqual(line2.debit, Decimal('0'))

        self.assertEqual(line2.credit, Decimal('118.75'))
        self.assertEqual(line3.debit, Decimal('125.00'))

        self.assertEqual(line3.credit, Decimal('0'))

        # Create customer credit note invoice
        invoice = Invoice()
        invoice.party = party
        invoice.payment_term = payment_term
        line = InvoiceLine()
        invoice.lines.append(line)
        line.product = product
        line.quantity = -5
        line.unit_price = Decimal('40')
        invoice.save()

        # Post customer credit invoice
        invoice.click('post')
        self.assertEqual(invoice.state, 'posted')
        line1, line2, line3, line4 = sorted(invoice.move.lines,
                                            key=lambda x: (x.debit, x.credit))
        self.assertEqual(line1.debit, Decimal('0'))

        self.assertEqual(line1.credit, Decimal('10.00'))
        self.assertEqual(line2.debit, Decimal('0'))

        self.assertEqual(line2.credit, Decimal('210.00'))
        self.assertEqual(line3.debit, Decimal('20.00'))

        self.assertEqual(line3.credit, Decimal('0'))
        self.assertEqual(line4.debit, Decimal('200.00'))

        self.assertEqual(line4.credit, Decimal('0'))
