var scales = ["Reference", "1:10.000", "1:25.000", "1:50.000", "1:100.000", "1:250.000", "1:500.000", "1:1.000.000", "1:2.500.000", "1:5.000.000", "1:10.000.000"];
var wmsScales = ["ref", "10", "25", "50", "100","250","500","1000","2500","5000","10000"];
var scaleLayers = ["Landpolygon", "Havpolygon", "Landpolygonmaske", "Kyst", "Havn"];

var scaleData = {
	"Reference": {
		"Landpolygonmaske": { "pointCount": "1.105.646", "featureCount": "27"},
		"Havpolygon": { "pointCount": "1.104.104", "featureCount": "28"},
		"Havn": { "pointCount": "65.727", "featureCount": "1.190"},
		"Kyst": { "pointCount": "1.049.382", "featureCount": "12.257"},
		"Landpolygon": { "pointCount": "1.104.970", "featureCount": "1.525"}
	},
	"1:5.000.000": {
		"Landpolygon": { "pointCount": "1.454", "featureCount": "23"},
		"Havpolygon": { "pointCount": "2.347", "featureCount": "21"},
		"Kyst": { "pointCount": "1.437", "featureCount": "24"},
		"Landpolygonmaske": { "pointCount": "2.132", "featureCount": "20"}
	},
	"1:500.000": {
		"Landpolygon": { "pointCount": "23.085", "featureCount": "209"},
		"Kyst": { "pointCount": "21.393", "featureCount": "318"},
		"Landpolygonmaske": { "pointCount": "23.763", "featureCount": "48"},
		"Havn": { "pointCount": "1.716", "featureCount": "105"},
		"Havpolygon": { "pointCount": "23.834", "featureCount": "49"}
	},
	"1:250.000": {
		"Havpolygon": { "pointCount": "46.344", "featureCount": "55"},
		"Landpolygonmaske": { "pointCount": "46.353", "featureCount": "54"},
		"Kyst": { "pointCount": "41.873", "featureCount": "526"},
		"Landpolygon": { "pointCount": "45.675", "featureCount": "353"},
		"Havn": { "pointCount": "3.896", "featureCount": "197"}
	},
	"1:25.000": {
		"Havpolygon": { "pointCount": "373.156", "featureCount": "40"},
		"Landpolygonmaske": { "pointCount": "373.897", "featureCount": "39"},
		"Landpolygon": { "pointCount": "373.221", "featureCount": "1.474"},
		"Havn": { "pointCount": "25.822", "featureCount": "710"},
		"Kyst": { "pointCount": "347.611", "featureCount": "1.970"}
	},
	"1:10.000.000": {
		"Havpolygon": { "pointCount": "1.951", "featureCount": "21"},
		"Landpolygon": { "pointCount": "1.062", "featureCount": "22"},
		"Landpolygonmaske": { "pointCount": "1.722", "featureCount": "20"},
		"Kyst": { "pointCount": "1.050", "featureCount": "23"}
	},
	"1:10.000": {
		"Havn": { "pointCount": "45.006", "featureCount": "811"},
		"Landpolygonmaske": { "pointCount": "731.264", "featureCount": "27"},
		"Landpolygon": { "pointCount": "730.588", "featureCount": "1.523"},
		"Havpolygon": { "pointCount": "729.543", "featureCount": "28"},
		"Kyst": { "pointCount": "684.955", "featureCount": "2.047"}
	},
	"1:100.000": {
		"Landpolygon": { "pointCount": "112.396", "featureCount": "706"},
		"Havpolygon": { "pointCount": "112.913", "featureCount": "63"},
		"Havn": { "pointCount": "10.985", "featureCount": "450"},
		"Kyst": { "pointCount": "101.764", "featureCount": "1.044"},
		"Landpolygonmaske": { "pointCount": "113.072", "featureCount": "62"}
	},
	"1:50.000": {
		"Landpolygon": { "pointCount": "204.295", "featureCount": "1.062"},
		"Kyst": { "pointCount": "187.771", "featureCount": "1.495"},
		"Havpolygon": { "pointCount": "204.616", "featureCount": "53"},
		"Havn": { "pointCount": "16.937", "featureCount": "602"},
		"Landpolygonmaske": { "pointCount": "204.973", "featureCount": "52"}
	},
	"1:1.000.000": {
		"Landpolygon": { "pointCount": "11.550", "featureCount": "129"},
		"Havpolygon": { "pointCount": "12.344", "featureCount": "37"},
		"Landpolygonmaske": { "pointCount": "12.214", "featureCount": "36"},
		"Havn": { "pointCount": "656", "featureCount": "49"},
		"Kyst": { "pointCount": "10.873", "featureCount": "184"}
	},
	"1:2.500.000": {
		"Kyst": { "pointCount": "5.596", "featureCount": "98"},
		"Havpolygon": { "pointCount": "6.667", "featureCount": "26"},
		"Landpolygon": { "pointCount": "5.824", "featureCount": "81"},
		"Havn": { "pointCount": "195", "featureCount": "16"},
		"Landpolygonmaske": { "pointCount": "6.490", "featureCount": "25"}
	}
};