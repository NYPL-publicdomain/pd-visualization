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
    this.coords_loaded = $.Deferred();

    $.when(this.images_loaded, this.data_loaded, this.labels_loaded, this.coords_loaded).done(function() {
      $('.info-button').removeClass('loading');
      _this.loadUI();
      _this.loadListeners();
    });

    this.loadImages();
    this.loadData();
    this.loadLabels();
    this.loadCoords();
  };

  NYPLPD.prototype.groupBy = function(groupId){
    if ($('.nav-tab.active').attr('data-group')==groupId) return;

    $('[data-group]').removeClass('active');
    $('[data-group="'+groupId+'"]').addClass('active');

    this.stickyMarker();
    this.updateMapWindow();
  };

  NYPLPD.prototype.isLargeScreen = function(){
    return $('#large-breakpoint').css('display') == 'block';
  };

  NYPLPD.prototype.loadCoords = function(){
    var _this = this;

    this.coords = {};

    $.getJSON("js/coords.json", function(data) {
      _this.coords = data;
      console.log('All coords loaded');
      _this.coords_loaded.resolve();
    });
  };

  NYPLPD.prototype.loadData = function(){
    var _this = this,
      groups = this.opt.item_data_groups;

    this.item_groups = [];
    this.items = [];
    this.activeItem = false;
    this.groups_loaded = 0;

    // init groups
    for(var i=0; i<groups; i++) {
      this.item_groups.push([]);
    }

    // get data for each group
    for(var i=0; i<groups; i++) {
      $.getJSON("js/items/items_"+i+"_"+groups+".json", function(data) {
        var items = data.items,
            page = data.page;
        _this.item_groups[page] = items;

        // Track group loaded
        _this.groups_loaded++;

        // Check if all data is loaded
        if (_this.groups_loaded >= groups) {
          // merge all the groups into one
          for(var j=0; j<groups; j++) {
            _this.items = _this.items.concat(_this.item_groups[j]);
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
      if ($('#loading-button').hasClass('loading')) return false;
      $('.info').toggleClass('active');
    });

    $('#nav-tabs').on('click', '.nav-tab', function(e){
      e.preventDefault();
      _this.groupBy($(this).attr('data-group'));
    });

    $('#viz-images').on('mousemove', function(e){
      _this.showItemInfoByEvent(e);
    });

    $('#viz-images').on('mouseout', function(e){
      $('#item-info-box').removeClass('active');
    });

    $('#viz-images').on('click', function(e){
      e.preventDefault();
      _this.openItemByEvent(e);
    });

    $('#map-window').draggable({
      containment: 'parent',
      axis: 'y',
      drag: function(e, ui) {
        _this.onMapWindowDrag(e, ui);
      }
    });

    $(window).on('scroll', function(){
      _this.stickyMarker();
      _this.updateMapWindow();
    });

    $(window).on('resize', function(){
      _this.stickyMarker();
      _this.updateMapWindow();
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
        var $marker,
            markerClass = 'marker-' + marker.value,
            markerLabel = marker.label + ' ('+marker.count+')';
        if (marker.count <= 300) markerClass += ' short';
        if (marker.url && marker.url.length) {
          $marker = $('<div class="marker '+markerClass+'"><div class="marker-inner"><a href="'+marker.url+'" target="_blank" title="'+markerLabel+'">'+markerLabel+'</a></div></div>');
        } else {
          $marker = $('<div class="marker '+markerClass+'"><div class="marker-inner"><span title="'+markerLabel+'">'+markerLabel+'</span></div></div>');
        }
        $marker.css({
          height: marker.h
        });
        $marker.find('.marker-inner').css({
          height: marker.h
        }).hoverIntent(function(){
          $marker.addClass('active');
        }, function(){
          $marker.removeClass('active');
        });
        $markers.append($marker);
      });
      $('#viz-markers').append($markers);
    });

    this.stickyMarker();
    this.updateMapWindow();
  };

  NYPLPD.prototype.onMapWindowDrag = function(evt, ui){
    var elTop = ui.position.top,
        windowHeight = $(window).height(),
        imageHeight = $('.viz-image.active').height(),
        percentTop = elTop / windowHeight,
        top = imageHeight * percentTop;

    $(window).scrollTop(top);
  };

  NYPLPD.prototype.openItemByEvent = function(evt){
    var item = this.getItemByEvent(evt);

    if (item) {
      window.open("http://digitalcollections.nypl.org/items/" + item.uuid);
    }
  };

  NYPLPD.prototype.showItem = function(item){
    var uuid = item.uuid,
        title = item.title,
        captureId = item.captureId,
        x = item.x,
        y = item.y;

    // already active
    if (this.activeItem === uuid) return;
    this.activeItem = uuid;

    var $item = $('#item-info-box'),
        $content = $('<div><img src="http://images.nypl.org/index.php?id='+captureId+'&t=t" /><h5>'+title+'</h5></div>')

    // reset item el
    $item.empty();
    $item.css({
      top: y,
      left: x
    });
    $item.html($content);
    $item.addClass('active');
  };

  NYPLPD.prototype.getItemByEvent = function(evt){
    var $parent = $('#viz-images'),

        // get mouse x/y relative to parent element
        x = evt.pageX - $parent.offset().left,
        y = evt.pageY - $parent.offset().top,

        // init options
        item_w = this.opt.item_w,
        item_h = this.opt.item_h,
        items_per_row = this.opt.items_per_row,

        // get current active group
        group_name = $('.nav-tab.active').first().attr('data-group'),
        coords = this.coords[group_name],

        // determine item row/col
        item_col = Math.floor(x / item_w),
        item_row = Math.floor(y / item_h),

        // init item data
        item_index = -1,
        item = false;

    // attempt to retrieve item info
    item_index = coords[item_row*items_per_row + item_col];
    if (item_index >= 0 && item_index < this.items.length){
      var _item = this.items[item_index];
      item = {
        uuid: _item[0],
        title: _item[1],
        captureId: _item[2],
        x: (item_col + 1) * item_w,
        y: item_row * item_h
      }
    }

    return item;
  };

  NYPLPD.prototype.showItemInfoByEvent = function(evt){
    var item = this.getItemByEvent(evt);
    if (item) {
      this.showItem(item);
    } else {
      $('#item-info-box').removeClass('active');
    }
  };

  NYPLPD.prototype.stickyMarker = function(){
    var $sticky = $('#sticky-content'),
        scrollTop = $(window).scrollTop(),
        padding = 28,
        windowHeight = $(window).height(),
        $markers = $('.markers.active').first().find('.marker'),
        stickyActive = false;

    $markers.each(function(){
      var markerScrollTop = $(this).offset().top,
          markerHeight = $(this).height();

      if (markerScrollTop+padding < scrollTop && (markerScrollTop+markerHeight) > (scrollTop+windowHeight/4)) {
        var $content = $(this).find('.marker-inner').html();
        $sticky.html($content);
        stickyActive = true;
        return false;
      }
    });

    if (stickyActive) {
      $sticky.addClass('active');
    } else {
      $sticky.empty().removeClass('active');
    }
  };

  NYPLPD.prototype.updateMapWindow = function(){
    // update height
    var $mapWindow = $('#map-window'),
        windowHeight = $(window).height(),
        imageHeight = $('.viz-image.active').height(),
        percentHeight = windowHeight / imageHeight * 100;

    $mapWindow.height(percentHeight + '%');

    // update top
    var scrollTop = $(window).scrollTop(),
        percentTop = scrollTop / imageHeight * 100;

    $mapWindow.css('top', percentTop + '%');
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
