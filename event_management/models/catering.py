# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class CatersNames(models.Model):
    _name = 'cater.cater'
    _rec_name = 'cater_name'

    cater_name = fields.Many2one('res.partner', 'Caterers Name')
    packages_ids = fields.Many2many('makeup.package', string='Package')

    @api.onchange('cater_name')
    def onchange_package_id(self):
        package_ids = self.env['makeup.package'].search([('package_by','=',self.cater_name.id)])
        self.packages_ids = package_ids

class BookCaters(models.Model):
    _name = 'book.cater'
    _rec_name = 'artist_name'

    artist_name = fields.Many2one('cater.cater', string='Caterers Name',required=True)
    customer_name = fields.Many2one('res.partner', string='Customer Name',required=True)
    package = fields.Many2one('makeup.package', string='Package',required=True)
    number_of_plate = fields.Integer('Serving For(Nos)',required=True)
    booking_date = fields.Date('Booking Date',required=True)
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    date = fields.Date('Date')
    rate = fields.Float('Rate/Plate')
    total = fields.Float('Total Amount')
    # service_ids = fields.Many2one('package.services', 'Services')
    service_id = fields.Many2many('package.service', string='Dishes')
    # subject_ids = fields.Many2many('package.service',)
    type_of_event_id = fields.Many2one('event.management.type', string="Event Type",
                                       required=True)
    compute_field = fields.Char(compute="_compute_total_rate")



    @api.onchange('artist_name')
    def onchange_pack_id(self):
        return {'domain': {'package': [('id', 'in', self.artist_name.packages_ids.ids)]}}

    @api.onchange('package')
    def onchange_place_id(self):
        self.rate = self.package.rate
        self.service_id = self.package.package_services_ids

    @api.onchange('rate', 'number_of_plate','total')
    def _compute_total_rate(self):
        for rec in self:
            rec.total = rec.rate * rec.number_of_plate

