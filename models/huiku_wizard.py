# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools
from odoo.exceptions import ValidationError


class HuikuWiz(models.TransientModel):
    _name = "wms.wizard.huiku"
    _description = "回库向导"

    # rukus = []
    state = fields.Selection([
        ('dest', '回库'),
        ('complete', '完成'),
        ], default='dest')

    huowei = fields.Many2one('wms.huowei', '回库货位')
    kucuncelue = fields.Many2one('wms.kucuncelue')
    cangkuname = fields.Char()
    beijianfull = fields.Char()
    chukuhuowei = fields.Many2one('wms.huowei', '出库货位')

    @api.model
    def default_get(self, fields):
        res = super(HuikuWiz, self).default_get(fields)
        geti = self.env['wms.geti'].browse(self.env.context['geti'])
        beijianext = geti.beijianext
        res['kucuncelue'] = geti.huowei.kucuncelue.id
        res['beijianfull'] = '%s（%s）' % (beijianext.beijian.name, beijianext.name)
        res['chukuhuowei'] = geti.huowei.id
        res['cangkuname'] = geti.huowei.cangku.name
        return res

    @api.multi
    def save_huiku(self):
        self.ensure_one()
        if not self.huowei:
            raise ValidationError("请选择货位！")
        geti = self.env['wms.geti'].browse(self.env.context['geti'])
        # NOTE: 此处的状态判断要与geti视图中的按钮显示条件一致
        if geti.zhuangtai not in ('chuku', 'yiku'):
            raise ValidationError("备件已经回库，若界面未更新，请刷新网页。%s" % geti.xuliehao)
        geti.huowei = self.huowei
        geti.zhuangtai_core = 'jiashang'
        self.env['wms.lishijilu'].create({
            'xinxi': '回库到"%s"' % self.huowei.complete_bianma,
            'geti_id': geti.id,})
        self.state = 'complete'
        return {'type': 'ir_actions_act_window_donothing'}

    def newhuowei_wizard_act_window(self):
        return {
            'name': '为此备件分配货位',
            'type': 'ir.actions.act_window',
            'res_model': 'wms.wizard.newhuowei',
            'views': [[self.env.ref('wms.newhuowei_wizard_view').id, 'form']],
            'target': 'new_no_close',
            'context': {
                'cangku': self.kucuncelue.cangku.id,
                'beijianext': self.kucuncelue.beijianext.id,}}
