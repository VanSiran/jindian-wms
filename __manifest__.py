# -*- coding: utf-8 -*-
{
    'name': "1.wms",

    'summary': "天津电务段仓库管理系统",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jia Qi",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/templates.xml',
        'views/web_customize.xml',

        'data/res.company.csv',
        'data/ir.sequence.csv',
        'data/wms.cangku.csv',
        'data/wms.shebei.csv',
        'data/wms.beijian.csv',
        'data/wms.beijianext.csv',

        'views/dashboard.xml',
        'views/jiancebaojing_sqlview.xml',
        'views/kucunbaojing_sqlview.xml',
        'views/cangku.xml',
        'views/new_huowei_wizard.xml',
        'views/beijian.xml',
        'views/changjia.xml',
        'views/yiku_wizard.xml',
        'views/chuku_wizard.xml',
        'views/huiku_wizard.xml',
        'views/geti.xml',
        'views/huowei.xml',
        'views/kucuncelue.xml',
        'views/lishijilu.xml',
        'views/shebei.xml',
        'views/saomiao_wizard.xml',
        'views/set_kucuncelue_wizard.xml',
        'views/ruku_queren_wizard.xml',
        'views/ruku_wizard.xml',
        'views/filter_search.xml',
        'views/cangkuyonghu.xml',
        'views/daiyiku.xml',

        'data/wms.view.dashboard.csv',

        'views/menu_items.xml',

        'data/res.groups.csv',
        'data/ir.rule.csv',
        'data/ir.model.access.csv',
        'data/ir.cron.csv',
        'data/res.users.csv',
    ],

    # 'qweb': [
    #     'static/src/xml/base.xml',
    # ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],

    'application': True,
    'auto_install': True,
}
