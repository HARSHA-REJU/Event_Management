# -*- coding: utf-8 -*-
"""Event Management"""

from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class FacilitiesEvent(models.Model):
    _name = 'facility.event'

    product_id = fields.Many2one('product.product', string="Facility")
    facility_id2 = fields.Many2one('event.management', string="Facility")
    price = fields.Float('Price')
    quantity = fields.Float('Nos', default=1)
    total = fields.Float('Total', compute="_compute_total")

    @api.depends("total", "price", "quantity")
    def _compute_total(self):
        for rec in self:
            print("inside compute")
            rec.total = rec.price * rec.quantity


class EventManagement(models.Model):
    """Model for managing Event Management"""
    _name = 'event.management'

    name = fields.Char('Name', readonly=True, copy=False)
    ref = fields.Char(string='Ref', readonly=True)
    type_of_event_id = fields.Many2one('event.management.type', string="Type",
                                       required=True)
    venue_id = fields.Many2one('res.partner', domain=[('venue', '=', True)], string="Venue", required=True)
    rent = fields.Float('Amount')
    makeup_id = fields.Many2one('artist.artist', string="Makeup Arist")
    package_id = fields.Many2one('makeup.package', string="Package")
    makeup_rate = fields.Float('Amount')
    mehndi_id = fields.Many2one('artist.artist', string="Mehndi Arist")
    mehndi_package_id = fields.Many2one('makeup.package', string="Package")
    mehndi_rate = fields.Float('Amount')
    photography_id = fields.Many2one('photographer.photographer', string="Photography")
    photography_package_id = fields.Many2one('makeup.package', string="Package")
    photography_rate = fields.Float('Amount')
    caterers_id = fields.Many2one('cater.cater', string="Caterers Name")
    catering_package_id = fields.Many2one('makeup.package', string="Package")
    catering_rate = fields.Float('Rate/Plate')
    no_people = fields.Integer('Serving For(Nos)')
    total_amt = fields.Float('Amount')
    entert_id = fields.Many2one('entertainer.entertainer', string="Entertainer")
    entert_package_id = fields.Many2one('makeup.package', string="Package")
    entert_rate = fields.Float('Amount')
    grand_total = fields.Float('Grand Total')
    compute_field = fields.Char(compute="_compute_total_rate")
    compute_field2 = fields.Char(compute="_compute_grand_rate")

    @api.onchange('makeup_id')
    def onchange_packages_id(self):
        partner_id = self.env['makeup.package'].search([('package_by', '=', self.makeup_id.artist_name.id)])
        return {'domain': {'package_id': [('id', '=', partner_id.ids)]}}

    @api.onchange('package_id')
    def onchange_pack_id(self):
        for rec in self:
            rec.makeup_rate = rec.package_id.rate

    @api.onchange('mehndi_id')
    def onchange_mehndi_id(self):
        partner_id = self.env['makeup.package'].search([('package_by', '=', self.mehndi_id.artist_name.id)])
        return {'domain': {'mehndi_package_id': [('id', '=', partner_id.ids)]}}

    @api.onchange('mehndi_package_id')
    def onchange_meh_id(self):
        for rec in self:
            rec.mehndi_rate = rec.mehndi_package_id.rate

    @api.onchange('photography_id')
    def onchange_photo_id(self):
        partner_id = self.env['makeup.package'].search([('package_by', '=', self.photography_id.photography_name.id)])
        return {'domain': {'photography_package_id': [('id', '=', partner_id.ids)]}}

    @api.onchange('photography_package_id')
    def onchange_photography_id(self):
        for rec in self:
            rec.photography_rate = rec.photography_package_id.rate

    @api.onchange('caterers_id')
    def onchange_cater_id(self):
        partner_id = self.env['makeup.package'].search([('package_by', '=', self.caterers_id.cater_name.id)])
        return {'domain': {'catering_package_id': [('id', '=', partner_id.ids)]}}

    @api.onchange('catering_package_id')
    def onchange_catering_id(self):
        for rec in self:
            rec.catering_rate = rec.catering_package_id.rate

    @api.onchange('catering_rate', 'no_people', 'total_amt', 'rent', 'makeup_rate', 'mehndi_rate', 'photography_rate',
                  'entert_rate')
    def _compute_total_rate(self):
        for rec in self:
            rec.total_amt = rec.catering_rate * rec.no_people
            # rec.grand_total = rec.rent + rec.makeup_rate + rec.mehndi_rate + rec.photography_rate + rec.entert_rate

    @api.onchange('entert_id')
    def onchange_entert_id(self):
        partner_id = self.env['makeup.package'].search([('package_by', '=', self.entert_id.entertainer_name.id)])
        return {'domain': {'entert_package_id': [('id', '=', partner_id.ids)]}}

    @api.onchange('entert_package_id')
    def onchange_entertainment_id(self):
        for rec in self:
            rec.entert_rate = rec.entert_package_id.rate

    # venue_id = fields.Many2one('artist.a', domain=[('venue','=',True)], string="Venue", required=True)
    # venue_id = fields.Many2one('res.partner', domain=[('venue','=',True)], string="Venue", required=True)
    place_id = fields.Many2one('place.place', string="Place", required=True)
    partner_id = fields.Many2one('res.partner', string="Customer",
                                 required=True)
    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    event_date = fields.Date(string="Event Date", default=fields.Date.today, required=True)
    start_date = fields.Datetime(string="Start date",
                                 default=lambda self: fields.datetime.now(),
                                 )
    end_date = fields.Datetime(string="End date")
    service_line_ids = fields.One2many('event.service.line', 'event_id',
                                       string="Services")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('invoice', 'Invoiced'),
                              ('close', 'Close'), ('cancel', 'Canceled')],
                             string="State", default="draft")
    note = fields.Text('Terms and conditions')
    price_subtotal = fields.Float(string='Total',
                                  compute='_compute_price_subtotal',
                                  readonly=True, store=True)
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as image for "
                               "the event, limited to 1080x720px.")
    currency_id = fields.Many2one('res.currency', readonly=True,
                                  default=lambda self:
                                  self.env.user.company_id.currency_id)
    invoice_count = fields.Integer(string='# of Invoices')
    invoice_ids = fields.Many2many("account.move", string='Invoices',
                                   copy=False)
    pending_invoice = fields.Boolean(string="Invoice Pending",
                                     compute='_compute_pending_invoice')
    district_id = fields.Many2one('place.district')
    facility_ids = fields.Many2many('product.product')
    facilities_ids2 = fields.One2many('facility.event', 'facility_id2')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)

    @api.onchange('total_amt', 'rent', 'makeup_rate', 'mehndi_rate', 'photography_rate',
                  'entert_rate','catering_rate','no_people')
    def _compute_grand_rate(self):
        sum = 0
        for rec in self:
            sum = rec.rent + rec.makeup_rate + rec.mehndi_rate + rec.photography_rate + rec.entert_rate+rec.total_amt
            rec.grand_total = sum
    @api.onchange('district_id')
    def onchange_district_id(self):
        if self.district_id:
            return {'domain': {'place_id': [('district_id', '=', self.district_id.id)]}}

    @api.onchange('place_id')
    def onchange_place_id(self):
        if self.place_id:
            return {'domain': {'venue_id': [('place_id', '=', self.place_id.id)]}} \
 \
    # @api.onchange('venue_id')
    # def onchange_venue_id(self):
    #     if self.venue_id:
    #         self.place_id = self.venue_id.place_id
    #         self.district_id = self.venue_id.district_id

    @api.depends('service_line_ids', 'service_line_ids.state')
    def _compute_pending_invoice(self):
        pending = 0
        for lines in self.service_line_ids:
            if lines.invoiced is False and lines.state == "done":
                pending = 1
        if pending == 1:
            self.pending_invoice = True
        else:
            self.pending_invoice = False

    @api.depends('service_line_ids', 'service_line_ids.amount')
    def _compute_price_subtotal(self):
        total = 0
        for items in self.service_line_ids:
            total += items.amount
        self.price_subtotal = total

    @api.model
    def create(self, values):
        """Crete method for sequencing and checking dates while creating"""
        # start_date = values['start_date']
        # end_date = values['end_date']
        partner_name = self.env['res.partner'].browse(values['partner_id']).name
        event_name = self.env['event.management.type'].browse(
            values['type_of_event_id']).name
        # if start_date >= end_date:
        #     raise UserError(_('Start date must be less than End date'))

        name = '%s-%s-%s' % (partner_name, event_name, values['date'])
        values['name'] = name
        sequence_code = 'event.order.sequence'
        sequence_number = self.env['ir.sequence'].next_by_code(sequence_code)
        values['ref'] = sequence_number
        res = super(EventManagement, self).create(values)
        return res

    def action_event_confirm(self):
        """Button action to confirm"""
        self.state = "confirm"
        # Create other service bookins
        if self.makeup_id:
            makeup_artist_id = self.env['makeup.artist'].create({
                'makeup_artist':True,
                'customer_name':self.partner_id.id,
                'date':self.date,
                'booking_date':self.event_date,
                'type_of_event_id': self.type_of_event_id.id,
                'artist_name':self.makeup_id.id,
                'package':self.package_id.id,
                'rate':self.makeup_rate,
                'service_id':self.package_id.package_services_ids,
            })
            # print("makeup artist booked from event page")
        if self.mehndi_id:
            mehndi_artist_id = self.env['makeup.artist'].create({
                'mehndi_artist': True,
                'customer_name': self.partner_id.id,
                'date': self.date,
                'booking_date': self.event_date,
                'type_of_event_id': self.type_of_event_id.id,
                'artist_name': self.mehndi_id.id,
                'package': self.mehndi_package_id.id,
                'rate': self.mehndi_rate,
                'service_id': self.mehndi_package_id.package_services_ids,
            })
        if self.photography_id:
            photo_artist_id = self.env['book.photography'].create({
                'customer_name': self.partner_id.id,
                'date': self.date,
                'booking_date': self.event_date,
                'type_of_event_id': self.type_of_event_id.id,
                'artist_name': self.photography_id.id,
                'package': self.photography_package_id.id,
                'rate': self.photography_rate,
                'service_id': self.photography_package_id.package_services_ids,
            })
        if self.caterers_id:
            catering_id = self.env['book.cater'].create({
                'customer_name': self.partner_id.id,
                'date': self.date,
                'booking_date': self.event_date,
                'type_of_event_id': self.type_of_event_id.id,
                'artist_name': self.caterers_id.id,
                'package': self.catering_package_id.id,
                'rate': self.catering_rate,
                'total':self.total_amt,
                'number_of_plate':self.no_people,
                'service_id': self.catering_package_id.package_services_ids,
            })
        if self.entert_id:
            enter_id = self.env['book.entertainer'].create({
                'customer_name': self.partner_id.id,
                'date': self.date,
                'booking_date': self.event_date,
                'type_of_event_id': self.type_of_event_id.id,
                'artist_name': self.entert_id.id,
                'package': self.entert_package_id.id,
                'rate': self.entert_rate,
                'service_id': self.entert_package_id.package_services_ids,
            })






    def action_event_invoice(self):
        # vals = {
        #     'name': 'Customer Invoices - Test',
        #     'code': 'TINV',
        #     'type': 'sale',
        #     # 'default_account_id': a_sale.id,
        #     'refund_sequence': True,
        #
        # }
        # self.env['account.journal'].create(vals)
        vals = []
        a_sale = self.env['account.account'].search([])
        # a_sale = self.env['account.account'].create({
        #     'code': 'X2020',
        #     'name': 'Product Sales - (test)',
        #     'user_type_id': self.env.ref('account.data_account_type_revenue').id,
        # })
        for rec in self.facilities_ids2:
            dict = {

                'product_id': rec.product_id.id,
                'name': rec.product_id.name,
                'price_unit': rec.price,
                'quantity': rec.quantity,

            }
            vals.append((0, 0, dict))
        invoice_id = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'date': self.date,
            'partner_id': self.partner_id.id,
            'invoice_date': self.date,
            # 'account': a_sale.id,
            'invoice_line_ids': vals,
        })
        return {
            'name': _('Invoice'),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'res_id': invoice_id.id,
            'target': 'current',
        }

        # move = self.env['account.move'].create({
        #     'move_type': 'in_invoice',
        #     'date': self.date,
        #     'partner_id': self.partner_id.id,
        #     'invoice_date': self.date,
        #     # 'currency_id': self.currency_data['currency'].id,
        #     # 'invoice_payment_term_id': self.pay_terms_a.id,
        #     'invoice_line_ids': [
        #         (0, None, {
        #             'name': self.product_id.name,
        #             'product_id': self.product_id.id,
        #             # 'product_uom_id': self.product_line_vals_1['product_uom_id'],
        #             'quantity': self.quantity,
        #             'price_unit': self.price,
        #             # 'tax_ids': self.product_line_vals_1['tax_ids'],
        #         }),
        #         (0, None, {
        #             'name': self.product_line_vals_2['name'],
        #             'product_id': self.product_line_vals_2['product_id'],
        #             'product_uom_id': self.product_line_vals_2['product_uom_id'],
        #             'quantity': self.product_line_vals_2['quantity'],
        #             'price_unit': self.product_line_vals_2['price_unit'],
        #             'tax_ids': self.product_line_vals_2['tax_ids'],
        #
        #         }),
        #
        #     ]
        # })

    def action_event_cancel(self):
        """Button action to cancel"""
        self.state = "cancel"

    def action_event_close(self):
        """Button action to close"""
        pending = 0
        for lines in self.service_line_ids:
            if lines.invoiced is False:
                pending = 1
        if pending == 1:
            raise ValidationError(_('You can close an event only when all '
                                    'services is Done and Invoiced'))
        else:
            self.state = "close"

    def action_view_invoice_event(self):
        """Button action to View the related invoice"""
        invoices = self.mapped('invoice_ids')
        action = self.env.ref(
            'account.action_move_out_invoice_type').sudo().read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [
                (self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_event_invoice_create(self):
        """Button action to create related invoice"""
        product_line = []
        payment_list = []
        for line in self.service_line_ids:
            if line.invoiced is False and line.state == "done":
                product_line.append({'product_id': line.related_product_id,
                                     'price_unit': line.amount})
                line.invoiced = True
        if len(product_line) > 0:
            invoice = self.env['account.move']
            move_type = 'out_invoice'
            invoice = invoice.with_context(default_move_type=move_type)
            journal_id = invoice._compute_journal_id()
            company_id = self.env.user.company_id.id
            inv_obj = self.env['account.move']
            partner = self.partner_id
            for records in product_line:
                product_id = records['product_id']
                price_unit = records['price_unit']
                if product_id.property_account_income_id.id:
                    income_account = product_id.property_account_income_id.id
                elif product_id.categ_id.property_account_income_categ_id.id:
                    income_account = product_id.categ_id.property_account_income_categ_id.id
                else:
                    raise UserError(
                        _('Please define income account for'
                          ' this product: "%s" (id:%d).') % (
                            product_id.name, product_id.id))

                inv_line_data = {
                    'name': self.name,
                    'account_id': income_account,
                    'price_unit': price_unit,
                    'quantity': 1,
                    'product_id': product_id.id,
                    'product_uom_id': product_id.uom_id.id,
                }
                payment_list.append((0, 0, inv_line_data))
            inv_data = {
                'move_type': move_type,
                'ref': self.name,
                'bank_partner_id': partner.property_account_payable_id.id,
                'partner_id': partner.id,
                'payment_reference': self.name,
                'company_id': company_id,
                'invoice_line_ids': payment_list,
            }
            inv_id = inv_obj.create(inv_data)
            result = {
                'view_type': 'form',
                'res_model': 'account.move',
                'res_id': inv_id.id,
                'view_id': False,
                'view_mode': 'form',
                'type': 'ir.actions.act_window'
            }
            self.state = "invoice"
            all_invoice_ids = self.invoice_ids.ids
            all_invoice_ids.append(inv_id.id)
            self.update({'invoice_ids': all_invoice_ids,
                         'invoice_count': self.invoice_count + 1})
            return result


class EventServiceLine(models.Model):
    """Model to manage the service lines of the event management"""
    _name = 'event.service.line'

    service = fields.Many2one('event.services', string="Services",
                              required=True)
    # service = fields.Selection([('none', 'None')], string="Services",
    #                            required=True)
    event_id = fields.Many2one('event.management', string="Event")
    date_from = fields.Datetime(string="Date from", required=True)
    date_to = fields.Datetime(string="Date to", required=True)
    amount = fields.Float(string="Amount")
    state = fields.Selection([('done', 'Done'), ('pending', 'Pending')],
                             string="State", default="pending",
                             )
    currency_id = fields.Many2one('res.currency', readonly=True,
                                  default=lambda self:
                                  self.env.user.company_id.currency_id)
    invoiced = fields.Boolean(string="Invoiced", readonly=True)
    related_product_id = fields.Many2one('product.product',
                                         string="Related Product")

    _sql_constraints = [('event_supplier_unique', 'unique(event_id, service)',
                         'Duplication Of Service In The Service Lines '
                         'Is not Allowed')]

    @api.constrains('date_from', 'date_to')
    def _check_date_to_date_from(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError(_('"Date to" cannot be set before '
                                        '"Date from".\n\n'
                                        'Check the "Date from" and "Date to" '
                                        'of the "%s" service' % rec.service))


class EventServices(models.Model):
    """Model for managing the Event services"""
    _name = 'event.services'

    name = fields.Char(string="Service Name")


class EventPlace(models.Model):
    _name = 'place.place'

    name = fields.Char(string="Name")
    # district = fields.Selection([('admin', 'Administrators'),
    #                                   ('TV', 'THIRUVANANTHAPURAM'),
    #                                   ('KL', 'KOLLAM'),
    #                                   ('PT', 'PATHANAMTHITTA'),
    #                                   ('AL', 'AALAPUZHA'),
    #                                   ('KT', 'KOTTAYAM'),
    #                                   ('ID', 'IDUKKI'),
    #                                   ('ER', 'ERNAKULAM'),
    #                                   ('TS', 'THRISSUR'),
    #                                   ('PL', 'PALAKKAD'),
    #                                   ('MA', 'MALAPPURAM'),
    #                                   ('KZ', 'KOZHIKODE'),
    #                                   ('WA', 'WAYANAD'),
    #                                   ('KN', 'KANNUR'),
    #                                   ('KS', 'KASARAGOD'),
    #                                   ], default='admin', string='District Category', required=True)

    district_id = fields.Many2one('place.district')
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as "
                               "image for the event, limited to 1080x720px.")
    event_count = fields.Integer(string="# of Events",
                                 compute='_compute_place_wise_event_count')

    def _compute_place_wise_event_count(self):
        for records in self:
            events = self.env['event.management'].search([
                ('place_id', '=', records.id)])
            records.event_count = len(events)
        return

    def _get_action(self, action_xml_id):
        action = self.env['ir.actions.actions']._for_xml_id(action_xml_id)
        if self:
            action['display_name'] = self.display_name
        context = {
            'search_default_place_id': [self.id],
            'search_default_district_id': [self.district_id.id],
            'default_place_id': self.id,
            'default_district_id': self.district_id.id,
        }
        domain = [('place_id', '=', self.id)]

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        action['domain'] = domain
        return action

    def get_event_place_action_event(self):
        return self._get_action(
            'event_management.res_partner_action_events_kanban')


#
class PlaceDistrict(models.Model):
    _name = 'place.district'

    name = fields.Char(string="Name")
    state_id = fields.Many2one('res.country.state',
                               string="State", domain="[('country_id', '=?', country_id)]")
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as "
                               "image for the event, limited to 1080x720px.")
    event_count = fields.Integer(string="# of Events",
                                 compute='_compute_district_wise_event_count')
    event_type_id = fields.Many2one('event.management.type')

    #
    # type_event_count = fields.Integer(string="# of Events",
    #                              compute='_compute_event_type_count')

    def _compute_district_wise_event_count(self):
        for records in self:
            events = self.env['event.management'].search([
                ('district_id', '=', records.id)])
            records.event_count = len(events)
        return

    def _get_action(self, action_xml_id):
        action = self.env['ir.actions.actions']._for_xml_id(action_xml_id)
        if self:
            action['display_name'] = self.display_name
        context = {
            'search_default_district_id': [self.id],
            'default_district_id': self.id,
        }
        domain = [('district_id', '=', self.id)]

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        action['domain'] = domain
        return action

    # def get_event_district_action_event(self):
    #     return self._get_action(
    #         'event_management.action_event_place_view_kanban')
    def get_event_district_action_event(self):
        return self._get_action(
            'event_management.res_partner_action_events_kanban')

    # def _compute_event_type_count(self):
    #     for records in self.env['event.management.type'].search([]):
    #         events = self.env['event.management'].search([
    #             ('type_of_event_id', '=', records.id)])
    #         records.type_event_count = len(events)
    #
    # def _get_type_action(self, action_xml_id):
    #     action = self.env['ir.actions.actions']._for_xml_id(action_xml_id)
    #     if self:
    #         action['display_name'] = self.display_name
    #     context = {
    #         'search_default_type_of_event_id': [self.id],
    #         'default_type_of_event_id': self.id,
    #     }
    #
    #     action_context = literal_eval(action['context'])
    #     context = {**action_context, **context}
    #     action['context'] = context
    #     return action
    #
    # def get_event_type_action_event(self):
    #     return self._get_type_action(
    #         'event_management.event_management_action_view_kanban')


class EventManagementType(models.Model):
    """Model for managing the Event types"""
    _name = 'event.management.type'

    name = fields.Char(string="Name")
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as "
                               "image for the event, limited to 1080x720px.")
    event_count = fields.Integer(string="# of Events",
                                 compute='_compute_event_count')
    event_count_dashboard = fields.Integer(string="# of Events",
                                           compute='_compute_event_count_dashboard')

    def _compute_event_count(self):
        for records in self:
            events = self.env['event.management'].search([
                ('type_of_event_id', '=', records.id), ('venue_id', '=', self._context.get('default_venue_id'))])
            records.event_count = len(events)

    def _compute_event_count_dashboard(self):
        for records in self:
            domain = [('type_of_event_id', '=', records.id)]
            if self._context.get('default_venue_id'):
                venue_id = self._context.get('default_venue_id')
                domain += [('venue_id', '=', venue_id)]
            events = self.env['event.management'].search(domain)
            records.event_count_dashboard = len(events)

    def _get_action(self, action_xml_id):
        action = self.env['ir.actions.actions']._for_xml_id(action_xml_id)
        if self:
            action['display_name'] = self.display_name
        context = {
            'search_default_type_of_event_id': [self.id],
            'default_type_of_event_id': self.id,
        }
        if self._context.get('default_venue_id'):
            venue_id = self._context.get('default_venue_id')
            context.update({
                'search_default_venue_id': [venue_id],
                'default_venue_id': venue_id,
            })

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        return action

    def get_event_type_action_event(self):
        return self._get_action(
            'event_management.event_management_action_view_kanban')
