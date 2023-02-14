# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class MakeupArtistNames(models.Model):
    _name = 'artist.artist'
    _rec_name = 'artist_name'

    artist_name = fields.Many2one('res.partner', 'Name',options="{'no_quick_create': True}")
    packages_ids = fields.Many2many('makeup.package', string='Package')
    makeup_artist = fields.Boolean(string="Makeup Artist ?")
    mehndi_artist = fields.Boolean(string="Mehndi Artist ?")
    compute_field = fields.Char(compute="_compute_artist_type")

    @api.onchange('artist_name')
    def onchange_package_id(self):
        package_ids = self.env['makeup.package'].search([('package_by','=',self.artist_name.id)])
        self.packages_ids = package_ids
        # return {'domain': {'packages_ids': [('id', '=', package_ids.ids)]}}

    @api.onchange('makeup_artist','mehndi_artist')
    def _compute_artist_type(self):
        for rec in self:
            if rec.makeup_artist == True:
                partner_id = self.env['res.partner'].search([('makeup_artist','=',True)])
                return {'domain': {'artist_name': [('id', '=', partner_id.ids)]}}
            else:
                if rec.mehndi_artist == True:
                    partner_id = self.env['res.partner'].search([('mehndi_artist','=',True)])
                    return {'domain': {'artist_name': [('id', '=', partner_id.ids)]}}


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
    makeup_artist = fields.Boolean(string="Makeup Package ?")
    mehndi_artist = fields.Boolean(string="Mehndi Package ?")
    photographer = fields.Boolean(string="Photography Packages ?")
    catering = fields.Boolean(string="Catering Package ?")
    entertainment = fields.Boolean(string="Entertainment Package ?")
    decoration = fields.Boolean(string="Decoration Package ?")
    compute_field = fields.Char(compute="_compute_artist_type")

    @api.onchange('makeup_artist', 'mehndi_artist','photographer','catering','entertainment')
    def _compute_artist_type(self):
        for rec in self:
            if rec.makeup_artist == True:
                partner_id = self.env['res.partner'].search([('makeup_artist', '=', True)])
                packages_id = self.env['package.service'].search([('makeup_artist', '=', True)])
                return {'domain': {'package_by': [('id', '=', partner_id.ids)],'package_services_ids':[('id', 'in', packages_id.ids)]}}

            if rec.mehndi_artist == True:
                partner_id = self.env['res.partner'].search([('mehndi_artist', '=', True)])
                packages_id = self.env['package.service'].search([('mehndi_artist', '=', True)])
                return {'domain': {'package_by': [('id', '=', partner_id.ids)],'package_services_ids':[('id', 'in', packages_id.ids)]}}

            if rec.photographer == True:
                partner_id = self.env['res.partner'].search([('photographer', '=', True)])
                packages_id = self.env['package.service'].search([('photographer', '=', True)])
                return {'domain': {'package_by': [('id', '=', partner_id.ids)],'package_services_ids':[('id', 'in', packages_id.ids)]}}

            if rec.catering == True:
                partner_id = self.env['res.partner'].search([('catering', '=', True)])
                packages_id = self.env['package.service'].search([('catering', '=', True)])
                return {'domain': {'package_by': [('id', '=', partner_id.ids)],'package_services_ids':[('id', 'in', packages_id.ids)]}}

            if rec.entertainment == True:
                partner_id = self.env['res.partner'].search([('entertainment', '=', True)])
                packages_id = self.env['package.service'].search([('entertainment', '=', True)])
                return {'domain': {'package_by': [('id', '=', partner_id.ids)],'package_services_ids':[('id', 'in', packages_id.ids)]}}

    @api.model
    def create(self, values):
        res = super(MakeupPackages,self).create(values)
        product_id = self.env['product.product'].create({"name": res.name})
        return res

class BookMakeupArtist(models.Model):
    _name = 'makeup.artist'
    _rec_name = 'artist_name'

    artist_name = fields.Many2one('artist.artist', string='Artist Name',required=True)
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
    makeup_artist = fields.Boolean(string="Makeup Artist booking?")
    mehndi_artist = fields.Boolean(string="Mehndi Artist booking ?")
    compute_field = fields.Char(compute="_compute_artist_type")



    @api.onchange('artist_name')
    def onchange_pack_id(self):
        partner_id = self.env['makeup.package'].search([('package_by', '=', self.artist_name.artist_name.id)])
        return {'domain': {'package': [('id', '=', partner_id.ids)]}}

    @api.onchange('makeup_artist', 'mehndi_artist')
    def _compute_artist_type(self):
        for rec in self:
            if rec.makeup_artist == True:
                partner_id = self.env['artist.artist'].search([('makeup_artist', '=', True)])
                return {'domain': {'artist_name': [('id', '=', partner_id.ids)]}}
            else:
                if rec.mehndi_artist == True:
                    partner_id = self.env['artist.artist'].search([('mehndi_artist', '=', True)])
                    return {'domain': {'artist_name': [('id', '=', partner_id.ids)]}}


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
    makeup_artist = fields.Boolean(string="Makeup Service ?")
    mehndi_artist = fields.Boolean(string="Mehndi Service ?")
    photographer = fields.Boolean(string="Photography Service ?")
    catering = fields.Boolean(string="Catering Service ?")
    entertainment = fields.Boolean(string="Entertainment Service ?")
    decoration = fields.Boolean(string="Decoration Service ?")


class Decoration(models.Model):
    _name = 'decoration.items'

    # code = fields.Char('Code')
    name = fields.Char('Decoration Package Name')
    rate = fields.Float('Rate')

