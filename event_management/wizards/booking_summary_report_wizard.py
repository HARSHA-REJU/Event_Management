# -*- coding: utf-8 -*-
"""Wizard for pdf and xlsx reports"""

import json
import pytz
from odoo import fields, models,api
from odoo.exceptions import ValidationError
from odoo.tools import date_utils, io, xlsxwriter
from datetime import date
from datetime import datetime


class BookingSummaryWizard(models.TransientModel):
    """Class for wizard"""
    _name = 'booking.summary.wizard'
    _description = 'Booking Summary Wizard'

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    district_id = fields.Many2one('place.district', string='District')

    def print_summary_pdf_report(self):
        """Method for printing pdf report"""

        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Customer Invoice Report',
            'type': 'ir.actions.report',
            'report_name': 'event_management.report_booking_summary',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    def get_details(self):
        lst=[]
        district = []
        domain = []
        domain2 = []
        audi=[]
        if self.district_id:
            domain += [('district_id', '=', self.district_id.id)]
            domain2 += [('district_id', '=', self.district_id.id)]
        if self.date_from :
            dt = datetime.combine(self.date_from, datetime.min.time())
            print(dt)
            # domain += [('start_date', '>=', dt), ('end_date', '<=', dt)]
            # domain += [('start_date', '>=', dt)]
            domain += [('event_date', '>=', dt)]
        if self.date_to :
            dt = datetime.combine(self.date_to, datetime.min.time())
        #     # domain += [('start_date', '>=', dt), ('end_date', '<=', dt)]
        #     domain += [('end_date', '<=', dt)]
            domain += [('event_date', '<=', dt)]
        res = self.env['event.management'].search(domain)
        aud = self.env['res.partner'].search(domain2)
        audi_count = 0

        for items in aud:
            audi_count = audi_count +1
            audi.append(items)
        print("total auditorium",len(audi))
        print("Auditoriums",aud)
        for rec in res:
            if rec.district_id.id not in district:
                vals={
                    'district_id':rec.district_id.id,
                    'district':rec.district_id.name,
                    'date':rec,
                    'count':1,
                    'total_audi':audi_count,
                    'booked':0,
                    'not_booked':0,
                    'venue_id':rec.venue_id.id,

                }
                lst.append(vals)
                district.append(rec.district_id.id)
            else:
                dis = rec.district_id.id
                for dicts in lst:
                    if (dicts['district_id'] == dis):
                        dicts['count'] = dicts['count']+1
        booked_count = 0
        district_audi_count=0
        venue_list=[]
        for vals in lst:
            venue=vals['venue_id']
            venue_obj= self.env['res.partner'].search([('district_id', '=', vals['district_id'])])
            vals['total_audi'] = len(venue_obj)
        booked_venues = self.env['event.management'].search([])
        for item in booked_venues:
            if item.venue_id in venue_list:
                pass
            else:
                venue_list.append(item.venue_id)
        for vals in lst:
            district_name = vals['district_id']
            b_count=0
            for i in venue_list:
                if i.district_id.id == district_name:
                    b_count=b_count+1
            vals['booked'] = b_count

        for vals in lst:
            vals['not_booked'] = vals['total_audi'] - vals['booked']

        return lst




