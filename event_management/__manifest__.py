{
    'name': 'Event Management',
    'version': '16.0.1.0.0',
    'summary': """Core Module for Managing Different Types Of Events.""",
    'description': """Core Module for Managing Different Types Of Events""",
    "category": "Industry",
    'author': 'Hiworth Solutions',
    'company': 'Hiworth Solutions',
    'maintainer': 'Hiworth Solutions',
    'website': "https://www.https://hiworthsolutions.com",
    'depends': ['product', 'account', 'website','mail',],
    'data': ['security/event_security.xml',
             'security/ir.model.access.csv',
             'views/event_type_view.xml',
             'views/customer_enquiry_details.xml',
             'views/res_partner_view.xml',
             'views/district_dashboard_view.xml',
             'views/locations.xml',
             'views/event_management_view.xml',
             'views/dashboard.xml',
             'views/category.xml',
             'views/photographers.xml',
             'views/catering.xml',
             'views/entertainment.xml',
             # 'views/decoration.xml',

             'views/hide_menu.xml',
             'data/email_template.xml',
             'data/event_management.xml',
             'data/place_districts.xml',
             'reports/event_management_pdf_report.xml',
             'reports/pdf_report_template.xml',
             'reports/booking_summary_template.xml',
             'wizards/event_management_wizard.xml',
             'wizards/booking_summary_report_wizard.xml',
             'wizards/enquiry_report_wizard.xml',
             'wizards/makeup_artist_booking.xml',
             'static/src/xml/style_sheet.xml',
             'static/src/xml/home_page.xml',
             'static/src/xml/contact_page.xml',
             'static/src/xml/venu_list_page_horizontal.xml',
             'static/src/xml/venue_filter_page.xml',
             'static/src/xml/makeup.xml',
             'static/src/xml/event_details_page.xml',
             'static/src/xml/booking_page.xml',
             'static/src/xml/makeup_artist_booking.xml',
             'static/src/xml/registration_login_template.xml',
             'static/src/xml/catering_service_page.xml',
             'static/src/xml/decorations_page.xml',
             'static/src/xml/entertainment_page.xml',
             'static/src/xml/photography_page.xml',
             'static/src/xml/account_summary.xml',
             'static/src/xml/all_venu_list_page.xml',
             ],
    'assets': {
        'web.assets_backend': [
            "event_management/static/src/css/event_dashboard.css",
            "event_management/static/src/js/action_manager.js"
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
# -*- coding: utf-8 -*-

