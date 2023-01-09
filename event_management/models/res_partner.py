from odoo import models, fields, api, _
from ast import literal_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    place_id = fields.Many2one('place.place')
    district_id = fields.Many2one('place.district')

    venue = fields.Boolean()

    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=False)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=False)

    event_count = fields.Integer(string="# of Events",
                                 compute='_compute_partner_wise_event_count')

    def _compute_partner_wise_event_count(self):
        for records in self:
            events = self.env['event.management'].search([
                ('venue_id', '=', records.id)])
            records.event_count = len(events)
        return

    def _get_action(self, action_xml_id):
        action = self.env['ir.actions.actions']._for_xml_id(action_xml_id)
        if self:
            action['display_name'] = self.display_name
        context = {
            'search_default_venue_id': [self.id],
            'default_venue_id': self.id,
        }
        # domain=[('venue_id','=',self.id)]

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        # action['domain'] = domain
        return action

    # def _get_action(self, action_xml_id):
    #     action = self.env['ir.actions.actions']._for_xml_id(action_xml_id)
    #     if self:
    #         action['display_name'] = self.display_name
    #     context = {
    #         'search_default_venue_id': [self.id],
    #         'default_venue_id': self.id,
    #     }
    #     domain=[('venue_id','=',self.id)]
    #
    #     action_context = literal_eval(action['context'])
    #     context = {**action_context, **context}
    #     action['context'] = context
    #     action['domain'] = domain
    #     return action


    # def get_event_partner_action_event(self):
    #     return self._get_action(
    #         'event_management.event_management_action_view_kanban')

    def get_event_partner_action_event(self):
        return self._get_action(
            'event_management.event_management_type_action_view_dashboard')

