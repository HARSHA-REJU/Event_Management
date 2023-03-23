# -*- coding: utf-8 -*-
"""Module for pdf data fetching and carry off pdf report data"""

import pytz
import datetime
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ReportHotelManagement(models.AbstractModel):
    """class for fetch and carry off pdf data to template"""
    _name = "report.event_management.report_event_management"
    _description = "Event Management Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        form_data = data['form']
        where = '1=1'
        if form_data['date_from'] and form_data['date_to'] \
                and form_data['date_from'] > form_data['date_to']:
            raise ValidationError('From Date must be less than To Date')
        if form_data["partner_id"]:
            where += """AND e.partner_id = '%s'""" % \
                     (form_data['partner_id'][0])
        if form_data['date_from']:
            where += """AND e.date>='%s'""" % (form_data['date_from'])
        if form_data['date_to']:
            where += """AND e.date <= '%s'""" % (form_data['date_to'])
        if form_data['type_event_ids']:
            event_list = data['event_types']
            event_ids = f"({event_list[0]})" if len(event_list) == 1 else tuple(
                event_list)
            where += """AND e.type_of_event_id IN {}""".format(event_ids)
        if form_data['event_state']:
            where += """AND e.state = '%s'""" % (form_data['event_state'])
        self.env.cr.execute("""
                SELECT e.name as event, t.name as type, r.name as partner, d.name as district, p.name as place,v.name as venue,
                e.state, e.date,e.email,e.mobile,e.address,
                e.start_date, e.end_date
                from event_management e inner join 
                res_partner r on e.partner_id = r.id
                inner join event_management_type t on 
                e.type_of_event_id = t.id
                inner join place_district d on 
                e.district_id = d.id
                inner join place_place p on 
                e.place_id = p.id
                inner join res_partner v on 
                e.venue_id = v.id
                where %s order by e.date""" % where)
        rec = self.env.cr.dictfetchall()
        user_tz = self.env.user.tz
        current = pytz.UTC.localize(fields.datetime.now())
        current = current.astimezone(pytz.timezone(user_tz))
        current = datetime.datetime.strftime(current, "%d-%m-%Y %H:%M:%S")
        return {
            'docs': rec,
            'docs2': form_data,
            'today_date': current
        }
