# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class JianceBaojingSqlView(models.Model):
    _name = 'wms.sqlview.jiancebaojing'
    _description = '检测报警'
    _auto = False
    _rec_name = 'beijianext'

    geti = fields.Many2one('wms.geti', '序列号', readonly=True)
    beijianext = fields.Many2one('wms.beijianext', '备件型号', readonly=True)
    huowei = fields.Many2one('wms.huowei', '货位', readonly=True)
    jiancedaoqiri = fields.Date('检测到期日', readonly=True)
    cangku = fields.Many2one('wms.cangku', '仓库', readonly=True)
    shengyutianshu = fields.Integer('剩余天数', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = '''
        CREATE OR REPLACE VIEW wms_sqlview_jiancebaojing AS (
        SELECT geti.id AS id,
        geti.id AS geti,
        geti.huowei AS huowei,
        geti.beijianext AS beijianext,
        geti.jiancedaoqiri AS jiancedaoqiri,
        kucuncelue.cangku AS cangku,
        EXTRACT(DAY from geti.jiancedaoqiri - now()) AS shengyutianshu
        FROM wms_geti AS geti
        JOIN wms_beijianext AS beijianext ON (geti.beijianext = beijianext.id)
        JOIN wms_huowei AS huowei ON (geti.huowei = huowei.id)
        JOIN wms_kucuncelue AS kucuncelue ON (kucuncelue.id = huowei.kucuncelue)
        WHERE geti.zhuangtai = 'zaiku' AND beijianext.jiancebaojing = TRUE AND
        EXTRACT(DAY from geti.jiancedaoqiri - now()) <= 30
        ORDER BY shengyutianshu DESC
        )'''
        self.env.cr.execute(query)
