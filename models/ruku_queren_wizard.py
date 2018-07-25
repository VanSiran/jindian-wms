# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools
from odoo.exceptions import ValidationError


class Rukuqueren(models.TransientModel):
    _name = "wms.wizard.rukuqueren"
    _description = "入库确认向导"

    bianma = fields.Char('选择的货位是', required=True)

    beijianfull = fields.Char()
    cangkuname = fields.Char()

    @api.model
    def default_get(self, fields):
        res = super(Newhuowei, self).default_get(fields)
        res['beijianfull'] = self._compute_beijianfull()
        res['cangkuname'] = self._compute_cangkuname()
        return res

    def _compute_cangkuname(self):
        cangku = self.env['wms.cangku'].browse(self.env.context['cangku'])
        return cangku.name

    def _compute_beijianfull(self):
        beijianext = self.env['wms.beijianext'].browse(self.env.context['beijianext'])
        return '%s（%s）' % (beijianext.beijian.name, beijianext.name)

    def save_huowei(self):
        Inventory = self.env['wms.huowei']
        for wizard in self:
            inventory = Inventory.create({
                'bianma': wizard.bianma,
                'cangku': self.env.context['cangku'],
                'beijianext': self.env.context['beijianext'],
            })
        if self.env.context.get('wizard', -1) != -1:
            wiz = self.env['wms.wizard.ruku'].browse(self.env.context['wizard'])
            if wiz:
                wiz.huowei = inventory
                if wiz.state != 'fillform':
                    return wiz.check_missing_settings()
