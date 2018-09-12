# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools
from odoo.exceptions import ValidationError


class YikuWiz(models.TransientModel):
    _name = "wms.wizard.yiku"
    _description = "移库向导"

    state = fields.Selection([
        ('selcangku', '选仓库'),
        ('complete', '信息确认'),
        ], default='selcangku')

    cangku = fields.Many2one('wms.cangku.mirror', '移动到哪个仓库？')
    beijianfull = fields.Char()
    # geti = fields.Many2one('wms.geti', '个体')


    @api.model
    def default_get(self, fields):
        res = super(YikuWiz, self).default_get(fields)
        geti = self.env['wms.geti'].browse(self.env.context['geti'])
        beijianext = geti.beijianext
        res['beijianfull'] = '%s（%s）' % (beijianext.beijian.name, beijianext.name)
        return res

    @api.multi
    def save_yiku(self):
        self.ensure_one()
        if not self.cangku:
            raise ValidationError("请选择仓库！")
        geti = self.env['wms.geti'].browse(self.env.context['geti'])
        # NOTE: 此处的状态判断要与geti视图中的按钮显示条件一致
        if geti.zhuangtai not in ('zaiku', 'daibaofei', 'daijiance'):
            raise ValidationError("备件正在移库，若界面未更新，请刷新网页。%s" % geti.xuliehao)
        geti.zhuangtai_core = 'yikuqu'
        self.env['wms.lishijilu'].create({
            'xinxi': '从"%s"移动到"%s",等待接收方收货' % (geti.huowei.complete_bianma, cangku.name),
            'geti_id': geti.id,})
        self.state = 'complete'
        return {'type': 'ir_actions_act_window_donothing'}
