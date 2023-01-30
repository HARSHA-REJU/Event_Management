# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PhotographyNames(models.Model):
    _name = 'photographer.photographer'
    _rec_name = 'photography_name'

    photography_name = fields.Many2one('res.partner', 'Name')
    packages_ids = fields.Many2many('makeup.package', string='Package')

    # @api.onchange('artist_name')
    # def onchange_package_id(self):
    #     package_ids = self.env['makeup.package'].search([('package_by','=',self.artist_name.id)])
    #     self.packages_ids = package_ids

class BookPhotography(models.Model):
    _name = 'book.photography'
    _rec_name = 'artist_name'

    artist_name = fields.Many2one('photographer.photographer', string='Photography Name',required=True)
    customer_name = fields.Many2one('res.partner', string='Customer Name',required=True)
    package = fields.Many2one('makeup.package', string='Package',required=True)
    booking_date = fields.Date('Booking Date',required=True)
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    date = fields.Date('Date')
    rate = fields.Float('package Rate')
    # service_ids = fields.Many2one('package.services', 'Services')
    service_id = fields.Many2many('package.service', string='Services')
    # subject_ids = fields.Many2many('package.service',)
    type_of_event_id = fields.Many2one('event.management.type', string="Event Type",
                                       required=True)


    @api.onchange('artist_name')
    def onchange_pack_id(self):
        return {'domain': {'package': [('id', 'in', self.artist_name.packages_ids.ids)]}}

