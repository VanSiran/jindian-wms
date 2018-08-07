# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class JianceBaojingSqlView(models.Model):
    _name = 'wms.sqlview.jiancebaojing'
    _auto = False

    cangku = fields.Many2one('wms.cangku', '仓库管理权')
    xuliehao = fields.Char('序列号', readonly=True)
    beijianext = fields.Many2one('wms.beijianext', '备件型号', readonly=True)
    huowei = fields.Many2one('wms.huowei', '货位', readonly=True)
    jiancedaoqiri = fields.Data('检测到期日', readonly=True)
