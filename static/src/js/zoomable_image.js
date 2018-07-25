odoo.define('zoomable_image', function(require){
  var registry = require('web.field_registry'),
    FieldBinaryImage = require('web.basic_fields').FieldBinaryImage;

  var ZoomableImage = FieldBinaryImage.extend({
    start: function(){
      this.$el.zoomify()
      return this._super.apply(this, arguments)
    }
    // events: _.extend({}, FieldBinaryImage.prototype.events, {
    //       'click img': function() {
    //           $('img.myImage1').zoomify();
    //       },
    //   }),
  });

  registry.add('zoomable_image', ZoomableImage);
  return {
    ZoomableImage: ZoomableImage,
  }
})
