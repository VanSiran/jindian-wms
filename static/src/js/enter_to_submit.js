odoo.define('enter_to_submit', function(require){
  var registry = require('web.field_registry'),
    FieldChar = require('web.basic_fields').FieldChar

  var EnterToSubmit = FieldChar.extend({
    className: 'oe_enter_to_submit_field',

    // init: function(){
    //   this._super.apply(this, arguments)
    // },
    events: _.extend({}, FieldChar.prototype.events, {
      'keyup': function(e){if(e.key=='Enter'){
        var error_dialog = $('div.o_dialog_warning.modal-body')
        if (error_dialog.length > 0) {
          error_dialog.first().siblings('div.modal-footer').children('button').click()
          this.$input.focus()
        } else {
          $('.enter_to_submit_button').click()
        }
      }},
      'click': function(){
        if (this.$input.hasClass('jq_clickselect')) {
          this.$input.select()
        }
      }
    }),
  });

  registry.add('enter_to_submit_field', EnterToSubmit);
  return {
    EnterToSubmit: EnterToSubmit,
  }
})
