# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools
from odoo.exceptions import ValidationError
from xmlrpc.client import ServerProxy
import json

import logging
_logger = logging.getLogger(__name__)

class Rukuqueren(models.TransientModel):
    _name = "wms.wizard.rukuqueren"
    _description = "入库确认向导"

    # rukus = []
    state = fields.Selection([
        ('confirm', '信息确认'),
        ('complete', '完成'),
        ], default='confirm')

    beijianfull = fields.Char('入库备件')
    image = fields.Binary("备件图片")
    rukushuliang = fields.Integer('入库数量')
    huowei = fields.Char('货位')
    changjia = fields.Char('生产厂家')
    shengchanriqi = fields.Date('生产日期')
    pihao = fields.Char("批次号")
    print_info = fields.Text()
    # allxuliehao = fields.Text('入库的编号')

    @api.model
    def default_get(self, fields):
        res = super(Rukuqueren, self).default_get(fields)
        res['beijianfull'], res['image'] = self._compute_beijianfull()
        res['huowei'] = self._compute_huowei_str()
        res['changjia'] = self._compute_changjia_str()
        # res['beijianext'] = self.env.context['beijianext']
        res['rukushuliang'] = self.env.context['rukushuliang']
        res['shengchanriqi'] = self.env.context['shengchanriqi']
        res['pihao'] = self.env.context['pihao']
        return res

    def _compute_beijianfull(self):
        beijianext = self.env['wms.beijianext'].browse(self.env.context['beijianext'])
        return '%s（%s）' % (beijianext.beijian.name, beijianext.name), beijianext.image

    def _compute_huowei_str(self):
        hw = self.env['wms.huowei'].browse(self.env.context['huowei'])
        return hw.complete_bianma

    def _compute_changjia_str(self):
        cj = self.env['wms.changjia'].browse(self.env.context['changjia'])
        return cj.name


    def save_geti(self):
        rukus = {'xlh': []}
        beijianext = self.env['wms.beijianext'].browse(self.env.context['beijianext'])
        for i in range(0, self.rukushuliang):
            z = self.env['wms.geti'].create({
                'xuliehao': self.env['ir.sequence'].next_by_code('wms.geti'),
                'beijianext': self.env.context['beijianext'],
                'huowei': self.env.context['huowei'],
                'changjia': self.env.context['changjia'] if self.env.context['changjia'] else False,
                'shengchanriqi': self.shengchanriqi,
                'pihao': self.pihao,
                'zhuangtai_core': 'jiashang',})
            self.env['wms.lishijilu'].create({
                'xinxi': '入库到"%s"' % (z.huowei.complete_bianma),
                'geti_id': z.id,})
            rukus['xlh'].append(z.xuliehao)
        rukus.update({
            'hw': self.huowei,
            'ph': self.pihao,
            'bjext': self.beijianfull,
            'cj': self.changjia,
            'scrq': self.shengchanriqi,})
        self.state = 'complete'
        enc = json.JSONEncoder().encode
        self.print_info = enc(rukus)
        return {'type': "ir_actions_act_window_donothing",}

    def close_all(self):
        return {'type': 'ir_actions_act_window_close_all'}

    def print_code(self):
        return {
            'type': 'ir_actions_print_code',
            'data': self.print_info,
            'url': 'http://localhost:8080/jsonrpc'}
