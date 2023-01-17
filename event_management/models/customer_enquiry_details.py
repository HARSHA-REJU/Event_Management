# -*- coding: utf-8 -*-
"""Customer Enquiry Details"""

from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CustomerEnquiryDetails(models.Model):
    """Model for managing Customer Enquiry Details"""
    _name = 'customer.enquiry.details'

    name = fields.Char('Name', readonly=True, copy=False)
    reference = fields.Char(string='Reference', readonly=True)
    type_of_event_id = fields.Many2one('event.management.type', string="Type",
                                       required=True)
    customer_name = fields.Char(string="Customer Name",
                                 required=True)
    mobile = fields.Char()
    address = fields.Text()
    venue_id = fields.Many2one('res.partner', string="Venue")
    venue_ids = fields.Many2many('res.partner', string="Venues")
    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    start_date = fields.Datetime(string="Start date",
                                 default=lambda self: fields.datetime.now(),
                                 required=True)
    end_date = fields.Datetime(string="End date", required=True)
    no_of_attendees = fields.Integer(string='Total Persons')
    note = fields.Text('Terms and conditions')
    state = fields.Selection([('draft', 'Draft'),('quote','Quotation Created'), ('confirm', 'Confirmed'),('event','Event Booked'),('cancel', 'Canceled')],
                             string="State", default="draft")
    services = fields.Many2many('event.services', string="Services")
    place_id = fields.Many2one('place.place')
    district_id = fields.Many2one('place.district')

    @api.onchange('district_id')
    def onchange_district_id(self):
        self.place_id = ''
        return {'domain':{'place_id':[('district_id','=',self.district_id.id)]}}

    @api.onchange('place_id')
    def onchange_place_id(self):
        self.venue_id=''
        return {'domain':{'venue_id':[('place_id','=',self.place_id.id)]}}

    @api.model
    def create(self, values):
        """Crete method for sequencing and checking dates while creating"""
        start_date = values['start_date']
        end_date = values['end_date']
        customer_name = values['customer_name']
        event_name = self.env['event.management.type'].browse(
            values['type_of_event_id']).name
        if start_date >= end_date:
            raise UserError(_('Start date must be less than End date'))

        name = '%s-%s-%s' % (customer_name, event_name, values['date'])
        values['name'] = name
        sequence_code = 'enquiry.sequence'
        sequence_number = self.env['ir.sequence'].next_by_code(sequence_code)
        values['reference'] = sequence_number
        res = super(CustomerEnquiryDetails, self).create(values)
        return res

    def action_enquiry_confirm(self):
        """Button action to confirm"""
        self.state = "confirm"
    def action_create_quote(self):
        """Button action to confirm"""
        self.state = "quote"
    def print_quote(self):
        pass




    def action_enquiry_cancel(self):
        """Button action to confirm"""
        self.state = "cancel"

    def action_create_event(self):

        venue_obj_id = self.env['res.partner'].browse(self.venue_id.id)
        vals = []
        for rec in venue_obj_id.facilities_ids:
            dict={

                    'product_id': rec.product_id.id,
                    'price': rec.price,
                    'quantity':rec.quantity,
                    'total':rec.total,

            }
            vals.append((0, 0, dict))


        event_id = self.env['event.management'].create({
            'start_date':self.start_date,
            'end_date':self.end_date,
            # 'partner_id':self.customer_name.id,
            'partner_id':self.env['res.partner'].create({'name':self.customer_name,}).id,
            'type_of_event_id':self.type_of_event_id.id,
            'date':fields.Date.today(),
            'district_id':self.district_id.id,
            'place_id':self.place_id.id,
            'venue_id':self.venue_id.id,
            'facilities_ids2': vals,
        })
        return {
            'name': _('Event Booking Form'),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'event.management',
            'type': 'ir.actions.act_window',
            'res_id':event_id.id,
            'target': 'current',
        }
