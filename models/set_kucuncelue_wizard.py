# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools

class SetKucuncelue(models.TransientModel):
    _name = "wms.wizard.setkucuncelue"
    _description = "备件库存策略设置向导"

    xiaxian = fields.Integer('库存下限', required=True, default=0)
    shangxian = fields.Integer('库存上限', required=True, default=0)
    xiaxianbaojing = fields.Boolean('打开下限报警', default=False)
    shangxianbaojing = fields.Boolean('打开上限报警', default=False)
    baojingdengji = fields.Selection([
        ('1', 'Ⅰ级报警'),
        ('2', 'Ⅱ级报警'),
        ('3', 'Ⅲ级报警')], string='报警等级')

    beijianfull = fields.Char()
    cangkuname = fields.Char()

    @api.model
    def default_get(self, fields):
        res = super(SetKucuncelue, self).default_get(fields)
        res['beijianfull'] = self._compute_beijianfull()
        res['cangkuname'] = self._compute_cangkuname()
        return res

    def _compute_cangkuname(self):
        cangku = self.env['wms.cangku'].browse(self.env.context['cangku'])
        return cangku.name

    def _compute_beijianfull(self):
        beijianext = self.env['wms.beijianext'].browse(self.env.context['beijianext'])
        return '%s（%s）' % (beijianext.beijian.name, beijianext.name)

    @api.multi
    def save_shezhi(self):
        Inventory = self.env['wms.kucuncelue']
        for wizard in self:
            Inventory.create({
                'xiaxian': wizard.xiaxian,
                'shangxian': wizard.shangxian,
                'xiaxianbaojing': wizard.xiaxianbaojing,
                'shangxianbaojing': wizard.shangxianbaojing,
                'baojingdengji': wizard.baojingdengji,
                'cangku': self.env.context['cangku'],
                'beijianext': self.env.context['beijianext'],})
        if self.env.context.get('wizard', -1) != -1:
            wiz = self.env['wms.wizard.ruku'].browse(self.env.context['wizard'])
            if wiz:
                return wiz.check_missing_settings()
