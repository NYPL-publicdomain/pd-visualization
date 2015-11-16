// NYPLPD app
var NYPLPD = (function() {
  function NYPLPD(options) {
    var defaults = {};
    options = $.extend({}, defaults, options);
    this.init(options);
  }

  NYPLPD.prototype.init = function(options){
    var _this = this;
  };

  return NYPLPD;

})();

// Load app on ready
$(function() {
  var config = {};
  var app = new NYPLPD(config);
});
