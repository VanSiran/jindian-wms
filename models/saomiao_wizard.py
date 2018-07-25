# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools
from odoo.exceptions import ValidationError


class SaomiaoWizard(models.TransientModel):
    _name = "wms.wizard.saomiao"
    _description = "扫描向导"

    xuliehao = fields.Char(string="序列号扫描输入", required=True)
    info = fields.Char()

    @api.model
    def default_get(self, fields):
        res = super(SaomiaoWizard, self).default_get(fields)
        res['info'] = self.env.context.get('info', '请扫码')
        return res

    @api.multi
    def submit(self):
        self.ensure_one()
        res = self.env['wms.geti'].search([('xuliehao', '=', self.xuliehao)], limit=1)
        return {
            'name': '查询结果',
            'type': 'ir.actions.act_window',
            'res_model': 'wms.geti',
            'res_id': res.id,
            'views': [[self.env.ref('wms.geti_ro_form_view').id, 'form']],
            'target': 'new'} if res else {
            'name': '扫码查询',
            'type': 'ir.actions.act_window',
            'res_model': 'wms.wizard.saomiao',
            'views': [[self.env.ref('wms.saomiao_wizard_view').id, 'form']],
            'target': 'new',
            'context': {'info': "未找到备件，请重新扫描"}}
