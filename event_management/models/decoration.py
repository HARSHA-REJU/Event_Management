# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class DecorationsNames(models.Model):
    _name = 'decoration.decoration'
    _rec_name = 'decoration_name'

    decoration_name = fields.Many2one('res.partner', 'Decoration Name')
    packages_ids = fields.Many2many('makeup.package', string='Package')

    @api.onchange('decoration_name')
    def onchange_package_id(self):
        package_ids = self.env['makeup.package'].search([('package_by','=',self.decoration_name.id)])
        self.packages_ids = package_ids

class BookDecorations(models.Model):
    _name = 'book.decorations'
    _rec_name = 'artist_name'

    artist_name = fields.Many2one('decoration.decoration', string='Decoration Name',required=True)
    customer_name = fields.Many2one('res.partner', string='Customer Name',required=True)
    package = fields.Many2one('makeup.package', string='Package',required=True)
    booking_date = fields.Date('Event Date',required=True)
    date = fields.Date('Date')
    rate = fields.Float('Rate')
    # service_ids = fields.Many2one('package.services', 'Services')
    service_id = fields.Many2many('package.service', string='Decoration Services')
    # subject_ids = fields.Many2many('package.service',)
    type_of_event_id = fields.Many2one('event.management.type', string="Event Type",
                                       required=True)

    @api.onchange('artist_name')
    def onchange_pack_id(self):
        partner_id = self.env['makeup.package'].search([('package_by', '=', self.artist_name.decoration_name.id)])
        return {'domain': {'package': [('id', '=', partner_id.ids)]}}

    @api.onchange('package')
    def onchange_rate_service(self):
        self.rate = self.package.rate
        self.service_id = self.package.package_services_ids

