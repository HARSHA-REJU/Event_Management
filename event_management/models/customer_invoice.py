# -*- coding: utf-8 -*-
"""Customer Invoice"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    booking_id = fields.Many2one('event.management')
    fortuna_discount = fields.Float()
    address = fields.Text()