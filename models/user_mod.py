# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class UserMod(models.Model):
    _inherit = 'res.users'

    cangku = fields.Many2one('wms.cangku', '仓库管理权')
