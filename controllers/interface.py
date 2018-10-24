from odoo import http
from odoo.http import request

class Main(http.Controller):
    @http.route('/wms/json/list', type='json', auth='none')
    def list(self):
        # records = [1,2,3]
        # obj = request.env['wms.geti'].sudo()
        records = self.list_geti(['电务段'，'京沪高铁车间'，'沧州西站工区'], ['轨道电路'，'ZPW-2000K'])
        return records

    def list_geti(cangku, shebei):
        # NOTE: 此处若顶层仓库不是“电务段”要更改！
        domain = []
        if isinstance(cangku, (list, tuple)):
            dcangku = ('cangku.complete_name', '=', ' / '.join(str(x).strip() for x in cangku if x))
            #duan = '电务段'
        elif isinstance(cangku, str):
            dcangku = ('cangku.name', '=', cangku.strip())
        else:
            return "Error: 'cangku' 必须是数组、字符串"
        dtcangku = tuple([dcangku[0].replace('cangku.', ''), *dcangku[1:]])
        if request.env['wms.cangku'].search_count([dtcangku]) == 0:
            return "Error: 未找到仓库 %s" % dtcangku[2]
        domain.append(dcangku)
        if isinstance(shebei, (list, tuple)):
            shebeiname = ' / '.join(str(x).strip() for x in shebei if x)
            shebeiobj = request.env['wms.shebei'].search([('complete_name','=',shebeiname)], limit=1)
            if len(shebeiobj) == 1:
                domain.append(('beijianext','in',[obj.id for obj in shebeiobj.beijianexts]))
            else:
                return "Error: 未找到设备 %s" % shebeiname
            #domain.append(('beijianext.shiyongshebei.complete_name', '=', ' / '.join(str(x) for x in cangku)))
        # elif isinstance(shebei, str):
        #     return "Error: 未找到设备 %s" % shebeiname
        else:
            return "Error: 'shebei' 必须是数组"
        # NOTE: 返回可用备件
        domain.append(('zhuangtai','in',('zaiku', 'daijiance', 'daibaofei')))
        objs = request.env['wms.geti'].search(domain)
        return [
            {'beijianmingcheng': obj.beijian.name,
             'beijianxinghao': obj.beijianext.name,
             'huowei': obj.huowei.complete_bianma,
             'bianhao': obj.xuliehao,
             'zhuangtai': obj.zhuangtai,
             'changjia': obj.changjia.name,
             'shiyongshebei': [x.complete_name for x in obj.shiyongshebei],
             'pihao': obj.pihao,
             'shengchanriqi': obj.shengchanriqi}
              for obj in objs]
