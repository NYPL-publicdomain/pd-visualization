// NYPLPD app
var NYPLPD = (function() {
  function NYPLPD(options) {
    var defaults = {};
    options = $.extend({}, defaults, options);
    this.init(options);
  }

  NYPLPD.prototype.init = function(options){
    var _this = this;

    this.opt = options;
    this.images_loaded = $.Deferred();
    this.data_loaded = $.Deferred();
    this.labels_loaded = $.Deferred();

    $.when(this.images_loaded, this.data_loaded, this.labels_loaded).done(function() {
      _this.loadUI();
      _this.loadListeners();
    });

    this.loadImages();
    this.loadData();
    this.loadLabels();
  };

  NYPLPD.prototype.groupBy = function(groupId){
    $('[data-group]').removeClass('active');
    $('[data-group="'+groupId+'"]').removeClass('active');
  };

  NYPLPD.prototype.loadData = function(){
    var groups = this.opt.item_data_groups;
    var item_groups = [];

    this.items = []
    this.groups_loaded = 0;

    // init groups
    for(var i=0; i<groups; i++) {
      item_groups.push([]);
    }

    // get data for each group
    for(var i=0; i<groups; i++) {
      $.getJSON("js/items/"+i+"_"+groups+".json", function(data) {
        item_groups[i] = data;

        // Track group loaded
        _this.groups_loaded++;

        // Check if all data is loaded
        if (_this.groups_loaded >= groups) {
          // merge all the groups into one
          for(var j=0; j<groups; j++) {
            _this.items.concat(item_groups[j]);
          }
          // all data is loaded
          console.log('All data loaded');
          _this.data_loaded.resolve();
        }
      });
    }

  };

  NYPLPD.prototype.loadImages = function(){
    var _this = this;

    $('#viz-images').imagesLoaded()
      .always(function(instance){
        console.log('All images loaded');
        _this.images_loaded.resolve();
      });
  };

  NYPLPD.prototype.loadLabels = function(){
    var _this = this;

    this.labels = [];

    $.getJSON("js/labels.json", function(data) {
      _this.labels = data;
      console.log('All labels loaded');
      _this.labels_loaded.resolve();
    });
  };

  NYPLPD.prototype.loadListeners = function(){
    var _this = this;

    $('.info-button').on('click', function(e){
      e.preventDefault();
      $('.info').toggeClass('active');
    });

    $('.nav-tabs').on('click', '.nav-tab', function(e){
      e.preventDefault();
      _this.groupBy($(this).attr('data-group'));
    });

  };

  NYPLPD.prototype.loadUI = function(){

    // load labels
    $.each(this.labels, function(i, label){
      // add tab
      var $tab = $('<a data-group="'+label.id+'" class="nav-tab nav-item">'+label.label+'</a>');
      if (i<=0) $tab.addClass("active");
      $('#nav-tabs').append($tab);

      // add markers
      var $markers = $('<div data-group="'+label.id+'" class="markers"></div>');
      if (i<=0) $markers.addClass("active");
      $.each(label.markers, function(j, marker){
        var $marker;
        if (marker.url && marker.url.length) {
          $marker = $('<div class="marker marker-'+marker.value+'"><a href="'+marker.url+'" target="_blank">'+marker.label+'</a></div>');
        } else {
          $marker = $('<div class="marker marker-'+marker.value+'"><span>'+marker.label+'</span></div>');
        }
        $marker.css({
          height: marker.h
        });
        $markers.append($marker);
      });
      $('#viz-markers').append($markers);
    });
  };

  return NYPLPD;

})();

// Load app on ready
$(function() {
  var config = {
    item_data_groups: 5,
    item_w: 10,
    item_h: 10,
    items_per_row: 100
  };
  var app = new NYPLPD(config);
});
