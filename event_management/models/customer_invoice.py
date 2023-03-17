# -*- coding: utf-8 -*-
"""Customer Invoice"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')
INTEGRITY_HASH_LINE_FIELDS = ('debit', 'credit', 'account_id', 'partner_id')
class AccountMove(models.Model):
    _inherit = "account.move"

    booking_id = fields.Many2one('event.management',required=True)
    auditorium_id = fields.Many2one('res.partner', related='booking_id.venue_id')
    fortuna_discount = fields.Float()
    auditorium_discount = fields.Float()
    address = fields.Text()
    total_advance = fields.Float()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)
    l10n_in_gst_treatment = fields.Selection([
            ('regular', 'Registered Business - Regular'),
            ('composition', 'Registered Business - Composition'),
            ('unregistered', 'Unregistered Business'),
            ('consumer', 'Consumer'),
            ('overseas', 'Overseas'),
            ('special_economic_zone', 'Special Economic Zone'),
            ('deemed_export', 'Deemed Export')
        ],default="unregistered", string="GST Treatment", compute="_compute_l10n_in_gst_treatment", store=True, readonly=False)
    number2 = fields.Char()
    payment_done = fields.Boolean()

    # total_advance = fields.Float(compute="_compute_total_advance_amount",store=True)
    # @api.depends('line_ids.advance')
    # def _compute_total_advance_amount(self):
    #     for move in self:
    #         move.total_advance=sum(move.line_ids.mapped('advance'))

    def action_pay_advance(self):
        for rec in self:
            if rec.total_advance > 0:
                # values = {
                #     'partner_type': 'customer',
                #     'date': fields.Date.today(),
                #     'destination_account_id': self.env['account.account'].search([('user_type_id.type', '=', 'receivable')],limit=1).id,
                #     'amount': rec.total_advance,
                #     'journal_id': self.env['account.journal'].search([('type', '=', 'cash')],limit=1).id,
                # }

                # values = {
                #     'communication':rec.name,
                #     'payment_date': fields.Date.today(),
                #     'destination_account_id': self.env['account.account'].search([('user_type_id.type', '=', 'receivable')],limit=1).id,
                #     'amount': rec.total_advance,
                #     'journal_id': self.env['account.journal'].search([('type', '=', 'cash')],limit=1).id,
                # }
                # self._context = {
                #     'active_model': 'account.move',
                #     'active_ids': rec.ids,
                # }
                # wizard = self.env['account.payment.register'].create(values)
                # print("Inside Functionnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")
                #
                # wizard._context = {
                #     'active_model': 'account.move',
                #     'active_ids': rec.ids,
                # }
                # # rec.action_register_payment
                # wizard.action_create_payments()
                # payment = self.env['account.payment'].create(values)
                # payment.reconciled_invoice_ids = [rec.id]
                if not rec.payment_done:
                    rec.payment_done = True
                if rec.payment_state == 'not_paid':
                    rec.payment_state = 'partial'
                if rec.state == 'draft':
                    rec.action_post()
        return

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'fortuna_discount',
        'total_advance')
    def _compute_amount(self):
        for move in self:
            if move.payment_state == 'invoicing_legacy':
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                move.payment_state = move.payment_state
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = move._get_lines_onchange_currency().currency_id

            for line in move.line_ids:
                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            # fortuna_discount = (sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)) * (move.fortuna_discount /100)
            move.amount_untaxed = (sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed))
            # move.amount_untaxed = (sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)) - (fortuna_discount+move.total_advance)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = (sign * (total_currency if len(currencies) == 1 else total)) - (move.total_advance)
            # move.amount_total = (sign * (total_currency if len(currencies) == 1 else total)) - (fortuna_discount+move.total_advance)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual) - (move.total_advance)
            move.amount_untaxed_signed = - total_untaxed
            move.amount_tax_signed = - total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies or move.company_id.currency_id

            # Compute 'payment_state'.
            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(include_receipts=True) and move.state == 'posted':

                if currency.is_zero(move.amount_residual):
                    reconciled_payments = move._get_reconciled_payments()
                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                        new_pmt_state = 'paid'
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                reverse_moves = self.env['account.move'].search([('reversed_entry_id', '=', move.id), ('state', '=', 'posted'), ('move_type', '=', reverse_type)])
                if self.env.company.tax_exigibility:
                    domain = [
                        ('tax_cash_basis_move_id', 'in', move.ids + reverse_moves.ids),
                        ('state', '=', 'posted'),
                        ('move_type', '=', 'entry')
                    ]
                    caba_moves = self.env['account.move'].search(domain)
                else:
                    caba_moves = self.env['account.move']

                # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                # We ignore potentials cash basis moves reconciled because the transition account of the tax is reconcilable
                reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (caba_moves + reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'

            move.payment_state = new_pmt_state



########################################################################################################################

    ## calculation with different discounts one after other


    # def _recompute_tax_lines(self, recompute_tax_base_amount=False, tax_rep_lines_to_recompute=None):
    #     """ Compute the dynamic tax lines of the journal entry.
    #
    #     :param recompute_tax_base_amount: Flag forcing only the recomputation of the `tax_base_amount` field.
    #     """
    #     self.ensure_one()
    #     in_draft_mode = self != self._origin
    #
    #     def _serialize_tax_grouping_key(grouping_dict):
    #         ''' Serialize the dictionary values to be used in the taxes_map.
    #         :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
    #         :return: A string representing the values.
    #         '''
    #         return '-'.join(str(v) for v in grouping_dict.values())
    #
    #     def _compute_base_line_taxes(base_line):
    #         ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
    #         amount_currency & balance could not be the same as the expected currency rate.
    #         The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
    #         :param base_line:   The account.move.line owning the taxes.
    #         :return:            The result of the compute_all method.
    #         '''
    #         move = base_line.move_id
    #
    #         if move.is_invoice(include_receipts=True):
    #             handle_price_include = True
    #             sign = -1 if move.is_inbound() else 1
    #             quantity = base_line.quantity
    #             is_refund = move.move_type in ('out_refund', 'in_refund')
    #             price_unit_wo_discount = sign * (base_line.price_unit * (1 - (base_line.discount / 100.0)))
    #         else:
    #             handle_price_include = False
    #             quantity = 1.0
    #             tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
    #             is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)
    #             price_unit_wo_discount = base_line.amount_currency
    #
    #         balance_taxes_res = base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
    #             price_unit_wo_discount,
    #             currency=base_line.currency_id,
    #             quantity=quantity,
    #             product=base_line.product_id,
    #             partner=base_line.partner_id,
    #             is_refund=is_refund,
    #             handle_price_include=handle_price_include,
    #         )
    #
    #         if move.move_type == 'entry':
    #             repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
    #             repartition_tags = base_line.tax_ids.flatten_taxes_hierarchy().mapped(repartition_field).filtered(lambda x: x.repartition_type == 'base').tag_ids
    #             tags_need_inversion = self._tax_tags_need_inversion(move, is_refund, tax_type)
    #             if tags_need_inversion:
    #                 balance_taxes_res['base_tags'] = base_line._revert_signed_tags(repartition_tags).ids
    #                 for tax_res in balance_taxes_res['taxes']:
    #                     tax_res['tag_ids'] = base_line._revert_signed_tags(self.env['account.account.tag'].browse(tax_res['tag_ids'])).ids
    #
    #         return balance_taxes_res
    #
    #     taxes_map = {}
    #
    #     # ==== Add tax lines ====
    #     to_remove = self.env['account.move.line']
    #     for line in self.line_ids.filtered('tax_repartition_line_id'):
    #         grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
    #         grouping_key = _serialize_tax_grouping_key(grouping_dict)
    #         if grouping_key in taxes_map:
    #             # A line with the same key does already exist, we only need one
    #             # to modify it; we have to drop this one.
    #             to_remove += line
    #         else:
    #             taxes_map[grouping_key] = {
    #                 'tax_line': line,
    #                 'amount': 0.0,
    #                 'tax_base_amount': 0.0,
    #                 'grouping_dict': False,
    #             }
    #     if not recompute_tax_base_amount:
    #         self.line_ids -= to_remove
    #
    #     # ==== Mount base lines ====
    #     for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
    #         # Don't call compute_all if there is no tax.
    #         if not line.tax_ids:
    #             if not recompute_tax_base_amount:
    #                 line.tax_tag_ids = [(5, 0, 0)]
    #             continue
    #
    #         compute_all_vals = _compute_base_line_taxes(line)
    #
    #         # Assign tags on base line
    #         if not recompute_tax_base_amount:
    #             line.tax_tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]
    #
    #         tax_exigible = True
    #         for tax_vals in compute_all_vals['taxes']:
    #             grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
    #             grouping_key = _serialize_tax_grouping_key(grouping_dict)
    #
    #             tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
    #             tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
    #
    #             if tax.tax_exigibility == 'on_payment':
    #                 tax_exigible = False
    #
    #             taxes_map_entry = taxes_map.setdefault(grouping_key, {
    #                 'tax_line': None,
    #                 'amount': 0.0,
    #                 'tax_base_amount': 0.0,
    #                 'grouping_dict': False,
    #             })
    #             taxes_map_entry['amount'] += tax_vals['amount']
    #             taxes_map_entry['tax_base_amount'] += self._get_base_amount_to_display(tax_vals['base'], tax_repartition_line, tax_vals['group'])
    #             taxes_map_entry['grouping_dict'] = grouping_dict
    #         if not recompute_tax_base_amount:
    #             line.tax_exigible = tax_exigible
    #
    #     # ==== Pre-process taxes_map ====
    #     taxes_map = self._preprocess_taxes_map(taxes_map)
    #
    #     # ==== Process taxes_map ====
    #     for taxes_map_entry in taxes_map.values():
    #         # The tax line is no longer used in any base lines, drop it.
    #         if taxes_map_entry['tax_line'] and not taxes_map_entry['grouping_dict']:
    #             if not recompute_tax_base_amount:
    #                 self.line_ids -= taxes_map_entry['tax_line']
    #             continue
    #
    #         currency = self.env['res.currency'].browse(taxes_map_entry['grouping_dict']['currency_id'])
    #
    #         # Don't create tax lines with zero balance.
    #         if currency.is_zero(taxes_map_entry['amount']):
    #             if taxes_map_entry['tax_line'] and not recompute_tax_base_amount:
    #                 self.line_ids -= taxes_map_entry['tax_line']
    #             continue
    #
    #         # tax_base_amount field is expressed using the company currency.
    #         tax_base_amount = currency._convert(taxes_map_entry['tax_base_amount'], self.company_currency_id, self.company_id, self.date or fields.Date.context_today(self))
    #
    #         # Recompute only the tax_base_amount.
    #         if recompute_tax_base_amount:
    #             if taxes_map_entry['tax_line']:
    #                 taxes_map_entry['tax_line'].tax_base_amount = tax_base_amount
    #             continue
    #
    #         balance = currency._convert(
    #             taxes_map_entry['amount'],
    #             self.company_currency_id,
    #             self.company_id,
    #             self.date or fields.Date.context_today(self),
    #         )
    #         to_write_on_line = {
    #             'amount_currency': taxes_map_entry['amount'],
    #             'currency_id': taxes_map_entry['grouping_dict']['currency_id'],
    #             'debit': balance > 0.0 and balance or 0.0,
    #             'credit': balance < 0.0 and -balance or 0.0,
    #             'tax_base_amount': tax_base_amount,
    #         }
    #
    #         if taxes_map_entry['tax_line']:
    #             # Update an existing tax line.
    #             if tax_rep_lines_to_recompute and taxes_map_entry['tax_line'].tax_repartition_line_id not in tax_rep_lines_to_recompute:
    #                 continue
    #
    #             taxes_map_entry['tax_line'].update(to_write_on_line)
    #         else:
    #             # Create a new tax line.
    #             create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
    #             tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
    #             tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
    #
    #             if tax_rep_lines_to_recompute and tax_repartition_line not in tax_rep_lines_to_recompute:
    #                 continue
    #
    #             tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
    #             taxes_map_entry['tax_line'] = create_method({
    #                 **to_write_on_line,
    #                 'name': tax.name,
    #                 'move_id': self.id,
    #                 'company_id': self.company_id.id,
    #                 'company_currency_id': self.company_currency_id.id,
    #                 'tax_base_amount': tax_base_amount,
    #                 'exclude_from_invoice_tab': True,
    #                 'tax_exigible': tax.tax_exigibility == 'on_invoice',
    #                 **taxes_map_entry['grouping_dict'],
    #             })
    #
    #         if in_draft_mode:
    #             taxes_map_entry['tax_line'].update(taxes_map_entry['tax_line']._get_fields_onchange_balance(force_computation=True))


#####################################################################################################

    @api.model
    def create(self, values):
        sequence_number = self.env['ir.sequence'].next_by_code('account.move.sequence')
        values['number2'] = sequence_number
        res = super(AccountMove,self).create(values)
        return res

    def write(self, vals):
        for record in self:
            if 'name' in vals:
                vals['name'] = record.number2
        #       print(vals['name'])
        return super(AccountMove,self).write(vals)

    # @api.multi
    # @api.depends('number2')
    # def name_get(self):
    #     result = []
    #     for account in self:
    #         name = account.number2
    #         result.append((account.id, name))
    #     return result
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    advance = fields.Float()
    fortuna_discount_line = fields.Float()
    auditorium_discount = fields.Float()
    price_subtotal_duplicate = fields.Float()
    #################################################################################################
    ## calculation with different discounts together

    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0, compute="_compute_total_discount",store=True )

    @api.depends('auditorium_discount','fortuna_discount_line')
    def _compute_total_discount(self):
        for rec in self:
            rec.discount = rec.fortuna_discount_line + rec.auditorium_discount
    # @api.depends('price_subtotal')
    # def _onchange_price_subtotal_duplicate(self):
    #     for rec in self:
    #         rec.price_subtotal_duplicate = rec.price_subtotal
    #         if rec.price_subtotal == 0:
    #             rec._get_price_total_and_subtotal()


    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
        self.ensure_one()
        discount = self.discount if discount is None else discount
        if not discount:
            discount = self.fortuna_discount_line + self.auditorium_discount
        return self._get_price_total_and_subtotal_model(
            price_unit=self.price_unit if price_unit is None else price_unit,
            quantity=self.quantity if quantity is None else quantity,
            discount=discount,
            currency=self.currency_id if currency is None else currency,
            product=self.product_id if product is None else product,
            partner=self.partner_id if partner is None else partner,
            taxes=self.tax_ids if taxes is None else taxes,
            move_type=self.move_id.move_type if move_type is None else move_type,
        )
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        for vals in vals_list:
            move = self.env['account.move'].browse(vals['move_id'])
            discount = vals.get('discount', 0.0)
            print (discount)
            if discount == 0 or not discount:
                vals['discount'] = vals.get('fortuna_discount_line',0.0) + vals.get('auditorium_discount',0.0)
                print("...........................vals['discount']")
                print(vals['discount'])
        lines = super(AccountMoveLine, self).create(vals_list)
        for line in lines:
            line.price_subtotal = line.quantity * (line.price_unit * (1 - (line.discount / 100.0)))
                # line.update(line._get_price_total_and_subtotal())
                # line.update(line._get_fields_onchange_subtotal())
        return lines

#################################################################################################

    # @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids', 'fortuna_discount_line', 'auditorium_discount', 'advance')
    # def _onchange_price_subtotal(self):
    #     for line in self:
    #         if not line.move_id.is_invoice(include_receipts=True):
    #             continue
    #
    #         line.update(line._get_price_total_and_subtotal())
    #         line.update(line._get_fields_onchange_subtotal())



#################################################################################################
    ## calculation with different discounts one after other



    #
    # def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, advance=None, fortuna_discount_line=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
    #     self.ensure_one()
    #     return self._get_price_total_and_subtotal_model(
    #         price_unit=self.price_unit if price_unit is None else price_unit,
    #         quantity=self.quantity if quantity is None else quantity,
    #         discount=self.discount if discount is None else discount,
    #         currency=self.currency_id if currency is None else currency,
    #         product=self.product_id if product is None else product,
    #         partner=self.partner_id if partner is None else partner,
    #         taxes=self.tax_ids if taxes is None else taxes,
    #         move_type=self.move_id.move_type if move_type is None else move_type,
    #         advance=self.advance if advance is None else advance,
    #         fortuna_discount_line=self.fortuna_discount_line if fortuna_discount_line is None else fortuna_discount_line,
    #
    #     )
    #
    #
    #
    # @api.model
    # def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, advance, fortuna_discount_line, currency, product, partner, taxes, move_type):
    #     ''' This method is used to compute 'price_total' & 'price_subtotal'.
    #
    #     :param price_unit:  The current price unit.
    #     :param quantity:    The current quantity.
    #     :param discount:    The current discount.
    #     :param currency:    The line's currency.
    #     :param product:     The line's product.
    #     :param partner:     The line's partner.
    #     :param taxes:       The applied taxes.
    #     :param move_type:   The type of the move.
    #     :return:            A dictionary containing 'price_subtotal' & 'price_total'.
    #     '''
    #     res = {}
    #
    #     # Compute 'price_subtotal'.
    #     line_discount_price_unit = (price_unit * (1 - (discount / 100.0)))*(1 - (fortuna_discount_line / 100.0))
    #
    #     subtotal = quantity * line_discount_price_unit
    #     # subtotal = (quantity * line_discount_price_unit) - advance
    #
    #     # Compute 'price_total'.
    #     if taxes:
    #         taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
    #             quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
    #         res['price_subtotal'] = taxes_res['total_excluded']
    #         res['price_total'] = taxes_res['total_included']
    #     else:
    #         res['price_total'] = res['price_subtotal'] = subtotal
    #     #In case of multi currency, round before it's use for computing debit credit
    #     if currency:
    #         res = {k: currency.round(v) for k, v in res.items()}
    #     return res
    # def _get_fields_onchange_balance(self, quantity=None, discount=None, advance=None, fortuna_discount_line=None, amount_currency=None, move_type=None, currency=None, taxes=None, price_subtotal=None, force_computation=False):
    #     self.ensure_one()
    #     return self._get_fields_onchange_balance_model(
    #         quantity=self.quantity if quantity is None else quantity,
    #         advance=self.advance if advance is None else advance,
    #         fortuna_discount_line=self.fortuna_discount_line if fortuna_discount_line is None else fortuna_discount_line,
    #         discount=self.discount if discount is None else discount,
    #         amount_currency=self.amount_currency if amount_currency is None else amount_currency,
    #         move_type=self.move_id.move_type if move_type is None else move_type,
    #         currency=(self.currency_id or self.move_id.currency_id) if currency is None else currency,
    #         taxes=self.tax_ids if taxes is None else taxes,
    #         price_subtotal=self.price_subtotal if price_subtotal is None else price_subtotal,
    #         force_computation=force_computation,
    #     )
    #
    #
    # @api.model
    # def _get_fields_onchange_balance_model(self, quantity, discount, advance, fortuna_discount_line, amount_currency, move_type, currency, taxes, price_subtotal, force_computation=False):
    #     ''' This method is used to recompute the values of 'quantity', 'discount', 'price_unit' due to a change made
    #     in some accounting fields such as 'balance'.
    #
    #     This method is a bit complex as we need to handle some special cases.
    #     For example, setting a positive balance with a 100% discount.
    #
    #     :param quantity:        The current quantity.
    #     :param discount:        The current discount.
    #     :param amount_currency: The new balance in line's currency.
    #     :param move_type:       The type of the move.
    #     :param currency:        The currency.
    #     :param taxes:           The applied taxes.
    #     :param price_subtotal:  The price_subtotal.
    #     :return:                A dictionary containing 'quantity', 'discount', 'price_unit'.
    #     '''
    #     if move_type in self.move_id.get_outbound_types():
    #         sign = 1
    #     elif move_type in self.move_id.get_inbound_types():
    #         sign = -1
    #     else:
    #         sign = 1
    #     amount_currency *= sign
    #
    #     print("Fortuna Discount*****************************************************************************" )
    #     print(fortuna_discount_line)
    #     # Avoid rounding issue when dealing with price included taxes. For example, when the price_unit is 2300.0 and
    #     # a 5.5% price included tax is applied on it, a balance of 2300.0 / 1.055 = 2180.094 ~ 2180.09 is computed.
    #     # However, when triggering the inverse, 2180.09 + (2180.09 * 0.055) = 2180.09 + 119.90 = 2299.99 is computed.
    #     # To avoid that, set the price_subtotal at the balance if the difference between them looks like a rounding
    #     # issue.
    #     if not force_computation and currency.is_zero(amount_currency - price_subtotal):
    #         return {}
    #
    #     taxes = taxes.flatten_taxes_hierarchy()
    #     if taxes and any(tax.price_include for tax in taxes):
    #         # Inverse taxes. E.g:
    #         #
    #         # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
    #         # -----------------------------------------------------------------------------------
    #         # 110           | 10% incl, 5%  |                   | 100               | 115
    #         # 10            |               | 10% incl          | 10                | 10
    #         # 5             |               | 5%                | 5                 | 5
    #         #
    #         # When setting the balance to -200, the expected result is:
    #         #
    #         # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
    #         # -----------------------------------------------------------------------------------
    #         # 220           | 10% incl, 5%  |                   | 200               | 230
    #         # 20            |               | 10% incl          | 20                | 20
    #         # 10            |               | 5%                | 10                | 10
    #         force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
    #         taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(amount_currency, currency=currency, handle_price_include=False)
    #         for tax_res in taxes_res['taxes']:
    #             tax = self.env['account.tax'].browse(tax_res['id'])
    #             if tax.price_include:
    #                 amount_currency += tax_res['amount']
    #
    #     discount_factor = 1 - (discount / 100.0)
    #     if amount_currency and discount_factor:
    #         # discount != 100%
    #         vals = {
    #             'quantity': quantity or 1.0,
    #             'fortuna_discount_line':fortuna_discount_line,
    #             # 'price_unit': amount_currency / discount_factor / (quantity or 1.0),
    #         }
    #     elif amount_currency and not discount_factor:
    #         # discount == 100%
    #         vals = {
    #             'quantity': quantity or 1.0,
    #             'discount': 0.0,
    #             'fortuna_discount_line':fortuna_discount_line,
    #             # 'price_unit': amount_currency / (quantity or 1.0),
    #         }
    #     elif not discount_factor:
    #         # balance of line is 0, but discount  == 100% so we display the normal unit_price
    #         vals = {}
    #     else:
    #         # balance is 0, so unit price is 0 as well
    #         vals = {'price_unit': 0.0}
    #     return vals
    #
    # @api.model_create_multi
    # def create(self, vals_list):
    #     # OVERRIDE
    #     ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
    #     BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids','fortuna_discount_line')
    #
    #     for vals in vals_list:
    #         move = self.env['account.move'].browse(vals['move_id'])
    #         vals.setdefault('company_currency_id', move.company_id.currency_id.id) # important to bypass the ORM limitation where monetary fields are not rounded; more info in the commit message
    #
    #         # Ensure balance == amount_currency in case of missing currency or same currency as the one from the
    #         # company.
    #         currency_id = vals.get('currency_id') or move.company_id.currency_id.id
    #         if currency_id == move.company_id.currency_id.id:
    #             balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
    #             vals.update({
    #                 'currency_id': currency_id,
    #                 'amount_currency': balance,
    #             })
    #         else:
    #             vals['amount_currency'] = vals.get('amount_currency', 0.0)
    #
    #         if move.is_invoice(include_receipts=True):
    #             currency = move.currency_id
    #             partner = self.env['res.partner'].browse(vals.get('partner_id'))
    #             taxes = self.new({'tax_ids': vals.get('tax_ids', [])}).tax_ids
    #             tax_ids = set(taxes.ids)
    #             taxes = self.env['account.tax'].browse(tax_ids)
    #
    #             # Ensure consistency between accounting & business fields.
    #             # As we can't express such synchronization as computed fields without cycling, we need to do it both
    #             # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
    #             # business [resp. accounting] fields are recomputed.
    #             if any(vals.get(field) for field in ACCOUNTING_FIELDS):
    #                 price_subtotal = self._get_price_total_and_subtotal_model(
    #                     vals.get('price_unit', 0.0),
    #                     vals.get('quantity', 0.0),
    #                     vals.get('discount', 0.0),
    #                     vals.get('advance', 0.0),
    #                     vals.get('fortuna_discount_line', 0.0),
    #                     currency,
    #                     self.env['product.product'].browse(vals.get('product_id')),
    #                     partner,
    #                     taxes,
    #                     move.move_type,
    #                 ).get('price_subtotal', 0.0)
    #                 vals.update(self._get_fields_onchange_balance_model(
    #                     vals.get('quantity', 0.0),
    #                     vals.get('discount', 0.0),
    #                     vals.get('advance', 0.0),
    #                     vals.get('fortuna_discount_line', 0.0),
    #                     vals['amount_currency'],
    #                     move.move_type,
    #                     currency,
    #                     taxes,
    #                     price_subtotal
    #                 ))
    #                 vals.update(self._get_price_total_and_subtotal_model(
    #                     vals.get('price_unit', 0.0),
    #                     vals.get('quantity', 0.0),
    #                     vals.get('discount', 0.0),
    #                     vals.get('advance', 0.0),
    #                     vals.get('fortuna_discount_line', 0.0),
    #                     currency,
    #                     self.env['product.product'].browse(vals.get('product_id')),
    #                     partner,
    #                     taxes,
    #                     move.move_type,
    #                 ))
    #             elif any(vals.get(field) for field in BUSINESS_FIELDS):
    #                 vals.update(self._get_price_total_and_subtotal_model(
    #                     vals.get('price_unit', 0.0),
    #                     vals.get('quantity', 0.0),
    #                     vals.get('discount', 0.0),
    #                     vals.get('advance', 0.0),
    #                     vals.get('fortuna_discount_line', 0.0),
    #                     currency,
    #                     self.env['product.product'].browse(vals.get('product_id')),
    #                     partner,
    #                     taxes,
    #                     move.move_type,
    #                 ))
    #                 vals.update(self._get_fields_onchange_subtotal_model(
    #                     vals['price_subtotal'],
    #                     move.move_type,
    #                     currency,
    #                     move.company_id,
    #                     move.date,
    #                 ))
    #
    #     lines = super(AccountMoveLine, self).create(vals_list)
    #     return lines
    # def write(self, vals):
    #     # OVERRIDE
    #     ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
    #     BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')
    #     PROTECTED_FIELDS_TAX_LOCK_DATE = ['debit', 'credit', 'tax_line_id', 'tax_ids', 'tax_tag_ids']
    #     PROTECTED_FIELDS_LOCK_DATE = PROTECTED_FIELDS_TAX_LOCK_DATE + ['account_id', 'journal_id', 'amount_currency', 'currency_id', 'partner_id']
    #     PROTECTED_FIELDS_RECONCILIATION = ('account_id', 'date', 'debit', 'credit', 'amount_currency', 'currency_id')
    #
    #     account_to_write = self.env['account.account'].browse(vals['account_id']) if 'account_id' in vals else None
    #
    #     # Check writing a deprecated account.
    #     if account_to_write and account_to_write.deprecated:
    #         raise UserError(_('You cannot use a deprecated account.'))
    #
    #     for line in self:
    #         if line.parent_state == 'posted':
    #             if line.move_id.restrict_mode_hash_table and set(vals).intersection(INTEGRITY_HASH_LINE_FIELDS):
    #                 raise UserError(_("You cannot edit the following fields due to restrict mode being activated on the journal: %s.") % ', '.join(INTEGRITY_HASH_LINE_FIELDS))
    #             if any(key in vals for key in ('tax_ids', 'tax_line_id')):
    #                 raise UserError(_('You cannot modify the taxes related to a posted journal item, you should reset the journal entry to draft to do so.'))
    #
    #         # Check the lock date.
    #         if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_LOCK_DATE):
    #             line.move_id._check_fiscalyear_lock_date()
    #
    #         # Check the tax lock date.
    #         if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_TAX_LOCK_DATE):
    #             line._check_tax_lock_date()
    #
    #         # Check the reconciliation.
    #         if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_RECONCILIATION):
    #             line._check_reconciliation()
    #
    #         # Check switching receivable / payable accounts.
    #         if account_to_write:
    #             account_type = line.account_id.user_type_id.type
    #             if line.move_id.is_sale_document(include_receipts=True):
    #                 if (account_type == 'receivable' and account_to_write.user_type_id.type != account_type) \
    #                         or (account_type != 'receivable' and account_to_write.user_type_id.type == 'receivable'):
    #                     raise UserError(_("You can only set an account having the receivable type on payment terms lines for customer invoice."))
    #             if line.move_id.is_purchase_document(include_receipts=True):
    #                 if (account_type == 'payable' and account_to_write.user_type_id.type != account_type) \
    #                         or (account_type != 'payable' and account_to_write.user_type_id.type == 'payable'):
    #                     raise UserError(_("You can only set an account having the payable type on payment terms lines for vendor bill."))
    #
    #     # Tracking stuff can be skipped for perfs using tracking_disable context key
    #     if not self.env.context.get('tracking_disable', False):
    #         # Get all tracked fields (without related fields because these fields must be manage on their own model)
    #         tracking_fields = []
    #         for value in vals:
    #             field = self._fields[value]
    #             if hasattr(field, 'related') and field.related:
    #                 continue # We don't want to track related field.
    #             if hasattr(field, 'tracking') and field.tracking:
    #                 tracking_fields.append(value)
    #         ref_fields = self.env['account.move.line'].fields_get(tracking_fields)
    #
    #         # Get initial values for each line
    #         move_initial_values = {}
    #         for line in self.filtered(lambda l: l.move_id.posted_before): # Only lines with posted once move.
    #             for field in tracking_fields:
    #                 # Group initial values by move_id
    #                 if line.move_id.id not in move_initial_values:
    #                     move_initial_values[line.move_id.id] = {}
    #                 move_initial_values[line.move_id.id].update({field: line[field]})
    #
    #     result = True
    #     for line in self:
    #         cleaned_vals = line.move_id._cleanup_write_orm_values(line, vals)
    #         if not cleaned_vals:
    #             continue
    #
    #         # Auto-fill amount_currency if working in single-currency.
    #         if 'currency_id' not in cleaned_vals \
    #             and line.currency_id == line.company_currency_id \
    #             and any(field_name in cleaned_vals for field_name in ('debit', 'credit')):
    #             cleaned_vals.update({
    #                 'amount_currency': vals.get('debit', 0.0) - vals.get('credit', 0.0),
    #             })
    #
    #         result |= super(AccountMoveLine, line).write(cleaned_vals)
    #
    #         if not line.move_id.is_invoice(include_receipts=True):
    #             continue
    #
    #         # Ensure consistency between accounting & business fields.
    #         # As we can't express such synchronization as computed fields without cycling, we need to do it both
    #         # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
    #         # business [resp. accounting] fields are recomputed.
    #         if any(field in cleaned_vals for field in ACCOUNTING_FIELDS):
    #             price_subtotal = line._get_price_total_and_subtotal().get('price_subtotal', 0.0)
    #             to_write = line._get_fields_onchange_balance(price_subtotal=price_subtotal)
    #             to_write.update(line._get_price_total_and_subtotal(
    #                 price_unit=to_write.get('price_unit', line.price_unit),
    #                 quantity=to_write.get('quantity', line.quantity),
    #                 discount=to_write.get('discount', line.discount),
    #                 advance=to_write.get('advance', line.advance),
    #                 fortuna_discount_line=to_write.get('fortuna_discount_line', line.fortuna_discount_line),
    #             ))
    #             print("Inside write function.....................")
    #             result |= super(AccountMoveLine, line).write(to_write)
    #         elif any(field in cleaned_vals for field in BUSINESS_FIELDS):
    #             to_write = line._get_price_total_and_subtotal()
    #             to_write.update(line._get_fields_onchange_subtotal(
    #                 price_subtotal=to_write['price_subtotal'],
    #             ))
    #             result |= super(AccountMoveLine, line).write(to_write)
    #
    #     # Check total_debit == total_credit in the related moves.
    #     if self._context.get('check_move_validity', True):
    #         self.mapped('move_id')._check_balanced()
    #
    #     self.mapped('move_id')._synchronize_business_models({'line_ids'})
    #
    #     if not self.env.context.get('tracking_disable', False):
    #         # Create the dict for the message post
    #         tracking_values = {}  # Tracking values to write in the message post
    #         for move_id, modified_lines in move_initial_values.items():
    #             tmp_move = {move_id: []}
    #             for line in self.filtered(lambda l: l.move_id.id == move_id):
    #                 changes, tracking_value_ids = line._mail_track(ref_fields, modified_lines)  # Return a tuple like (changed field, ORM command)
    #                 if tracking_value_ids:
    #                     for value in tracking_value_ids:
    #                         selected_field = value[2]  # Get the last element of the tuple in the list of ORM command. (changed, [(0, 0, THIS)])
    #                         tmp_move[move_id].append({
    #                             'line_id': line.id,
    #                             **{'field_name': selected_field.get('field_desc')},
    #                             **self._get_formated_values(selected_field)
    #                         })
    #                 elif changes:
    #                     for change in changes:
    #                         field_name = line._fields[change].string  # Get the field name
    #                         tmp_move[move_id].append({
    #                             'line_id': line.id,
    #                             'error': True,
    #                             'field_error': field_name,
    #                         })
    #                 else:
    #                     continue
    #             if len(tmp_move[move_id]) > 0:
    #                 tracking_values.update(tmp_move)
    #
    #         # Write in the chatter.
    #         for move in self.mapped('move_id'):
    #             fields = tracking_values.get(move.id, [])
    #             if len(fields) > 0:
    #                 msg = self._get_tracking_field_string(tracking_values.get(move.id))
    #                 move.message_post(body=msg)  # Write for each concerned move the message in the chatter
    #
    #     return result

######################################################################################################################



class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False,
        compute='_compute_amount_duplicate')

    def _compute_amount_duplicate(self):
        for rec in self:
            lines = self.line_ids._origin
            print("lines////////////////////.............................")
            print(lines)
            print("self._active_id..............")
            print(self._active_id)
            print("self._context..............")
            print(self._context)
            rec.amount = 0
