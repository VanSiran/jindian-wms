odoo.define('tree_selection', function(require){
  var registry = require('web.field_registry'),
    AbstractField = require('web.AbstractField');

  var TreeSelection = AbstractField.extend({
    supportedFieldTypes: ['many2one'],
    _field_value: -1,

    start: function(){
      var self = this
      this._super.apply(this, arguments)
      return this._rpc({
          model: self.field.relation,
          method: "search_read",
          kwargs: {
              fields: ["name","parent_id","id","sousuo"],
          }
      }).done(function(result) {
        result = _.map(result, function(r){
          r.parent = r.parent_id ? r.parent_id[0] : '#'
          r.text = r.name
          delete r.parent_id
          delete r.name
          return r
        })
        self.$el.jstree({ 'core' : {
            'data' : result,
            'multiple': false,
        }})
        self.$el.on('ready.jstree', function(){
          if(self.value !== false){
            self._field_value = self.value.data.id
            self.$el.jstree(true).select_node(self._field_value, true)
          }
          self.$el.on('select_node.jstree', function(e, data){
            if (data.selected[0] !== self._field_value){
              self._field_value = data.selected[0]
              self._setValue(data.selected[0])
            }
          })
        })
      })
    },
  });

  registry.add('tree_selection_field', TreeSelection);
  return {
    TreeSelection: TreeSelection,
  }
})
