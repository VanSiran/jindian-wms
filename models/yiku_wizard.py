# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools
from odoo.exceptions import ValidationError
import traceback

# import logging
# _logger = logging.getLogger(__name__)

class YikuWizard(models.TransientModel):
    _name = "wms.wizard.yiku"
    _description = "移库向导"

    # name = fields.Char(default="入库")
    state = fields.Selection([
        ('selcangku', '选仓库'),
        ('confirm', '信息确认'),
        ], default='selcangku')

    cangku = fields.Many2one('wms.cangku', '选择要管理的仓库')
    beijian = fields.Many2one('wms.beijian', '备件名称')
    beijianext = fields.Many2one('wms.beijianext', '备件型号')

    tbeijians = fields.Many2many('wms.beijian')
    tbeijianexts = fields.Many2many('wms.beijianext')
    info = fields.Char()

    @api.constrains('rukushuliang')
    def constrains_rukushuliang(self):
        if not self.rukushuliang or self.rukushuliang < 1:
            raise ValidationError("入库数量不能小于 1！")


    @api.multi
    def progress_next(self):
        self.ensure_one()
        if self.state == 'selcangku':
            if not self.cangku:
                raise ValidationError("请选择仓库！")
            self.state = 'selbeijianext'
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
        return {'type': "ir_actions_act_window_donothing",}

    @api.multi
    def progress_prev(self):
        self.ensure_one()
        if self.state == 'selbeijianext':
            self.state = 'selcangku'
        elif self.state == 'fillform':
            self.state = 'selbeijianext'
        # elif self.state == 'confirm':
        #     self.state = 'fillform'
        return {'type': "ir_actions_act_window_donothing",}
