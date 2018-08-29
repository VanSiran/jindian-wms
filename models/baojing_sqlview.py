# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class JianceBaojingSqlView(models.Model):
    _name = 'wms.sqlview.jiancebaojing'
    _description = '检测报警'
    _auto = False
    _rec_name = 'geti'

    geti = fields.Many2one('wms.geti', '编号', readonly=True)
    beijianext = fields.Many2one('wms.beijianext', '备件型号', readonly=True)
    huowei = fields.Many2one('wms.huowei', '货位', readonly=True)
    jiancedaoqiri = fields.Date('检测到期日', readonly=True)
    cangku = fields.Many2one('wms.cangku', '仓库', readonly=True)
    shengyutianshu = fields.Integer('剩余天数', readonly=True)
    baojingdengji = fields.Selection([
        ('1', 'Ⅰ 级报警'),
        ('2', 'Ⅱ 级报警'),
        ('3', 'Ⅲ 级报警'),
        ('-1', '过期未检')], string="报警等级", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = '''
        CREATE OR REPLACE VIEW wms_sqlview_jiancebaojing AS (
        SELECT *,
        CASE
        WHEN shengyutianshu < 0 THEN '-1'
        WHEN shengyutianshu >=0 AND shengyutianshu < 5 THEN '1'
        WHEN shengyutianshu >= 5 AND shengyutianshu < 15 THEN '2'
        ELSE '3'
        END AS baojingdengji
        FROM (
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
            ) AS tmp)'''
        self.env.cr.execute(query)

# class KucunBaojingSqlView(models.Model):
#     _name = 'wms.sqlview.kucunbaojing'
#     _description = '库存报警'
#     _auto = False
#     _rec_name = 'beijianext'
#
#     beijianext = fields.Many2one('wms.beijianext', '备件型号', readonly=True)
#     cangku = fields.Many2one('wms.cangku', '仓库', readonly=True)
#     baojingleixing = fields.Selection([
#         ('1', '库存不足'),
#         ('2', '库存过多')], string="报警类型", readonly=True)
#
#     @api.model_cr
#     def init(self):
#         tools.drop_view_if_exists(self.env.cr, self._table)
#         query = '''
#         CREATE OR REPLACE VIEW wms_sqlview_kucunbaojing AS (
#         SELECT *,
#         CASE
#         WHEN shengyutianshu < 0 THEN '-1'
#         WHEN shengyutianshu >=0 AND shengyutianshu < 5 THEN '1'
#         WHEN shengyutianshu >= 5 AND shengyutianshu < 15 THEN '2'
#         ELSE '3'
#         END AS baojingdengji
#         FROM (
#             SELECT count(*) AS shuliang
#             FROM wms_geti AS geti
#             JOIN wms_beijianext AS beijianext ON (geti.beijianext = beijianext.id)
#             JOIN wms_huowei AS huowei ON (geti.huowei = huowei.id)
#             JOIN wms_kucuncelue AS kucuncelue ON (kucuncelue.id = huowei.kucuncelue)
#             WHERE geti.zhuangtai = 'zaiku'
#             ) AS tmp)'''
#         self.env.cr.execute(query)
