# -*- coding: utf-8 -*-
"""Controller for xlsx report"""
import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.http import serialize_exception as _serialize_exception
from odoo.tools import html_escape
import werkzeug


class XLSXReportController(http.Controller):
    """Controller Class for xlsx report"""
    @http.route('/xlsx_reports', type='http', auth='user', methods=['POST'],
                csrf=False)
    def get_report_xlsx(self, model, options, output_format, report_name):
        """Method for passing data to xlsx report"""
        uid = request.session.uid
        report_obj = request.env[model].with_user(uid)
        options = json.loads(options)
        token = 'dummy-because-api-expects-one'
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[('Content-Type', 'application/vnd.ms-excel'), (
                        'Content-Disposition',
                        content_disposition(report_name + '.xlsx'))])
                report_obj.get_xlsx_report(options, response)
            return response
        except Exception as err:
            exception = _serialize_exception(err)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': exception
            }
            return request.make_response(html_escape(json.dumps(error)))


# class ServiceRequest(http.Controller):
#
#     @http.route(['/home'], type='http', auth="public", website=True)
#     def service_request(self):
#         # products = request.env['product.product'].search([])
#         #
#         # values = {
#         #
#         #     'products': products
#
#         # }
#
#         return request.render(
#
#             "event_management.custom_home_page")

class HomePage(http.Controller):

    @http.route(['/'], type='http', auth="public",website=True)
    def home_page_controller(self):

        # venues = request.env['res.partner'].search([])
        districts = request.env['place.district'].sudo().search([])
        types = request.env['event.management.type'].sudo().search([])
        places = request.env['place.place'].sudo().search([])

        values = {
            # 'venues':venues,
            'districts':districts,
            'types':types,
            'places':places,
        }
        return request.render(

        "event_management.custom_home_page",values)

class ContactUsPage(http.Controller):
    @http.route(['/contactus'], type='http', auth="public",website=True)
    def contact_page_controller(self):

        # venues = request.env['res.partner'].search([])
        # districts = request.env['place.district'].search([])
        # types = request.env['event.management.type'].search([])
        # places = request.env['place.place'].search([])

        values = {
            # 'venues':venues,
            # 'districts':districts,
            # 'types':types,
            # 'places':places,
        }
        return request.render(

        "event_management.contact_page",values)

class VenueListingPage(http.Controller):
    @http.route(['/venuelist'], type='http', auth="public",website=True)
    def venue_page_controller(self):

        venues = request.env['res.partner'].sudo().search([])
        districts = request.env['place.district'].sudo().search([])
        # types = request.env['event.management.type'].search([])
        # places = request.env['place.place'].search([])

        values = {
            'venues':venues,
            'districts':districts,
            # 'types':types,
            # 'places':places,
        }
        return request.render(

        "event_management.venue_page",values)
class SearchListPage(http.Controller):
    @http.route(['/searchlist'], type='http', auth="public",website=True)
    def search_page_controller(self, **args):

        district_domain = []
        domain_venue = []
        print (args.get('district_id'))
        if args.get('district_id'):
            domain_venue = [('district_id.id','=',args.get('district_id'))]
            district_domain = [('id','=',args.get('district_id'))]

        venues = request.env['res.partner'].sudo().search(domain_venue)
        districts = request.env['place.district'].sudo().search(district_domain)

        values = {
            'venues':venues,
            'districts':districts,
        }
        return request.render(

        "event_management.venue_search_page",values)

class MakeupPage(http.Controller):
    @http.route(['/makeup'], type='http', auth="public",website=True)
    def search_page_controller(self, **args):

        print (args.get('price'))
        makeup_artists = request.env['artist.artist'].sudo().search([])
        mehandi_artists = request.env['artist.artist'].sudo().search([])
        packages = request.env['makeup.package'].sudo().search([])
        services = request.env['package.service'].sudo().search([])

        values = {
            'makeup_artists':makeup_artists,
            'mehandi_artists':mehandi_artists,
            'packages':packages,
            'services':services,
        }
        return request.render(

        "event_management.makeup_page",values)
class EventDetailsPage(http.Controller):
    @http.route(['/eventdetails'], type='http', auth="public",website=True)
    def event_page_controller(self, **args):
        # print (self)
        # print ('..........')
        # print (district_id)
        print (args.get('price'))
        venues = request.env['res.partner'].sudo().search([('district_id','=',args.get('district_id'))])
        # venues = request.env['res.partner'].search([])
        districts = request.env['place.district'].sudo().search([('id','=',args.get('district_id'))])
        # types = request.env['event.management.type'].search([])
        # places = request.env['place.place'].search([])

        values = {
            'venues':venues,
            'districts':districts,
            # 'types':types,
            # 'places':places,
        }
        return request.render(

        "event_management.event_details_page",values)
class BookingPage(http.Controller):
    @http.route(['/booking'], type='http', auth="public",website=True)
    def booking_page_controller(self, **args):
        venues = request.env['res.partner'].sudo().search([])
        districts = request.env['place.district'].sudo().search([])
        types = request.env['event.management.type'].sudo().search([])
        places = request.env['place.place'].sudo().search([])

        values = {
            'venues':venues,
            'districts':districts,
            'types':types,
            'places':places,
        }
        return request.render(

        "event_management.booking_page",values)
