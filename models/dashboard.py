# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class Dashboard(models.Model):
    _name = "wms.view.dashboard"
    _description = "仪表盘"

    name = fields.Char(string="动作")
    type = fields.Char("类型")
    action = fields.Many2one('ir.actions.act_window')
    actionc = fields.Many2one('ir.actions.client')

    action_id = fields.Integer(compute="_compute_actionid")

    @api.depends('action', 'actionc')
    def _compute_actionid(self):
        for s in self:
            if s.action:
                s.action_id = s.action.id
            if s.actionc:
                s.action_id = s.actionc.id
    # view = fields.Many2one('ir.ui.view')
    # model = fields.Char()

    # @api.multi
    # def run_action(self):
    #     self.ensure_one()
    #     return {
    #         'name': self.name,
    #         'type': 'ir.actions.act_window',
    #         'res_model': self.model,
    #         'views': [[self.view.id, 'form']],
    #         'target': 'new',
    #         'context': {}}
