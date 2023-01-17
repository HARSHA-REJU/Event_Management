# -*- coding: utf-8 -*-
from odoo import fields, models
from datetime import datetime

class BookingWizard(models.TransientModel):
    """Class for wizard"""
    _name = 'booking.wizard'
    _description = 'Booking Wizard'


