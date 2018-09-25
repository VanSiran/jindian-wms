# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools
from odoo.exceptions import ValidationError


class ChukuWiz(models.TransientModel):
    _name = "wms.wizard.chuku"
    _description = "出库向导"

    # rukus = []
    state = fields.Selection([
        ('confirm', '确认'),
        ('dest', '出库'),
        ('complete', '完成'),
        ], default='confirm')

    bianma = fields.Char('设备')
    beijianfull = fields.Char()
    huoweiname = fields.Char()

    @api.model
    def default_get(self, fields):
        res = super(ChukuWiz, self).default_get(fields)
        geti = self.env['wms.geti'].browse(self.env.context['geti'])
        beijianext = geti.beijianext
        res['beijianfull'] = '%s（%s）' % (beijianext.beijian.name, beijianext.name)
        res['huoweiname'] = geti.huowei.complete_bianma
        # NOTE: 待报废添加的时候，还需要改这里
        res['state'] = 'confirm' if geti.zhuangtai == 'daijiance' else 'dest'
        # if self.env['wms.sqlview.jiancebaojing'].search_count([('geti','=',self.id)]):
        #     raise ValidationError('快过期了')
        return res

    @api.multi
    def continues(self):
        self.ensure_one()
        self.state = 'dest'
        return {'type': 'ir_actions_act_window_donothing'}

    @api.multi
    def save_chuku(self):
        self.ensure_one()
        geti = self.env['wms.geti'].browse(self.env.context['geti'])
        # NOTE: 此处的状态判断要与geti视图中的按钮显示条件一致
        if geti.zhuangtai not in ('zaiku', 'daibaofei', 'daijiance'):
            raise ValidationError("备件已经出库，若界面未更新，请刷新网页。%s" % geti.xuliehao)
        geti.zhuangtai_core = 'chukuqu'
        self.env['wms.lishijilu'].create({
            'xinxi': '从"%s"出库,用于"%s"' % (self.huoweiname, self.bianma),
            'geti_id': geti.id,})
        self.state = 'complete'
        return {'type': 'ir_actions_act_window_donothing'}
