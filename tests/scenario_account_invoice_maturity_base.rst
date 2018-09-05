==============================
Invoice Maturity Base Scenario
==============================

Imports::
    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences
    >>> today = datetime.date.today()

Install account_invoice::

    >>> config = activate_modules('account_invoice_maturity_base')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> account_tax = accounts['tax']
    >>> account_cash = accounts['cash']

Create tax::

    >>> tax = create_tax(Decimal('.10'))
    >>> tax.save()

Set Cash journal::

    >>> Journal = Model.get('account.journal')
    >>> journal_cash, = Journal.find([('type', '=', 'cash')])

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.save()

Create account category::

    >>> ProductCategory = Model.get('product.category')
    >>> account_category = ProductCategory(name="Account Category")
    >>> account_category.accounting = True
    >>> account_category.account_expense = expense
    >>> account_category.account_revenue = revenue
    >>> account_category.customer_taxes.append(tax)
    >>> account_category.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('40')
    >>> template.account_category = account_category
    >>> product, = template.products
    >>> product.cost_price = Decimal('25')
    >>> template.save()
    >>> product, = template.products

Create payment term::

    >>> PaymentTerm = Model.get('account.invoice.payment_term')
    >>> payment_term = PaymentTerm(name='Term')
    >>> line = payment_term.lines.new(type='percent_on_untaxed_amount',
    ...     ratio=Decimal('0.05'), divisor=Decimal('20.0'))
    >>> delta = line.relativedeltas.new(days=20)
    >>> line = payment_term.lines.new(type='remainder')
    >>> delta = line.relativedeltas.new(days=40)
    >>> payment_term.save()

Create customer invoice::

    >>> Invoice = Model.get('account.invoice')
    >>> InvoiceLine = Model.get('account.invoice.line')
    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> line = InvoiceLine()
    >>> invoice.lines.append(line)
    >>> line.product = product
    >>> line.quantity = 5
    >>> line.unit_price = Decimal('40')
    >>> invoice.save()

Post customer invoice::

    >>> invoice.click('post')
    >>> invoice.state
    'posted'
    >>> line1, line2, line3, line4 = invoice.move.lines
    >>> line1.debit, line1.credit
    (Decimal('210.00'), Decimal('0'))
    >>> line2.debit, line2.credit
    (Decimal('10.00'), Decimal('0'))
    >>> line3.debit, line3.credit
    (Decimal('0'), Decimal('20.00'))
    >>> line4.debit, line4.credit
    (Decimal('0'), Decimal('200.00'))

Create supplier invoice::

    >>> invoice = Invoice()
    >>> invoice.type = 'in'
    >>> invoice.invoice_date = today
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> line = InvoiceLine()
    >>> invoice.lines.append(line)
    >>> line.product = product
    >>> line.quantity = 5
    >>> line.unit_price = Decimal('25')
    >>> invoice.save()

Post supplier invoice::

    >>> invoice.click('post')
    >>> invoice.state
    'posted'
    >>> line1, line2, line3 = invoice.move.lines
    >>> line1.debit, line1.credit
    (Decimal('0'), Decimal('118.75'))
    >>> line2.debit, line2.credit
    (Decimal('0'), Decimal('6.25'))
    >>> line3.debit, line3.credit
    (Decimal('125.00'), Decimal('0'))

Create customer credit note invoice::

    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> line = InvoiceLine()
    >>> invoice.lines.append(line)
    >>> line.product = product
    >>> line.quantity = -5
    >>> line.unit_price = Decimal('40')
    >>> invoice.save()

Post customer credit invoice::

    >>> invoice.click('post')
    >>> invoice.state
    'posted'
    >>> line1, line2, line3, line4 = invoice.move.lines
    >>> line1.debit, line1.credit
    (Decimal('0'), Decimal('210.00'))
    >>> line2.debit, line2.credit
    (Decimal('0'), Decimal('10.00'))
    >>> line3.debit, line3.credit
    (Decimal('20.00'), Decimal('0'))
    >>> line4.debit, line4.credit
    (Decimal('200.00'), Decimal('0'))
