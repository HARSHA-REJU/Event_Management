# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class MakeupArtistNames(models.Model):
    _name = 'artist.artist'
    _rec_name = 'artist_name'

    artist_name = fields.Many2one('res.partner', 'Name')
    packages_ids = fields.Many2many('makeup.package', string='Package')

    @api.onchange('artist_name')
    def onchange_package_id(self):
        package_ids = self.env['makeup.package'].search([('package_by','=',self.artist_name.id)])
        self.packages_ids = package_ids

class MakeupPackages(models.Model):
    _name = 'makeup.package'
    _rec_name = 'name'

    # code = fields.Char('Code')
    name = fields.Char('Package Name')
    package_by = fields.Many2one('res.partner', 'Package By')
    rate = fields.Float('Rate')
    package_services_ids = fields.Many2many('package.service', string='Services')
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as image for "
                               "the event, limited to 1080x720px.")


class BookMakeupArtist(models.Model):
    _name = 'makeup.artist'
    _rec_name = 'artist_name'

    artist_name = fields.Many2one('artist.artist', string='Artist Name',required=True)
    customer_name = fields.Many2one('res.partner', string='Customer Name',required=True)
    package = fields.Many2one('makeup.package', string='Package',required=True)
    date_from = fields.Date('Date From',required=True)
    date_to = fields.Date('Date To',required=True)
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




    @api.onchange('package')
    def onchange_place_id(self):
        self.rate = self.package.rate
        self.service_id = self.package.package_services_ids

class PackageServices(models.Model):
    _name = 'package.service'
    _rec_name = 'service_name'

    service_name = fields.Char('Service Name')
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as image for "
                               "the event, limited to 1080x720px.")

