# -*- coding: utf-8 -*-
"""Controller for xlsx report"""
import json
import datetime
from datetime import timedelta

from odoo import http, fields, _
from odoo.http import content_disposition, request
from odoo.http import serialize_exception as _serialize_exception
from odoo.tools import html_escape
import werkzeug
from werkzeug.utils import redirect

import odoo

SIGN_UP_REQUEST_PARAMS = {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'city', 'country_id', 'lang'}
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

class HomePage(http.Controller):
    @http.route(['/'], type='http', auth="public",website=True)
    def home_page_controller(self):

        districts = request.env['place.district'].sudo().search([])
        types = request.env['event.management.type'].sudo().search([])
        places = request.env['place.place'].sudo().search([])
        current_user = request.env.user

        values = {
            'districts':districts,
            'types':types,
            'places':places,
            'current_user':current_user,
        }
        return request.render(

        "event_management.custom_home_page",values)

    @http.route(['/signup'], type='http', auth="public",website=True)
    def signup_controller(self, **args):
        email = args.get('email')
        password = args.get('pass')
        re_password = args.get('re_pass')
        mobile = args.get('mobile')
        name = args.get('name')
        current_user = request.env.user


        vals = {
            'login':email,
            'name':name,
            'password':password,
        }
        # print(vals)
        if password==re_password:
            new_user = request.env['res.users'].sudo().create(vals)
            new_user.partner_id.write({'mobile': mobile})
            new_user.partner_id.write({'email': email})
            return http.redirect_with_hash('/#loginModal')

    @http.route(['/user/login'], type='http', auth="public",website=True)
    def login_controller(self, **args):
        email = args.get('email')
        password = args.get('pass')
        current_user = request.env['res.users'].sudo().search([('login','=',email)])

        # response = redirect("/#LoginModal")
        # return response

        # ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, email, password)
                request.params['login_success'] = True
                return http.redirect_with_hash('/')
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
                return http.redirect_with_hash('/#loginModal?error=true')
                # return http.redirect_with_hash('/#loginModal',values)
        # else:
        #     if 'error' in request.params and request.params.get('error') == 'access':
        #         values['error'] = _('Only employees can access this database. Please contact the administrator.')
        #
        # if 'login' not in values and request.session.get('auth_login'):
        #     values['login'] = request.session.get('auth_login')
        #
        # if not odoo.tools.config['list_db']:
        #     values['disable_database_manager'] = True
        #
        # response = request.render('web.login', values)
        # response.headers['X-Frame-Options'] = 'DENY'
        # return response

        
    @http.route(['/account'], type='http', auth="public", website=True)
    def user_account(self, **args):
        current_user = request.env.user
        current_user_id = request.env.user.id

        if current_user.has_group('event_management.group_auditorium_manager'):
            enquiries = request.env['customer.enquiry.details'].sudo().search([('venue_id','=',current_user.auditorium.id)])
            venue_bookings = request.env['event.management'].sudo().search([('venue_id','=',current_user.auditorium.id)])
        elif current_user.has_group('base.group_system'):
            enquiries = request.env['customer.enquiry.details'].sudo().search([])
            venue_bookings = request.env['event.management'].sudo().search([])
        else:
            enquiries = request.env['customer.enquiry.details'].sudo().search([('user_id','=',current_user_id)])
            venue_bookings = request.env['event.management'].sudo().search([('user_id','=',current_user_id)])

        values = {
            'enquiries':enquiries,
            'venue_bookings':venue_bookings,
            'current_user': current_user,
        }
        return request.render(
        "event_management.account_page",values)
    @http.route(['/invoices'], type='http', auth="public", website=True)
    def user_invoices_show(self, **args):
        current_user = request.env.user
        current_user_id = request.env.user.id

        if current_user.has_group('event_management.group_auditorium_manager'):
            venue_bookings = request.env['event.management'].sudo().search([('venue_id','=',current_user.auditorium.id)])
            invoices = request.env['account.move'].sudo().search([('booking_id','in',venue_bookings.ids)])
        elif current_user.has_group('base.group_system'):
            invoices = request.env['account.move'].sudo().search([])
        else:
            invoices = request.env['account.move'].sudo().search([('partner_id','=',current_user_id.partner_id)])

        values = {
            'invoices':invoices,
            'current_user': current_user,
        }
        return request.render(
        "event_management.invoices_page",values)

    @http.route(['/bill/ref'], type='http', auth="public", website=True)
    def user_invoices_direct_controller(self, **args):
        current_user = request.env.user
        if current_user.has_group ('event_management.group_auditorium_manager') or current_user.has_group ('base.group_system'):

            return http.redirect_with_hash("/web#action=196&model=account.move&view_type=list&cids=1&menu_id=101")
        else:
            return http.redirect_with_hash('/invoices')

    @http.route(['/logout'], type='http', auth="public", website=True)
    def logout_controller(self, **args):
        request.session.logout(keep_db=True)
        return http.redirect_with_hash('/')

    @http.route(['/dashboard'], type='http', auth="public", website=True)
    def dashboard_controller(self, **args):
        current_user = request.env.user
        if current_user.has_group ('event_management.group_auditorium_manager') or current_user.has_group ('base.group_system'):
            return http.redirect_with_hash("/web")
        else:
            return http.redirect_with_hash('/account')

    @http.route(['/record'], type='http', auth="public", website=True)
    def booking_direct_controller(self, **args):
        current_user = request.env.user
        if current_user.has_group ('event_management.group_auditorium_manager') or current_user.has_group ('base.group_system'):

            return http.redirect_with_hash("/web#action=281&model=event.management&view_type=list&cids=&menu_id=186")
        else:
            return http.redirect_with_hash('/account')
    @http.route(['/enquiry'], type='http', auth="public", website=True)
    def enquiry_direct_controller(self, **args):
        current_user = request.env.user
        if current_user.has_group ('event_management.group_auditorium_manager') or current_user.has_group ('base.group_system'):

            return http.redirect_with_hash("/web#action=273&model=customer.enquiry.details&view_type=list&cids=&menu_id=180")
        else:
            return http.redirect_with_hash('/account')


class ContactUsPage(http.Controller):
    @http.route(['/contactus'], type='http', auth="public",website=True)
    def contact_page_controller(self):
        current_user = request.env.user
        districts = request.env['place.district'].sudo().search([])
        types = request.env['event.management.type'].sudo().search([])

        values = {
            # 'venues':venues,
            'districts':districts,
            'types':types,
            # 'places':places,
            'current_user': current_user,
        }
        return request.render(
        "event_management.contact_page",values)
    @http.route(['/enquiry/confirm'], type='http', auth="public",website=True)
    def contact_page_confirm(self, **args):
        district_id = int(args.get('district_id'))
        type_id = int(args.get('type_id'))
        email = args.get('email')
        date = args.get('date')
        mobile = args.get('mobile')
        name = args.get('name')
        # surname = args.get('surname')
        address = args.get('address')
        message = args.get('message')
        auditorium = args.get('option1')
        makeup = args.get('option2')
        catering = args.get('option3')
        photography = args.get('option4')
        decoration = args.get('option5')
        entertainment = args.get('option6')


        vals = {
            'district_id':district_id,
            'type_of_event_id':type_id,
            'email':email,
            'date':fields.Date.today(),
            'event_date':date,
            'mobile':mobile,
            'customer_name':name,
            'address':address,
            'remarks':message,
            'auditorium':auditorium,
            'decoration':decoration,
            'photography':photography,
            'catering':catering,
            'makeup':makeup,
            'entertainment':entertainment,
        }
        #
        #
        # print(vals)
        enquiry_event = request.env['customer.enquiry.details'].sudo().create(vals)
        response = redirect("/contactus")
        return response



class VenueListingPage(http.Controller):

    @http.route(['/list'], type='http', auth="public",website=True)
    def all_venue_list_page_controller(self, **args):
        current_user = request.env.user
        current_user = request.env.user
        district_id = args.get('district_id')

        # print (district_id)
        # print ("district_id")
        # print ("district_id")
        # print ("district_id")
        # print ("district_id")
        venues = request.env['res.partner'].sudo().search([('venue', '=', True), ('district_id.id', '=', args.get('district_id'))])
        districts = request.env['place.district'].sudo().search([('id', '=', args.get('district_id'))])

        values = {
            'venues': venues,
            'districts': districts,
            'current_user': current_user,
        }
        return request.render(
            "event_management.venue_search_page", values)


        # venues = request.env['res.partner'].sudo().search([('venue','=',True)])
        # # districts = request.env['place.district'].sudo().search(district_domain)
        # # print("keeeeeeeeeeeeeeeeeeeeeeeejhukgggggggggggggggggggggggggggggggggggggggggggg")
        # values = {
        #     'venues':venues,
        #     'district_id':event_type[1],
        #     'current_user': current_user,
        # }
        # return request.render(
        #
        # "event_management.all_venue_list_page",values)

    @http.route(['/venuelist'], type='http', auth="public",website=True)
    def venue_page_controller(self):
        current_user = request.env.user
        values = {
                'current_user':current_user
                  }
        return request.render(

        "event_management.venue_page",values)
    # @http.route(['/venuelist'], type='http', auth="public",website=True)
    # def venue_page_controller(self):
    #     current_user = request.env.user
    #     # if current_user.has_group ('event_management.group_auditorium_manager'):
    #     #     return http.redirect_with_hash("/web")
    #     # else:
    #     trivandrum_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',1)])
    #     kollam_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',2)])
    #     pathanamthitta_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',3)])
    #     alappey_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',4)])
    #     kottayam_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',5)])
    #     idukki_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',6)])
    #     ernakulam_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',7)])
    #     thrissur_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',8)])
    #     palakkad_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',9)])
    #     malappuram_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',10)])
    #     kozhikkod_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',11)])
    #     wayanad_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',12)])
    #     kannur_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',13)])
    #     kasaragod_venues = request.env['res.partner'].sudo().search([('venue','=',True), ('district_id.id','=',14)])
    #
    #     districts = request.env['place.district'].sudo().search([])
    #
    #     values = {
    #         'trivandrum_venues':trivandrum_venues,
    #         'kollam_venues':kollam_venues,
    #         'pathanamthitta_venues':pathanamthitta_venues,
    #         'alappey_venues':alappey_venues,
    #         'kottayam_venues':kottayam_venues,
    #         'idukki_venues':idukki_venues,
    #         'ernakulam_venues':ernakulam_venues,
    #         'thrissur_venues':thrissur_venues,
    #         'palakkad_venues':palakkad_venues,
    #         'malappuram_venues':malappuram_venues,
    #         'kozhikkod_venues':kozhikkod_venues,
    #         'wayanad_venues':wayanad_venues,
    #         'kannur_venues':kannur_venues,
    #         'kasaragod_venues':kasaragod_venues,
    #         'districts':districts,
    #         'current_user': current_user,
    #         # 'types':types,
    #         # 'places':places,
    #     }
    #     return request.render(
    #
    #     "event_management.venue_page",values)
class SearchListPage(http.Controller):
    @http.route(['/searchlist'], type='http', auth="public",website=True)
    def search_page_controller(self, **args):
        current_user = request.env.user
        district_domain = []
        domain_venue = []
        # print (args.get('district_id'))
        if args.get('district_id'):
            domain_venue = [('venue','=',True),('district_id.id','=',args.get('district_id'))]
            district_domain = [('id','=',args.get('district_id'))]

        venues = request.env['res.partner'].sudo().search(domain_venue)
        districts = request.env['place.district'].sudo().search(district_domain)

        values = {
            'venues':venues,
            'districts':districts,
            'current_user': current_user,
        }
        return request.render(

        "event_management.venue_search_page",values)

class MakeupPage(http.Controller):
    @http.route(['/makeup'], type='http', auth="public",website=True)
    def search_page_controller(self, **args):
        current_user = request.env.user
        # print (args.get('price'))
        makeup_artists = request.env['res.partner'].sudo().search([('makeup_artist','=',True)])
        mehndi_artists = request.env['res.partner'].sudo().search([('mehndi_artist','=',True)])
        packages = request.env['makeup.package'].sudo().search([('makeup_artist','=',True)])
        services = request.env['package.service'].sudo().search([('makeup_artist','=',True)])

        values = {
            'makeup_artists':makeup_artists,
            'mehndi_artists':mehndi_artists,
            'packages':packages,
            'services':services,
            'current_user': current_user,

        }
        return request.render(

        "event_management.makeup_page",values)
class EventDetailsPage(http.Controller):
    @http.route(['/eventdetails'], type='http', auth="public",website=True)
    def event_page_controller(self, **args):
        # print (self)
        # print ('..........')
        # print (district_id)
        current_user = request.env.user

        # print (args.get('price'))
        venues = request.env['res.partner'].sudo().search([('venue','=',True),('district_id','=',args.get('district_id'))])
        districts = request.env['place.district'].sudo().search([('id','=',args.get('district_id'))])

        values = {
            'venues':venues,
            'districts':districts,
            # 'types':types,
            # 'places':places,
            'current_user': current_user,

        }
        return request.render(

        "event_management.event_details_page",values)
class MakeupArtistBookingPage(http.Controller):
    @http.route(['/makeupartistbooking'], type='http', auth="public", website=True)
    def makeup_booking_page_controller(self, **args):
        current_user = request.env.user

        # makeup_artists = request.env['res.partner'].sudo().search([('makeup_artist','=',True)])
        makeup_artists = request.env['artist.artist'].sudo().search([])
        customers = request.env['res.partner'].sudo().search([('customer','=',True)])
        types = request.env['event.management.type'].sudo().search([])
        packages = request.env['makeup.package'].sudo().search([])
        values = {
            'makeup_artists': makeup_artists,
            'customers': customers,
            'types': types,
            'packages':packages,
            'current_user': current_user,

        }
        return request.render("event_management.makeup_artist_booking_page", values)

class BookingPage(http.Controller):
    @http.route(['/booking'], type='http', auth="public",website=True)
    def booking_page_controller(self, **args):
        current_user = request.env.user
        # print(current_user)
        if current_user.id!=4:
            venues = request.env['res.partner'].sudo().search([('venue','=',True)])
            districts = request.env['place.district'].sudo().search([])
            types = request.env['event.management.type'].sudo().search([])
            places = request.env['place.place'].sudo().search([])
            # makeup_artists = request.env['res.partner'].sudo().search([('makeup_artist','=',True)])
            makeup_artists = request.env['artist.artist'].sudo().search([])
            makeup_packages = request.env['makeup.package'].sudo().search([])

            values = {
                'venues':venues,
                'districts':districts,
                'types':types,
                'places':places,
                'makeup_artists':makeup_artists,
                'current_user': current_user,
                'current_user_name': current_user.name,
                'makeup_packages': makeup_packages,

            }

            return request.render(

            "event_management.booking_page",values)
        else:
            return http.redirect_with_hash('/#loginModal')

    @http.route(['/makeupartistbooking/book'], type='http', auth="public", website=True)
    def makeup_booking_page_submit(self, **args):
        current_user = request.env.user
        if current_user:
            artist_name  = int(args.get('artist_name'))
            customer_name = int(args.get('customer_name'))
            event_type = int(args.get('type_id'))
            package = int(args.get('package_id'))
            b_date = args.get('date')
            price = args.get('price')
            # price = venue_obj = request.env['res.partner'].sudo().search([('id','=',venue_id)])
            vals = {
                'artist_name': artist_name,
                'customer_name': customer_name,
                'type_of_event_id': event_type,
                'package': package,
                'booking_date': b_date,
                'rate': price,

            }
            booking_artist = request.env['makeup.artist'].sudo().create(vals)

    @http.route(['/booking/confirm'], type='http', auth="public",website=True)
    def booking_page_submitt(self, **args):
        current_user = request.env.user
        current_user_id = request.env.user.id
        print("name is..........................",current_user.name)
        if current_user.name == 'Administrator':
            print("I am the admin")
            vals = {
                'name': args.get('name'),
                'place_id': int(args.get('place_id')),
                'district_id': int(args.get('district_id')),
                'customer': True,
            }
            new_user = request.env['res.partner'].sudo().create(vals)
            venue_id = int(args.get('venue_id'))
            auditorium_obj = request.env['res.partner'].sudo().browse(venue_id)
            amount = auditorium_obj.amount
            district_id = int(args.get('district_id'))
            place_id = int(args.get('place_id'))
            type_id = int(args.get('type_id'))
            date = args.get('date')
            mobile = args.get('mobile')
            address = args.get('address')
            email = args.get('email')
            name = args.get('name')
            venue_obj = request.env['res.partner'].sudo().search([('id', '=', venue_id)])
            print("name......................", current_user.name)
            vals = {
                'venue_id': venue_id,
                'type_of_event_id': type_id,
                'date': fields.Date.today(),
                'event_date': date,
                'mobile': mobile,
                'district_id': district_id,
                'place_id': place_id,
                # 'package_id':makeup_package,
                # 'makeup_id':makeup_artist_name,
                # 'partner_id':current_user.partner_id.id,
                'partner_id': new_user.id,
                'rent': amount,
                'address':address,
                'email':email,
            }
            booking_event = request.env['event.management'].sudo().create(vals)

        else:
            print("name is..........................", current_user.name)
            auditorium = request.env['res.partner'].sudo().search(
                [('venue', '=', True), ('venue_owner', '=', current_user_id)])
            bookings = False
            vals = {
                'name': args.get('name'),
                'place_id': auditorium.place_id.id,
                'district_id': auditorium.district_id.id,
                'customer': True,
            }
            new_user = request.env['res.partner'].sudo().create(vals)

            if auditorium:
                print("yessssssssssssssssssssss")
                # venue_id = int(args.get('venue_id'))
                venue_id = auditorium.id
                amount = auditorium.amount
                # district_id = int(args.get('district_id'))
                district_id = auditorium.district_id.id
                # place_id = int(args.get('place_id'))
                place_id = auditorium.place_id.id
                type_id =  int(args.get('type_id'))
                date = args.get('date')
                mobile = args.get('mobile')
                address = args.get('address')
                email = args.get('email')
                name = args.get('name')
                # makeup_package =  int(args.get('makeup_package_id'))
                # makeup_artist_name =  int(args.get('artist_name'))
                venue_obj = request.env['res.partner'].sudo().search([('id','=',venue_id)])


                vals = {
                        'venue_id':venue_id,
                        'type_of_event_id':type_id,
                        'date':fields.Date.today(),
                        'event_date':date,
                        'mobile':mobile,
                        'district_id':district_id,
                        'place_id':place_id,
                        # 'package_id':makeup_package,
                        # 'makeup_id':makeup_artist_name,
                        # 'partner_id':current_user.partner_id.id,
                        'partner_id':new_user.id,
                        'rent':amount,
                        'address': address,
                        'email': email,
                }
                booking_event = request.env['event.management'].sudo().create(vals)
            # print(venue_id,type_id,date,mobile,name,venue_obj.district_id.id,venue_obj.place_id.id)
            # booking_event = request.env['customer.enquiry.details'].sudo().create(vals)


            # booking_event.action_create_quote()
            # booking_event.action_enquiry_confirm()
            # booking_event.action_create_event()
            # print ("My bookingssssssssssssssssss///////////...................")
            # print (booking_event.id)
            # venues = request.env['res.partner'].sudo().search([('venue', '=', True)])
            # districts = request.env['place.district'].sudo().search([])
            # types = request.env['event.management.type'].sudo().search([])
            # places = request.env['place.place'].sudo().search([])
            # makeup_artists = request.env['res.partner'].sudo().search([('makeup_artist', '=', True)])

            # values = {
            #     'venues': venues,
            #     'districts': districts,
            #     'types': types,
            #     'places': places,
            #     'makeup_artists': makeup_artists,
            # }
            # return request.render("survey.survey_auth_required", {'survey': survey_sudo, 'redirect_url': redirect_url})

        # return http.redirect_with_hash('/booking')

        return http.redirect_with_hash("/web#id=&action=196&model=account.move&view_type=form&cids=1&menu_id=101")

            # response = redirect("/booking")
            # return response


    @http.route(['/ajax/reservations/get/<int:venue_id>'], type='http', auth="public",website=True,csrf=False)
    def data_calender_ajax(self, venue_id,**args):
        # current_user_id = request.env.user.id
        # auditorium = request.env['res.partner'].sudo().search(
        #     [('venue', '=', True), ('venue_owner', '=', current_user_id)])
        # bookings = False
        # if auditorium:
        #     bookings = request.env['event.management'].sudo().search([('venue_id', '=', auditorium.id)])
        #     print("bookings", bookings)

        venue_id = venue_id
        values=[{
            'title': "Title",
            'start': '2018-02-01',
            'end': '2018-02-02',
            # 'bookings':bookings,
        }]
        # print ("valueeeeeeeeeeeeeeeeessssssssssssssssssssss")
        return values


class RegistrationPage(http.Controller):
    @http.route(['/registration'], type='http', auth="public",website=True)
    def booking_page_controller(self, **args):
        current_user = request.env.user

        # venues = request.env['res.partner'].sudo().search([('venue','=',True),])
        # districts = request.env['place.district'].sudo().search([])
        # types = request.env['event.management.type'].sudo().search([])
        # places = request.env['place.place'].sudo().search([])

        values = {
            'current_user': current_user,

            # 'venues':venues,
            # 'districts':districts,
            # 'types':types,
            # 'places':places,
        }
        return request.render(

        "event_management.registration_page",values)


class DecorationPage(http.Controller):
    @http.route(['/decoration'], type='http', auth="public",website=True)
    def decoration_page_controller(self, **args):
        current_user = request.env.user

        # venues = request.env['res.partner'].sudo().search([('venue','=',True),])
        # districts = request.env['place.district'].sudo().search([])
        # types = request.env['event.management.type'].sudo().search([])
        # places = request.env['place.place'].sudo().search([])

        values = {
            'current_user': current_user,

            # 'venues':venues,
            # 'districts':districts,
            # 'types':types,
            # 'places':places,
        }
        return request.render(

        "event_management.decoration_page",values)


class EntertainmentPage(http.Controller):
    @http.route(['/entertainment'], type='http', auth="public",website=True)
    def entertainment_page_controller(self, **args):
        current_user = request.env.user

        # venues = request.env['res.partner'].sudo().search([('venue','=',True),])
        # districts = request.env['place.district'].sudo().search([])
        # types = request.env['event.management.type'].sudo().search([])
        # places = request.env['place.place'].sudo().search([])

        values = {
            # 'venues':venues,
            # 'districts':districts,
            # 'types':types,
            # 'places':places,
            'current_user': current_user,

        }
        return request.render(

        "event_management.entertainment_page",values)


class CateringServicesPage(http.Controller):
    @http.route(['/catering'], type='http', auth="public",website=True)
    def catering_page_controller(self, **args):
        current_user = request.env.user

        # venues = request.env['res.partner'].sudo().search([('venue','=',True),])
        # districts = request.env['place.district'].sudo().search([])
        # types = request.env['event.management.type'].sudo().search([])
        # places = request.env['place.place'].sudo().search([])

        values = {
            'current_user': current_user,

            # 'venues':venues,
            # 'districts':districts,
            # 'types':types,
            # 'places':places,
        }
        return request.render(

        "event_management.catering_page",values)


class VideographyPage(http.Controller):
    @http.route(['/videography'], type='http', auth="public",website=True)
    def video_page_controller(self, **args):
        current_user = request.env.user

        # venues = request.env['res.partner'].sudo().search([('venue','=',True),])
        # districts = request.env['place.district'].sudo().search([])
        # types = request.env['event.management.type'].sudo().search([])
        # places = request.env['place.place'].sudo().search([])

        values = {
            # 'venues':venues,
            # 'districts':districts,
            # 'types':types,
            # 'places':places,
            'current_user': current_user,

        }
        return request.render(

        "event_management.photography_page",values)


class AllVenueListPage(http.Controller):
    @http.route(['/venues'], type='http', auth="public",website=True)
    def all_venue_list_page_controller(self, **args):
        current_user = request.env.user
        # print (http.request.env['ir.config_parameter'].sudo().get_param('web.base.url') ) # BASE URL
        # print(http.request.httprequest)
        # print(request.httprequest.url)

        # district_domain = []
        # domain_venue = []
        # print (args.get('district_id'))
        # if args.get('district_id'):
        #     domain_venue = [('venue','=',True),('district_id.id','=',args.get('district_id'))]
        #     district_domain = [('id','=',args.get('district_id'))]
        # window.location.search

        event_type_string = (request.httprequest.url).split('?')
        venues = request.env['res.partner'].sudo().search([('venue','=',True)])
        # districts = request.env['place.district'].sudo().search(district_domain)
        # print("keeeeeeeeeeeeeeeeeeeeeeeejhukgggggggggggggggggggggggggggggggggggggggggggg")
        event_type = event_type_string[1]
        if event_type == 'Reception':
            event_type = 'Wedding Reception'
        elif event_type == 'Baby':
            event_type = 'Baby Shower'
        elif event_type == 'Birthday':
            event_type = 'Birthday Party'

        values = {
            'venues':venues,
            'event_type':event_type,
            'current_user': current_user,
        }
        return request.render(

        "event_management.all_venue_list_page",values)

