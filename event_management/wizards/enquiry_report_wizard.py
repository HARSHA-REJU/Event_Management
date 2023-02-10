# -*- coding: utf-8 -*-
from odoo import fields, models
from datetime import datetime


class EnquiryReportWizard(models.TransientModel):
    """Class for wizard"""
    _name = 'enquiry.report.wizard'
    _description = 'Enquiry Report Wizard'

    date_from = fields.Datetime(string="From")
    date_to = fields.Datetime(string="To")
    state = fields.Selection([('draft', 'Enquiries in Draft'), ('confirm', 'Confirmed Enquiries'), ],
                             string="Status", )

    def print_enquiries_pdf_report(self):
        """Method for printing pdf report"""

        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Customer Enquiry Report',
            'type': 'ir.actions.report',
            'report_name': 'event_management.report_customer_enquiry',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    def view_summary_pdf_report(self):
        pass

    def get_details(self):
        domain = []
        lst = []
        if self.state:
            domain += [('state', '=', self.state)]
        if self.date_from:
            dt = datetime.combine(self.date_from, datetime.min.time())
            # domain += [('start_date', '>=', self.date_from)]
            domain += [('event_date', '>=', self.date_from)]
        if self.date_to:
            dt = datetime.combine(self.date_to, datetime.min.time())
            # domain += [('end_date', '<=', self.date_to)]
            domain += [('event_date', '<=', self.date_to)]
        res = self.env['customer.enquiry.details'].search(domain)
        for rec in res:
            vals = {
                'state': rec.state,
                'type': rec.type_of_event_id.name,
                'customer_name': rec.customer_name,
                'contact': rec.mobile,
                'venue_id': rec.venue_id.name,
                'district': rec.district_id.name,
                'place': rec.place_id.name,
                'address': rec.address,
                'email': rec.email,
                # 'start_date': rec.start_date,
                # 'end_date': rec.end_date,
                'event_date': rec.event_date,
                'reference': rec.reference,
            }
            lst.append(vals)
        return lst
