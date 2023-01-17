# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class MakeupArtistNames(models.Model):
    _name = 'artist.artist'
    _rec_name = 'artist_name'

    artist_name = fields.Many2one('res.partner', 'Name')
    packages_ids = fields.Many2many('makeup.package', string='Package')

class MakeupPackages(models.Model):
    _name = 'makeup.package'
    _rec_name = 'name'

    # code = fields.Char('Code')
    name = fields.Char('Package Name')
    package_by = fields.Many2one('res.partner', 'Package By')
    rate = fields.Float('Rate')
    package_services_ids = fields.Many2many('package.service', string='Services')


class BookMakeupArtist(models.Model):
    _name = 'makeup.artist'
    _rec_name = 'artist_name'

    artist_name = fields.Many2one('res.partner', 'Name')
    package = fields.Many2one('makeup.package', string='Package')
    date_of = fields.Date('Book Date')
    date = fields.Date('Date')
    rate = fields.Float('package Rate')
    # service_ids = fields.Many2one('package.services', 'Services')
    service_id = fields.Many2many('package.service', string='Services')
    # subject_ids = fields.Many2many('package.service',)

    @api.onchange('package')
    def onchange_place_id(self):
        self.rate = self.package.rate
        self.service_id = self.package.package_services_ids

class PackageServices(models.Model):
    _name = 'package.service'
    _rec_name = 'service_name'

    service_name = fields.Char('Service Name')

