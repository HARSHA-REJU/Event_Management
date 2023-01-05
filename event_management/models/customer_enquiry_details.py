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
    customer_name = fields.Char(string="Customer",
                                 required=True)
    mobile = fields.Char()
    address = fields.Text()
    auditorium_id = fields.Many2one('res.company', string="Auditorium")
    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    start_date = fields.Datetime(string="Start date",
                                 default=lambda self: fields.datetime.now(),
                                 required=True)
    end_date = fields.Datetime(string="End date", required=True)

    no_of_attendees = fields.Integer(string='Total Persons')
    note = fields.Text('Terms and conditions')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),('event','Event Booked'),('cancel', 'Canceled')],
                             string="State", default="draft")
    services = fields.Many2many('event.services', string="Services")

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

    def action_enquiry_cancel(self):
        """Button action to confirm"""
        self.state = "cancel"

    def create_event(self):
        event_id = self.env['event.management'].create({
            'start_date':self.start_date,
            'end_date':self.end_date,
            'partner_id':self.env['res.partner'].create({'name':self.customer_name,}).id,
            'type_of_event_id':self.type_of_event_id.id,
            'service_line_ids':{}
        })
