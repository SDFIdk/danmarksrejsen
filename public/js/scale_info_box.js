L.Control.ScaleInfoBox = L.Control.extend({
	options: {
		position: 'topleft',
		defaultScale: '',
		scales: [],
		scaleLayers: [],
		scaleData: {}
	},	

	onAdd: function(map) {
		this._initLayout();
		
		return this._container;
	},

	onRemove: function(map) {
		
	},
	
	changeScale: function(event) {
		// Empty the box.
		while (this._container.firstChild) {
			this._container.removeChild(this._container.lastChild);
		}
		
		// Rebuild the box.
		this._buildBox(event.scale);
	},
	
	_initLayout: function () {
		var className = 'leaflet-control-scaleinfobox leaflet-control-layers leaflet-control-layers-expanded';
		var options = this.options;
		var container = L.DomUtil.create('div', className);
		L.DomEvent.disableClickPropagation(container);
		
		this._container = container;

		this._buildBox(options.defaultScale);
	},
	
	_buildBox: function(scale) {
		var container = this._container;
		
		var box = L.DomUtil.create('div', 'leaflet-control-scaleinfobox-box', container);
		var title = L.DomUtil.create('div', 'leaflet-control-scaleinfobox-box-title', box);
		title.innerHTML = "Detaljer for: " + scale;
		var table = L.DomUtil.create('table', 'leaflet-control-scaleinfobox-box-table', box);		
		var thead = L.DomUtil.create('thead', 'leaflet-control-scaleinfobox-box-thead', table);
		var row = L.DomUtil.create('tr', 'leaflet-control-scaleinfobox-box-thead-row', thead);
		var th = L.DomUtil.create('th', 'leaflet-control-scaleinfobox-box-th', row);
		th.innerHTML = "Lag";
		th = L.DomUtil.create('th', 'leaflet-control-scaleinfobox-box-th', row);
		th.innerHTML = "Punkter";
		th = L.DomUtil.create('th', 'leaflet-control-scaleinfobox-box-th', row);
		th.innerHTML = "Objekter";
		var tbody = L.DomUtil.create('tbody', 'leaflet-control-scaleinfobox-box-tbody', table);
		
		for(var i in this.options.scaleLayers) {
			var layerName = this.options.scaleLayers[i];
			var layerInfo = null;

			if(layerName in this.options.scaleData[scale]) {
				layerInfo = this.options.scaleData[scale][layerName];
			}
			
			var row = L.DomUtil.create('tr', 'leaflet-control-scaleinfobox-box-table-row', tbody);
			var td = L.DomUtil.create('td', 'leaflet-control-scaleinfobox-box-table-cell', row);
			td.innerHTML = layerName + ":";
			
			td = L.DomUtil.create('td', 'leaflet-control-scaleinfobox-box-table-cell leaflet-control-scaleinfobox-box-table-cell-numeric', row);
			if(layerInfo != null) {
				td.innerHTML = layerInfo["pointCount"];
			} else {
				td.innerHTML = "0";
			}
			td = L.DomUtil.create('td', 'leaflet-control-scaleinfobox-box-table-cell leaflet-control-scaleinfobox-box-table-cell-numeric', row);
			if(layerInfo != null) {
				td.innerHTML = layerInfo["featureCount"];
			} else {
				td.innerHTML = "0";
			}
		}		
	}
});

L.control.scaleInfoBox  = function(opts) {
	return new L.Control.ScaleInfoBox(opts);
}