odoo.define('filter_search_client_action', function(require){
  var core = require('web.core')
    // SearchView = require('web.SearchView'),
    Widget = require('web.Widget'),
    dialog = require('web.view_dialogs')

  var FilterSearch = Widget.extend({
    start: function(){
      this._super.apply(this, arguments)
      var self = this
      new dialog.SelectCreateDialog(this, {
          no_create: true,
          quick_create: true,
          res_model: "wms.geti",
          domain: [],
          context: {},
          title: "筛选查询",
          initial_ids: undefined,
          initial_view: "search",
          disable_multiple_selection: true,
          on_selected: function(records) {
              // self.reinitialize(records[0]);
              // self.activate();
              console.log(records)
              new dialog.FormViewDialog(self, {
                res_model: "wms.geti",
                res_id: records[0].id,
                title: "备件信息",
              }).open()
          }
      }).open();
    }
    // className: 'oe_enter_to_submit_field',
    // events: _.extend({}, FieldChar.prototype.events, {
    //   'keyup': function(e){if(e.key=='Enter'){
    //     $('.enter_to_submit_button').click()
    //   }},
    //   'click': function(){
    //     this.$input.select()
    //   }
    // }),
  });

  core.action_registry.add('wms.filter_search_client_action', FilterSearch)
  // registry.add('filter_search_client_action', FilterSearch);
  return {
    FilterSearch: FilterSearch,
  }
})
