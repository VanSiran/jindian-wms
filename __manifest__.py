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
        'data/ir.cron.csv',
        'data/ir.sequence.csv',
        'data/wms.cangku.csv',
        'data/wms.shebei.csv',
        'data/wms.beijian.csv',
        'data/wms.beijianext.csv',

        # 'security/ir.rule.xml',
        # 'security/ir.model.access.csv',

        # 'views/user_mod.xml',
        'views/dashboard.xml',
        'views/cangku.xml',
        'views/huowei.xml',
        'views/kucuncelue.xml',
        'views/beijian.xml',
        'views/changjia.xml',
        'views/geti.xml',
        'views/lishijilu.xml',
        'views/shebei.xml',
        'views/saomiao_wizard.xml',
        'views/new_huowei_wizard.xml',
        'views/set_kucuncelue_wizard.xml',
        'views/ruku_queren_wizard.xml',
        'views/ruku_wizard.xml',
        'views/filter_search.xml',

        'data/wms.view.dashboard.csv',

        'views/menu_items.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],

    'application': True,
    'auto_install': True,
}
