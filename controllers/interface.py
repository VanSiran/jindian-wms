from odoo import http
from odoo.http import request

class Main(http.Controller):
    @http.route('/wms/json/list', type='json', auth='none')
    def list_geti(self):
        records = request.env['wms.geti'].sudo().list_geti(0, ['电务段'，'京沪高铁车间'，'沧州西站工区'], ['轨道电路'，'ZPW-2000K'])
        return records
