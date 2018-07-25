// odoo.define('show_warn_field', function(require){
//   var registry = require('web.field_registry'),
//     FieldInteger = require('web.basic_fields').FieldInteger
//
//   var WarnField = FieldInteger.extend({
//     _onInput: function(){
//       this._super.apply(this, arguments)
//       console.log(this.$el.value)
//     }
//   });
//
//   console.log("oe_showwarn_field registry!")
//   registry.add('show_warn_field', WarnField)
//   return {
//     WarnField: WarnField,
//   }
// })




odoo.define('show_warn_field', function(require){
  var registry = require('web.field_registry'),
    InputField = require('web.basic_fields').InputField

  var Showwarn = InputField.extend({
      // className: 'o_field_integer o_field_number oe_showwarn_field',
      // tagName: 'span',
      // supportedFieldTypes: ['integer'],
      // isSet: function() {
      //     return this.value === 0 || this._super.apply(this, arguments);
      // },
      // _formatValue: function(value) {
      //     if (typeof value === 'string') {
      //         if (!/^[0-9]+-/.test(value)) {
      //             throw new Error('"' + value + '" is not an integer or a virtual id');
      //         }
      //         return value;
      //     }
      //     return this._super.apply(this, arguments);
      // },
      // events: _.extend({}, InputField.prototype.events, {
      //   'keyup': function(e){
      //     if(this.$el.value > 1){
      //       $('.duogeruku_warn').show()
      //     }else if(this.$el.value <= 1){
      //       $('.duogeruku_warn').hide()
      //     }
      //   },
      // }),
      _onInput: function(){
        console.log('123123')
        this._super.apply(this, arguments)
      }
  });

  console.log("oe_showwarn_field registry!")
  registry.add('show_warn_field', Showwarn)
  return {
    Showwarn: Showwarn,
  }
})
