# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api, tools
import datetime, dateutil
from fuzzywuzzy import process
import logging
_logger = logging.getLogger(__name__)

class BJGeTi(models.Model):
    _name = 'wms.geti'
    _description = "备件个体"
    _rec_name = 'xuliehao'
    _sql_constraints = [
        ('xuliehao_uniq', "UNIQUE (xuliehao)", '个体编号必须是唯一的')
    ]

    xuliehao = fields.Char('编号', required=True, index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('wms.geti'))
    beijianext = fields.Many2one('wms.beijianext', "备件型号", required=True)
    huowei = fields.Many2one('wms.huowei', '货位', required=True)
    zhuangtai = fields.Selection([
        ('zaiku', '正常在库'),
        ('daijiance', '即将检测'),
        ('daibaofei', '即将报废'),
        ('jianceguoqi', '过期未检测'),
        ('baofeiguoqi', '过期未报废'),
        ('chuku', '已出库'),
        ('baofei', '已报废'),
        ('yiku', '移库中')], string="备件状态", compute='_compute_zhuangtai', store=True)
    zhuangtai_core = fields.Selection([
        ('jiashang', '架上'),
        ('chukuqu', '出库区'),
        ('baofeiqu', '报废区'),
        ('yikuqu', '移库区')], required=True)
    changjia = fields.Many2one('wms.changjia', '厂家')
    shengchanriqi = fields.Date('生产日期', required=True)
    shangcijiance = fields.Date('上次检测')
    pihao = fields.Char("批次号")
    data = fields.Text('附加数据')

    lishijilu = fields.One2many('wms.lishijilu', 'geti_id', string='历史记录')
    beijian = fields.Many2one(string='备件名称', related='beijianext.beijian')
    shiyongshebei = fields.Many2many(string='适用设备', related='beijianext.shiyongshebei')
    cangku = fields.Many2one(string='所属仓库', related='huowei.cangku', store=True)
    image = fields.Binary(string='图片', related='beijianext.image')
    jiancedaoqiri = fields.Date(string='检测到期日', compute='_compute_daoqiri', store=True)

    @api.depends('jiancedaoqiri', 'beijianext.jiancebaojing', 'zhuangtai_core')
    def _compute_zhuangtai(self):
        DATE_FORMAT = "%Y-%m-%d"
        for geti in self:
            # NOTE：cron job 只更新 架上 备件
            # 若今后对 出库区 备件也要进行状态更新，则需修改cron job
            if geti.zhuangtai_core == 'jiashang':
                geti.zhuangtai = 'zaiku'
                if geti.beijianext.jiancebaojing:
                    daoqiri = datetime.datetime.strptime(geti.jiancedaoqiri, DATE_FORMAT)
                    today = datetime.datetime.strptime(fields.Date.today(), DATE_FORMAT)
                    if daoqiri < today:
                        geti.zhuangtai = 'jianceguoqi'
                    elif daoqiri <= datetime.timedelta(days=30) + today:
                        geti.zhuangtai = 'daijiance'
            elif geti.zhuangtai_core == 'chukuqu':
                geti.zhuangtai = 'chuku'
            elif geti.zhuangtai_core == 'yikuqu':
                geti.zhuangtai = 'yiku'
            elif geti.zhuangtai_core == 'baofeiqu':
                geti.zhuangtai = 'baofei'

    @api.depends('shangcijiance', 'beijianext.jiancezhouqi', 'beijianext.jiancebaojing', 'shengchanriqi')
    def _compute_daoqiri(self):
        DATE_FORMAT = "%Y-%m-%d"
        for geti in self:
            if geti.beijianext.jiancebaojing:
                geti.jiancedaoqiri = (
                    datetime.datetime.strptime(geti.shangcijiance if geti.shangcijiance else geti.shengchanriqi, DATE_FORMAT) +
                    dateutil.relativedelta.relativedelta(months=geti.beijianext.jiancezhouqi)
                    ).strftime(DATE_FORMAT)
            else:
                geti.jiancedaoqiri = False

    @api.multi
    def jiance(self):
        self.ensure_one()
        # NOTE: 此处的状态判断要与geti视图中的按钮显示条件一致
        if self.zhuangtai not in ('jianceguoqi', 'daijiance'):
            raise ValidationError("备件无需检测，若界面未更新，请刷新网页。")
        # if self.beijianext.jiancebaojing:
        self.shangcijiance = fields.Date.today()
        self.env['wms.lishijilu'].create({
            'xinxi': '检测通过',
            'geti_id': self.id,})

    @api.multi
    def list_geti(self, cangku, shebei):
        # NOTE: 此处若顶层仓库不是“电务段”要更改！
        domain = []
        if isinstance(cangku, (list, tuple)):
            dcangku = ('cangku.complete_name', '=', ' / '.join(str(x).strip() for x in cangku if x))
            #duan = '电务段'
        elif isinstance(cangku, str):
            dcangku = ('cangku.name', '=', cangku.strip())
        else:
            return {
                "message": "仓库参数必须是数组或字符串",
                "data": [],
                "success": False
            }
        dtcangku = tuple([dcangku[0].replace('cangku.', ''), *dcangku[1:]])
        if self.env['wms.cangku'].search_count([dtcangku]) == 0:
            return {
                "message": "找不到仓库 %s" % dtcangku[2],
                "data": [],
                "success": False
            }
        domain.append(dcangku)
        if isinstance(shebei, (list, tuple)):
            shebeiname = ' / '.join(str(x).strip() for x in shebei if x)
            shebeiobj = self.env['wms.shebei'].search([('complete_name','=',shebeiname)], limit=1)
            if len(shebeiobj) == 1:
                domain.append(('beijianext','in',[obj.id for obj in shebeiobj.beijianexts]))
            else:
                return {
                    "message": "找不到设备 %s" % shebeiname,
                    "data": [],
                    "success": False
                }
            #domain.append(('beijianext.shiyongshebei.complete_name', '=', ' / '.join(str(x) for x in cangku)))
        # elif isinstance(shebei, str):
        #     return "Error: 未找到设备 %s" % shebeiname
        else:
            return {
                "message": "设备参数必须是数组",
                "data": [],
                "success": False
            }
        # NOTE: 返回可用备件
        domain.append(('zhuangtai','in',('zaiku', 'daijiance', 'daibaofei')))
        objs = self.search(domain)
        ztdic = {'zaiku': '在库', 'daijiance': '待检测', 'daibaofei': '待报废'}
        return {
            "success": True,
            "message": "查询到 %d 个备件" % len(objs),
            "data": [
            {'beijianmingcheng': obj.beijian.name if obj.beijian.name else "",
             'beijianxinghao': obj.beijianext.name if obj.beijianext.name else "",
             'huowei': obj.huowei.complete_bianma if obj.huowei.complete_bianma else "",
             'bianhao': obj.xuliehao if obj.xuliehao else "",
             'zhuangtai': ztdic[obj.zhuangtai],
             'changjia': obj.changjia.name if obj.changjia.name else "",
             'shiyongshebei': ", ".join(x.complete_name for x in obj.shiyongshebei) if obj.shiyongshebei else "",
             'pihao': obj.pihao if obj.pihao else "",
             'shengchanriqi': obj.shengchanriqi if obj.shengchanriqi else ""}
              for obj in objs]}

    @api.multi
    def chuku(self, bianhao, yongtu, yonghu):
        if isinstance(bianhao, str):
            domain = [('xuliehao', '=', bianhao.strip())]
            bianhao = [bianhao,]
        elif isinstance(bianhao, (list, tuple)):
            domain = [('xuliehao', 'in', [x.strip() for x in bianhao])]
        else:
            return {
                "message": "编号参数必须是字符串或数组",
                "data": [],
                "success": False
            }
        objs = self.search(domain)
        state_fail_arr = []
        success_arr = []
        for obj in objs:
            if obj.zhuangtai not in ('zaiku', 'daibaofei', 'daijiance'):
                state_fail_arr.append(obj.xuliehao)
                continue
            success_arr.append(obj.xuliehao)
        notfound_arr = list(set(bianhao) - set(state_fail_arr) - set(success_arr))
        if notfound_arr or state_fail_arr:
            return {
                "message": "".join(["%s未找到; " % nf for nf in notfound_arr] + ["%s已出库或不允许出库; " % sf for sf in state_fail_arr]),
                "data": [],
                "success": False
            }
        for obj in objs:
            obj.zhuangtai_core = 'chukuqu'
            self.env['wms.lishijilu'].create({
                'xinxi': '从"%s"出库,用于"%s" %s' % (obj.huowei.complete_bianma, yongtu, "(办理人: %s)" % yonghu),
                'geti_id': obj.id,})
        return {
            "message": "%d 个备件出库成功" % len(objs),
            "data": [],
            "success": True
        }
        # fail_arr = []
        success_arr = []
        for obj in objs:
            # NOTE: 此处的状态判断要与geti视图中的按钮显示条件一致
            if obj.zhuangtai not in ('zaiku', 'daibaofei', 'daijiance'):
                # fail_arr.append({
                #     "message": "备件状态不允许出库。",
                #     "data": obj.xuliehao,
                # })
                # fail_arr.append(obj.xuliehao)
                continue
            obj.zhuangtai_core = 'chukuqu'
            # user = self.env['res.users'].search([('name','=',yonghu)], limit=1)
            self.env['wms.lishijilu'].create({
                'xinxi': '从"%s"出库,用于"%s" %s' % (obj.huowei.complete_bianma, yongtu, "(办理人: %s)" % yonghu),
                'geti_id': obj.id,})
                #'create_uid': user.id if user else False})
            # success_arr.append({
            #     "message": "成功",
            #     "data": obj.xuliehao,
            # })
            success_arr.append(obj.xuliehao)
            # return {
            #     "message": "%s 出库成功。" % obj.xuliehao,
            #     "data": [],
            #     "success": True
            # }
            # hist = {
            #     'xinxi': '从"%s"出库,用于"%s" %s' % (obj.huowei.complete_bianma, self.yongtu, "(办理人: %s)" % yonghu if not user else ''),
            #     'geti_id': geti.id,}
            # if user:
            #     hist['create_uid'] = user.id
            # self.env['wms.lishijilu'].create()
        fail_arr = list(set(bianhao) - set(success_arr))
        return {
            "message": "%s 个成功，%s 个失败" % (len(success_arr), len(fail_arr)),
            "data": {"success": success_arr, "fail": fail_arr},
            "success": True
        }


class DaiYiku(models.Model):
    _name = 'wms.daiyiku'
    _description = '待移库记录'

    geti_id = fields.Many2one('wms.geti', string="个体", required=True, ondelete="cascade")
    # beijian = fields.Many2one('wms.beijian', string="备件名称", related="geti_id.beijian")
    # beijianext = fields.Many2one('wms.beijianext', string="备件型号", related="geti_id.beijianext")
    yuancangku = fields.Many2one('wms.cangku', string="原始仓库", related="geti_id.cangku")
    mudicangku = fields.Many2one('wms.cangku', string="目的仓库", required=True)

    # @api.multi
    # def querenshouhuo(self):
    #     if self.env['wms.kucuncelue'].search_count([
    #         ('beijianext', '=', self.beijianext.id),
    #         ('cangku', '=', self.cangku.id)]) == 0:
    #         return {
    #             'name': '为此备件设置库存报警',
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'wms.wizard.setkucuncelue',
    #             'views': [[
    #                 self.env.ref('wms.setkucuncelue_wizard_view').id, 'form']],
    #             'target': 'new',
    #             'context': {
    #                 'cangku': self.cangku.id,
    #                 'beijianext': self.beijianext.id,
    #                 'object': self.id,}}
    #     if self.env['wms.huowei'].search_count([
    #         ('beijianext', '=', self.beijianext.id),
    #         ('cangku', '=', self.cangku.id)]) == 0:
    #         return {
    #             'name': '为此备件分配货位',
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'wms.wizard.newhuowei',
    #             'views': [[self.env.ref('wms.newhuowei_wizard_view').id, 'form']],
    #             'target': 'new',
    #             'context': {
    #                 'cangku': self.cangku.id,
    #                 'beijianext': self.beijianext.id,
    #                 'object': self.id,}}
    #     return {
    #         'name': '将此备件存储到哪个货位',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'wms.wizard.yikuqueren',
    #         'views': [[self.env.ref('wms.newhuowei_wizard_view').id, 'form']],
    #         'target': 'new',
    #         'context': {
    #             'cangku': self.cangku.id,
    #             'beijianext': self.beijianext.id,
    #             'object': self.id,}}

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

    @api.constrains('jiancebaojing', 'jiancezhouqi')
    def jianceconstrains(self):
        if self.jiancebaojing and self.jiancezhouqi <= 0:
            raise ValidationError("检测周期必须大于或等于1个月！")

    name = fields.Char('备件型号', required=True)
    beijian = fields.Many2one('wms.beijian', '备件名称', required=True)
    shiyongshebei = fields.Many2many('wms.shebei', string='适用设备', required=True)
    image = fields.Binary("图片", attachment=True)
    jiancebaojing = fields.Boolean("检测预警开关")
    jiancezhouqi = fields.Integer('检测周期（月）', default=0)
    # image_medium = fields.Binary("图片（中）", attachment=True)
    # image_small = fields.Binary("图片（小）", attachment=True)
    data = fields.Text('附加数据')

    @api.multi
    def find_similar(self, dest):
        # fuzz.partial_ratio
        names = self.search([]).mapped(lambda r: {"id": r.id, "beijianext": r.name, "beijian": r.beijian.name})
        # names = self.search([]).mapped(lambda r: (r.id, r.name, r.beijian.name))
        # _logger.info(names)
        return process.extractBests({"beijianext": dest}, names, processor=lambda x: x["beijianext"], score_cutoff=60)


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


class CangkuSqlView(models.Model):
    _name = 'wms.cangku.mirror'
    _description = '仓库镜像'
    _auto = False

    name = fields.Char('仓库名称', required=True)
    suoxie = fields.Char('搜索缩写', required=False)
    # complete_name = fields.Char(
    #     '仓库组织结构', compute='_compute_complete_name', store=True)
    parent_id = fields.Many2one('wms.cangku', '上级仓库', ondelete='restrict')
    # child_id = fields.One2many('wms.cangku', 'parent_id', '子仓库')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = '''
        CREATE OR REPLACE VIEW wms_cangku_mirror AS (
        SELECT id, name, parent_id, parent_left, parent_right, suoxie
        FROM wms_cangku)'''
        self.env.cr.execute(query)


class Changjia(models.Model):
    _name = 'wms.changjia'
    _description = "供应商"

    name = fields.Char('供应商名称', required=True)
    city = fields.Char('城市', required=True)
    beijian = fields.Many2one('wms.beijian', '供应备件')
    suoxie = fields.Char('搜索缩写')
    data = fields.Text('附加数据')


class Huowei(models.Model):
    _name = 'wms.huowei'
    _description = '货位'
    _rec_name = 'complete_bianma'
    _sql_constraints = [
        ('complete_bianma_uniq', "UNIQUE (complete_bianma)", '该货位已经用于存放其他备件。\n\n请使用其他货位编码，或通过“备件库存策略”页面分配货位。')
    ]

    @api.depends('bianma', 'cangku.name')
    def _compute_bianma(self):
        for s in self:
            s.complete_bianma = '%s / %s' % (s.cangku.name, s.bianma)

    @api.depends('geti','geti.zhuangtai')
    def _compute_getishu(self):
        for s in self:
            s.keyonggetishu = s.geti.search_count([('huowei', '=', s.id), ('zhuangtai', 'in', ('zaiku', 'daibaofei', 'daijiance'))])
            s.bukeyonggetishu = s.geti.search_count([('huowei', '=', s.id), ('zhuangtai', 'in', ('jianceguoqi', 'baofeiguoqi'))])

    bianma = fields.Char('货位编码', required=True)
    kucuncelue = fields.Many2one('wms.kucuncelue', '所属库存策略', required=True)
    cangku = fields.Many2one('wms.cangku', '所属仓库', related="kucuncelue.cangku", store=True)
    beijianext = fields.Many2one('wms.beijianext', '用于存放备件', related="kucuncelue.beijianext")

    complete_bianma = fields.Char('完整货位编码', compute='_compute_bianma', store=True)
    keyonggetishu = fields.Integer('本货位可用备品数量', compute='_compute_getishu', store=True)
    bukeyonggetishu = fields.Integer('本货位不可用备品数量', compute='_compute_getishu', store=True)
    geti = fields.One2many('wms.geti', 'huowei', '架上备品', domain=[('zhuangtai_core', '=', 'jiashang')])


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

    # @api.constrains('xiaxianbaojing', 'xiaxian', 'shangxianbaojing', 'shangxian', 'baojingdengji')
    @api.constrains('xiaxianbaojing', 'xiaxian', 'shangxianbaojing', 'shangxian')
    def xianconstrains(self):
        if self.xiaxianbaojing and self.xiaxian < 0:
            raise ValidationError("库存下限不能小于 0！")
        if self.shangxianbaojing and self.shangxian < 1:
            raise ValidationError("库存上限不能小于 1！")
        if self.shangxianbaojing and self.xiaxianbaojing and self.shangxian <= self.xiaxian:
            raise ValidationError("库存上限必须大于下限！")
        # if (self.xiaxianbaojing or self.shangxianbaojing) and not self.baojingdengji:
        #     raise ValidationError("请填写报警等级！")

    @api.depends('huowei', 'huowei.keyonggetishu')
    def _compute_keyongshuliang(self):
        for s in self:
            s.keyongshuliang = sum(v.keyonggetishu for v in s.huowei)

    @api.depends('huowei', 'huowei.bukeyonggetishu')
    def _compute_bukeyongshuliang(self):
        for s in self:
            s.bukeyongshuliang = sum(v.bukeyonggetishu for v in s.huowei)

    @api.depends('huowei')
    def _compute_huoweigeshu(self):
        for s in self:
            s.huoweigeshu = len(s.huowei)

    ident = fields.Char('配置号', compute='_compute_ident', store=True)
    beijianext = fields.Many2one('wms.beijianext', '备件型号', required=True)
    cangku = fields.Many2one('wms.cangku', '配置仓库', required=True)
    xiaxianbaojing = fields.Boolean('下限报警', default=False)
    shangxianbaojing = fields.Boolean('上限报警', default=False)
    xiaxian = fields.Integer('库存下限', required=True)
    shangxian = fields.Integer('库存上限', required=True)
    # baojingdengji = fields.Selection([
    #     ('1', 'Ⅰ级报警'),
    #     ('2', 'Ⅱ级报警'),
    #     ('3', 'Ⅲ级报警')], string='报警等级')
    huowei = fields.One2many('wms.huowei', 'kucuncelue', '货位列表')
    keyongshuliang = fields.Integer('在库可用数量', compute='_compute_keyongshuliang', store=True)
    bukeyongshuliang = fields.Integer('在库不可用数量', compute='_compute_bukeyongshuliang', store=True)
    huoweigeshu = fields.Integer('货位个数', compute='_compute_huoweigeshu', store=True)
    data = fields.Text('附加数据')


class CangkuYonghu(models.Model):
    _inherit = 'res.partner'

    cangku = fields.Many2one('wms.cangku', '所属仓库', required=True)


class ResUsers(models.Model):
    _inherit = 'res.users'
    @api.model
    def create(self, values):
        user = super(ResUsers, self).create(values)
        user.write({'password': "123456"})
        return user
