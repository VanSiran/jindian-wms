# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api, tools
import datetime

import logging
_logger = logging.getLogger(__name__)

class BJGeTi(models.Model):
    _name = 'wms.geti'
    _description = "备件个体"
    _rec_name = 'xuliehao'
    _sql_constraints = [
        ('xuliehao_uniq', "UNIQUE (xuliehao)", '个体序列号必须是唯一的')
    ]

    xuliehao = fields.Char('序列号', required=True, index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('wms.geti'))
    beijianext = fields.Many2one('wms.beijianext', "备件型号", required=True)
    huowei = fields.Many2one('wms.huowei', '货位', required=True)
    zhuangtai = fields.Selection([
        ('zaiku', '在库备用'),
        ('chuku', '出库'),
        ('baofei', '报废'),
        ('daibaofei', '待报废'),
        ('daiyiku', '待移库')], required=True, string="备件状态")
    changjia = fields.Many2one('wms.changjia', '厂家')
    shengchanriqi = fields.Date('生产日期')
    jiancedaoqiri = fields.Date('检测到期日')
    pihao = fields.Char("批次号")
    data = fields.Text('附加数据')

    lishijilu = fields.One2many('wms.lishijilu', 'geti_id', string='历史记录')
    beijian = fields.Many2one(string='备件名称', related='beijianext.beijian')
    shiyongshebei = fields.Many2many(string='适用设备', related='beijianext.shiyongshebei')
    cangku = fields.Many2one(string='所属仓库', related='huowei.cangku', store=True)
    image = fields.Binary(string='图片', related='beijianext.image')

    @api.multi
    def chuku(self):
        self.ensure_one()
        self.zhuangtai = 'chuku'
        self.env['wms.lishijilu'].create({
            'xinxi': '从"%s"出库' % self.huowei.complete_bianma,
            'geti_id': self.id,})

    def _get_due_date(self, start, days):
        DATE_FORMAT = "%Y-%m-%d"
        return (datetime.datetime.strptime(start, DATE_FORMAT) + datetime.timedelta(days=days)).strftime(DATE_FORMAT)

    @api.multi
    def jiance(self):
        self.ensure_one()
        if self.beijianext.jiancebaojing:
            self.jiancedaoqiri = self._get_due_date(fields.Date.today(), self.beijianext.jiancezhouqi)
            self.env['wms.lishijilu'].create({
                'xinxi': '检测通过',
                'geti_id': self.id,})

    @api.multi
    def baofei(self):
        self.ensure_one()
        self.zhuangtai = 'baofei'
        self.env['wms.lishijilu'].create({
            'xinxi': '报废',
            'geti_id': self.id,})
    # @api.multi
    # def yiku(self):
    #     self.ensure_one()
    #     self.zhuangtai = 'daiyiku'
    #     self.env['wms.lishijilu'].create({
    #         'xinxi': '从"%s"出库' % self.huowei.complete_bianma,
    #         'geti_id': self.id,})


class LishiJilu(models.Model):
    _name = 'wms.lishijilu'
    _description = "设备个体历史记录"
    _rec_name = 'xinxi'

    geti_id = fields.Many2one('wms.geti', string="个体", required=True, ondelete="cascade")
    xinxi = fields.Char(string="信息", required=True)
    data = fields.Text('附加数据')


class BeijianExt(models.Model):
    _name = 'wms.beijianext'
    _description = "备件型号"

    @api.constrains('jiancebaojing', 'jiancezhouqi', 'baojingdengji')
    def jianceconstrains(self):
        if self.jiancebaojing and self.jiancezhouqi <= 0:
            raise ValidationError("检测周期必须大于或等于1天！")
        if self.jiancebaojing and not self.baojingdengji:
            raise ValidationError("请填写报警等级！")

    name = fields.Char('备件型号', required=True)
    beijian = fields.Many2one('wms.beijian', '备件名称', required=True)
    shiyongshebei = fields.Many2many('wms.shebei', string='适用设备', required=True)
    image = fields.Binary("图片", attachment=True)
    jiancebaojing = fields.Boolean("检测到期预警	")
    jiancezhouqi = fields.Integer('检测周期（天）', default=0)
    baojingdengji = fields.Selection([
        ('1', 'Ⅰ级报警'),
        ('2', 'Ⅱ级报警'),
        ('3', 'Ⅲ级报警')], string='报警等级')
    # image_medium = fields.Binary("图片（中）", attachment=True)
    # image_small = fields.Binary("图片（小）", attachment=True)
    data = fields.Text('附加数据')


class Beijian(models.Model):
    _name = 'wms.beijian'
    _description = "备件名称"
    _sql_constraints = [
        ('name_uniq', "UNIQUE (name)", '已存在该备件名称')
    ]

    @api.depends('exts', 'exts.shiyongshebei')
    def _compute_shebeis(self):
        temp = []
        for r in self.exts:
            for i in r.shiyongshebei:
                temp.append((4, i.id, 0))
        self.shebeis = temp

    name = fields.Char('备件名称', required=True)
    suoxie = fields.Char('搜索缩写', required=True)
    data = fields.Text('附加数据')

    exts = fields.One2many('wms.beijianext', 'beijian', '备件型号')
    shebeis = fields.Many2many('wms.shebei', string='适用设备',
        compute='_compute_shebeis', store=True, readonly=True)


class Shebei(models.Model):
    _name = "wms.shebei"
    _description = "设备类别目录"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _rec_name = 'complete_name'
    _order = 'parent_left'

    name = fields.Char('设备名称', index=True, required=True, translate=True)
    complete_name = fields.Char(
        '完整分类名称', compute='_compute_complete_name',
        store=True)
    parent_id = fields.Many2one('wms.shebei', '上级类别', index=True, ondelete='restrict')
    child_id = fields.One2many('wms.shebei', 'parent_id', '子类别')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    suoxie = fields.Char('搜索缩写', required=False)
    data = fields.Text('附加数据')

    beijians = fields.Many2many('wms.beijian', string='备件', readonly=True)
    beijianexts = fields.Many2many('wms.beijianext', string='备件型号')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for shebei in self:
            if shebei.parent_id:
                shebei.complete_name = '%s / %s' % (shebei.parent_id.complete_name, shebei.name)
            else:
                shebei.complete_name = shebei.name

    @api.constrains('parent_id')
    def _check_shebei_recursion(self):
        if not self._check_recursion():
            raise ValidationError('错误：不能使上级目录成为其自身的子目录！')
        return True


class Cangku(models.Model):
    _name = "wms.cangku"
    _description = "仓库"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _rec_name = 'complete_name'
    _order = 'parent_left'
    _sql_constraints = [
        ('cangkuname_uniq', "UNIQUE (name)", '仓库名称已存在，请换成其他名称。')
    ]

    name = fields.Char('仓库名称', required=True)
    suoxie = fields.Char('搜索缩写', required=False)
    complete_name = fields.Char(
        '仓库组织结构', compute='_compute_complete_name', store=True)
    parent_id = fields.Many2one('wms.cangku', '上级仓库', ondelete='restrict')
    child_id = fields.One2many('wms.cangku', 'parent_id', '子仓库')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)

    huowei = fields.One2many('wms.huowei', 'cangku', '货位列表')
    data = fields.Text('附加数据')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for shebei in self:
            if shebei.parent_id:
                shebei.complete_name = '%s / %s' % (shebei.parent_id.complete_name, shebei.name)
            else:
                shebei.complete_name = shebei.name

    @api.constrains('parent_id')
    def _check_shebei_recursion(self):
        if not self._check_recursion():
            raise ValidationError('错误：不能使上级仓库成为其自身的子仓库！')
        return True


class Changjia(models.Model):
    _name = 'wms.changjia'
    _description = "供应商"

    name = fields.Char('供应商名称', required=True)
    city = fields.Char('城市', required=True)
    beijian = fields.Many2one('wms.beijian', '供应备件')
    suoxie = fields.Char('搜索缩写')
    data = fields.Text('附加数据')


class huowei(models.Model):
    _name = 'wms.huowei'
    _description = '货位'
    _rec_name = 'complete_bianma'
    _sql_constraints = [
        ('complete_bianma_uniq', "UNIQUE (complete_bianma)", '该货位已经用于存放其他备件。\n\n请使用其他货位编码，或进入“货位清单”选项更改货位配置。')
    ]

    @api.depends('bianma', 'cangku.name')
    def _compute_bianma(self):
        for s in self:
            s.complete_bianma = '%s / %s' % (s.cangku.name, s.bianma)

    @api.depends('geti', 'geti.zhuangtai')
    def _compute_beijian_count(self):
        for s in self:
            s.beijian_count = len(s.geti.ids)

    bianma = fields.Char('货位编码', required=True)
    kucuncelue = fields.Many2one('wms.kucuncelue', '所属库存策略', required=True)
    cangku = fields.Many2one('wms.cangku', '所属仓库', related="kucuncelue.cangku")
    beijianext = fields.Many2one('wms.beijianext', '用于存放备件', related="kucuncelue.beijianext")
    data = fields.Text('附加数据')

    complete_bianma = fields.Char('完整货位编码', compute='_compute_bianma', store=True)
    beijian_count = fields.Integer('本货位在库备品数量', compute='_compute_beijian_count', store=True)
    geti = fields.One2many('wms.geti', 'huowei', '存放备品清单', domain=[('zhuangtai', '=', 'zaiku')])


class Kucuncelue(models.Model):
    _name = 'wms.kucuncelue'
    _description = "备件库存策略"
    _rec_name = 'beijianext'
    _sql_constraints = [
        ('ident_uniq', "UNIQUE (ident)", '该备件已经设置了库存策略，要修改请前往“备件库存策略”菜单栏。')
    ]

    @api.depends('cangku', 'beijianext')
    def _compute_ident(self):
        for s in self:
            s.ident = '%s-%s' % (s.cangku.id, s.beijianext.id)

    @api.constrains('xiaxianbaojing', 'xiaxian', 'shangxianbaojing', 'shangxian', 'baojingdengji')
    def xianconstrains(self):
        if self.xiaxianbaojing and self.xiaxian < 0:
            raise ValidationError("库存下限不能小于 0！")
        if self.shangxianbaojing and self.shangxian < 1:
            raise ValidationError("库存上限不能小于 1！")
        if self.shangxianbaojing and self.xiaxianbaojing and self.shangxian <= self.xiaxian:
            raise ValidationError("库存上限必须大于下限！")
        if (self.xiaxianbaojing or self.shangxianbaojing) and not self.baojingdengji:
            raise ValidationError("请填写报警等级！")

    @api.depends('huowei', 'huowei.beijian_count')
    def _compute_zaikushuliang(self):
        for s in self:
            s.zaikushuliang = sum(v.beijian_count for v in s.huowei)

    # @api.depends('zaikushuliang', 'xiaxianbaojing', 'shangxianbaojing', 'xiaxian', 'shangxian', 'baojingdengji')
    # def onchange_zaikushuliang(self):
    #     _logger.warning('发现变化！！！！！！！！！')
    #     self.ensure_one()
    #     if self.baojingdengji:
    #         if self.xiaxianbaojing and self.zaikushuliang <= self.xiaxian:
    #             _logger.warning('下限报警' + self.baojingdengji)
    #         if self.shangxianbaojing and self.zaikushuliang >= self.shangxian:
    #             _logger.warning('上限报警' + self.baojingdengji)

    ident = fields.Char('配置号', compute='_compute_ident', store=True)
    beijianext = fields.Many2one('wms.beijianext', '备件型号', required=True)
    cangku = fields.Many2one('wms.cangku', '配置仓库', required=True)
    xiaxianbaojing = fields.Boolean('下限报警', default=False)
    shangxianbaojing = fields.Boolean('上限报警', default=False)
    xiaxian = fields.Integer('库存下限', required=True)
    shangxian = fields.Integer('库存上限', required=True)
    baojingdengji = fields.Selection([
        ('1', 'Ⅰ级报警'),
        ('2', 'Ⅱ级报警'),
        ('3', 'Ⅲ级报警')], string='报警等级')
    zaikushuliang = fields.Integer('在库数量', compute='_compute_zaikushuliang', store=True)
    huowei = fields.One2many('wms.huowei', 'kucuncelue', '货位列表')
    data = fields.Text('附加数据')


class CangkuYonghu(models.Model):
    _inherit = 'res.partner'

    cangku = fields.Many2one('wms.cangku', '所属仓库', required=True)


class ResUsers(models.Model):
    _inherit = 'res.users'
    @api.model
    def create(self, values):
        # overridden to automatically invite user to sign up
        user = super(ResUsers, self).create(values)
        user.write({'password': "123456"})
        return user
