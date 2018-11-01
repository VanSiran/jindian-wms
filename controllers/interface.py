from odoo import http
from odoo.http import request

class Main(http.Controller):
    @http.route('/wms/json/list', type='json', auth='none', cors="*")
    def list(self, cangku, shebei):
        obj = request.env['wms.geti'].sudo()
        records = obj.list_geti(cangku, shebei)
        return records
        # example:
        #  curl -i -X POST -H "Content-Type:application/json" -d '{"params":{"cangku": ["\u7535\u52a1\u6bb5", "\u4eac\u6caa\u9ad8\u94c1\u8f66\u95f4", "\u6ca7\u5dde\u897f\u7ad9\u5de5\u533a"], "shebei": ["\u8f68\u9053\u7535\u8def", "ZPW-2000K"]}}' http://47.95.8.185/wms/json/list

    @http.route('/wms/json/chuku', type='json', auth='none', cors="*")
    def chuku(self, bianhao, yongtu, yonghu):
        obj = request.env['wms.geti'].sudo()
        records = obj.chuku(bianhao, yongtu, yonghu)
        return records

    # note: this method deprecated!
    def list_geti(self, cangku, shebei):
        # return [1,2,3,4,5,6]
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
