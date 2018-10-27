# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools
from odoo.exceptions import ValidationError
import traceback

# import logging
# _logger = logging.getLogger(__name__)

class YikuQuerenWizard(models.TransientModel):
    _name = "wms.wizard.yikuqueren"
    _description = "移库确认向导"

    # name = fields.Char(default="入库")
    state = fields.Selection([
        ('selhuowei', '选货位'),
        ('confirm', '信息确认'),
        ], default='selcangku')

    huowei = fields.Many2one('wms.huowei', '选择放置货位')
    beijianext = fields.Many2one('wms.beijianext', '备件型号')
    cangku = fields.Many2one('wms.cangku', '目标仓库')

    @api.multi
    def progress_next(self):
        self.ensure_one()
        if not self.huowei:
            raise ValidationError("请填写货位！")
        return {
            'name': '入库确认',
            'type': 'ir.actions.act_window',
            'res_model': 'wms.wizard.rukuqueren',
            'views': [[self.env.ref('wms.rukuqueren_wizard_view').id, 'form']],
            'target': 'new_no_close',
            'context': {
                'beijianext': self.beijianext.id,
                'rukushuliang': self.rukushuliang,
                'huowei': self.huowei.id,
                'changjia': self.changjia.id if self.changjia else False,
                'shengchanriqi': self.shengchanriqi,
                'pihao': self.pihao,
                'hide_close_btn': True,}}


    @api.model
    def default_get(self, fields):
        res = super(YikuQuerenWizard, self).default_get(fields)
        res['cangku'] = self.env.context['cangku']
        res['beijianext'] = self.env.context['beijianext']
        huowei = self.env['wms.huowei'].search([
            ('beijianext', '=', res['beijianext']),
            ('cangku', '=', res['cangku'])],
            order='create_date desc', limit=1)
        if huowei:
            res['huowei'] = huowei.id
        return res

    def newhuowei_wizard_act_window(self):
        return {
            'name': '为此备件分配货位',
            'type': 'ir.actions.act_window',
            'res_model': 'wms.wizard.newhuowei',
            'views': [[self.env.ref('wms.newhuowei_wizard_view').id, 'form']],
            'target': 'new_no_close',
            'context': {
                'cangku': self.cangku.id,
                'beijianext': self.beijianext.id,}}
