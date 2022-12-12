L.Control.ScaleSlider = L.Control.extend({
	options: {
		position: 'bottomleft',
		scales: [],
		wmsScales: [],
		defaultScale: ''
	},
	
	initialize: function (layers, options) {
		L.setOptions(this, options);

		this._layers = layers;

		this.sliderChange(this.options.scales.indexOf(options.defaultScale));
	},

	onAdd: function(map) {
		this._initLayout();
		//this._update();
		
		return this._container;
	},

	onRemove: function(map) {
		
	},
	
	onSliderChange: function( event, ui ) {
		this.sliderChange(ui.value - 1);
	},

	sliderChange: function(scaleIndex) {		
		for(var layerName in this._layers) {
			var layer = this._layers[layerName];
			var wmsScale = this.options.wmsScales[scaleIndex];
			var wmsLayerName = layerName + "_" + wmsScale;
			if(layerName.toLowerCase().includes("landpolygonmaske")) {
				wmsLayerName = "landpolygon_maske_" + wmsScale;
			}
			layer.setParams({
				"layers": wmsLayerName
			});
		}
		
		this.fire('scalechange', { scale: this.options.scales[scaleIndex] } );
	},
	
	_initLayout: function () {
		var className = 'leaflet-control-scaleslider';
		var options = this.options;
		var container = L.DomUtil.create('div', className);
		L.DomEvent.disableClickPropagation(container);

		var slider = L.DomUtil.create('div', 'leaflet-control-scaleslider-slider', container);
		
		$( slider ).slider({
			value: options.scales.indexOf(options.defaultScale) + 1,
			min: 1,
			max: options.scales.length,
			step: 1,
			change: $.proxy(this.onSliderChange, this)
		}).each(function() {
			//
			// Add labels to slider whose values 
			// are specified by min, max and whose
			// step is set to 1
			//

			// Get the number of possible values
			var vals = options.scales.length - 1;

			// Space out values
			for (var i = 0; i <= vals; i++) {
				var el = $('<label>'+options.scales[i]+'</label>').css('left',(i/vals*100)+'%');
				el.addClass('leaflet-control-scaleslider-label');
				$( slider ).append(el);
			}
		});
		
		this._container = container;
	}
});

L.control.scaleSlider  = function(layers, options) {
	return new L.Control.ScaleSlider(layers, options);
}

L.extend(L.Control.ScaleSlider.prototype, L.Evented.prototype);