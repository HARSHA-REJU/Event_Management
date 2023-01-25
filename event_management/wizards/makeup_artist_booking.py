# -*- coding: utf-8 -*-
from odoo import fields, models
from datetime import datetime


class MakeupReportWizard(models.TransientModel):
    """Class for wizard"""
    _name = 'makeup.report.wizard'
    _description = 'Makeup Artist Booking Report Wizard'

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    artist = fields.Many2one('artist.artist', string='Makeup Artist')

    def print_makeup_pdf_report(self):
        """Method for printing pdf report"""

        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Makeup Artist Booking Report',
            'type': 'ir.actions.report',
            'report_name': 'event_management.report_makeup_artist_booking',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    def get_details(self):
        domain = []
        lst = []
        if self.artist:
            domain += [('artist_name', '=', self.artist.id)]
        if self.date_from:
            dt = datetime.combine(self.date_from, datetime.min.time())
            domain += [('booking_date', '>=', self.date_from)]
        if self.date_to:
            dt = datetime.combine(self.date_to, datetime.min.time())
            domain += [('booking_date', '<=', self.date_to)]
        res = self.env['makeup.artist'].search(domain)
        for rec in res:
            vals = {
                'artist': rec.artist_name.artist_name.name,
                'type': rec.type_of_event_id.name,
                'customer_name': rec.customer_name.name,
                'package': rec.package.name,
                'booking_date': rec.booking_date,
            }
            lst.append(vals)
        return lst
