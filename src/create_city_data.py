# -*- coding: utf-8 -*-
from osgeo import gdal, ogr, osr
from gdal_error_handler import GdalErrorHandler
from city import City
from municipality import Municipality

import datetime
import os
import pyperclip
import rtree

def load_selected_cities(input_folder):
    result = {}

    driver = ogr.GetDriverByName('GPKG')
    in_ds = driver.Open(os.path.join(os.path.dirname(input_folder), 'data.gpkg'))
    in_layer = in_ds.GetLayerByName('cities')

    count = 0
    total = in_layer.GetFeatureCount()
    current_feature = in_layer.GetNextFeature()

    while current_feature is not None:
        count += 1
        name = current_feature.GetFieldAsString('name')
        municipality_code = current_feature.GetFieldAsString('municipality_code')

        result[municipality_code] = name
        current_feature = in_layer.GetNextFeature()

    return result


def load_city_data(input_folder, cities):

    result = {}

    driver = ogr.GetDriverByName('GML')
    in_ds = driver.Open(os.path.join(input_folder, 'ds', 'bebyggelse.gml'))
    in_layer = in_ds.GetLayerByIndex(0)

    # Only load cities.
    in_layer.SetAttributeFilter('bebyggelsestype = \'by\'')

    count = 0
    total = in_layer.GetFeatureCount()
    current_feature = in_layer.GetNextFeature()

    while current_feature is not None:
        
        name = current_feature.GetFieldAsString('navn_1_skrivemaade')

        selected_city = [k for k,v in cities.items() if v == name]

        if len(selected_city) > 0:    
            count += 1
            municipality_code = selected_city[0]

            result[municipality_code] = current_feature.GetGeometryRef().Clone()
            result[municipality_code].Set3D(0)
        
        current_feature = in_layer.GetNextFeature()

        #if count > 15:
        #    break

    return result


def save_city_data(cities, output_folder):
    '''
    Save the computed results into a geopackage.
    '''
    projection = osr.SpatialReference()
    projection.ImportFromEPSG(25832)
    driver = ogr.GetDriverByName('GeoJSON')
    ds = driver.CreateDataSource(os.path.join(os.path.dirname(output_folder), 'city_polygons.js'))
    layer = ds.CreateLayer('cities', projection, geom_type=ogr.wkbMultiPolygon)

    # layer.CreateField(ogr.FieldDefn('name', ogr.OFTString))
    # layer.CreateField(ogr.FieldDefn('municipality_name', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('municipality_code', ogr.OFTString))
    # layer.CreateField(ogr.FieldDefn('population', ogr.OFTInteger))
    # layer.CreateField(ogr.FieldDefn('neighbours', ogr.OFTString))

    for ref_id, city in cities.items():
        feature = ogr.Feature(layer.GetLayerDefn())
        # feature.SetField('name', city.name)
        # feature.SetField('population', city.population)
        # feature.SetField('municipality_name', city.municipality_name)
        feature.SetField('municipality_code', ref_id)
        # feature.SetField('neighbours', ','.join(city.neighbours))
        feature.SetGeometry(city.Clone())

        layer.CreateFeature(feature)

    layer = None
    ds = None


if __name__ == "__main__":
    err = GdalErrorHandler()
    gdal.PushErrorHandler(err.handler)
    gdal.UseExceptions()  # Exceptions will get raised on anything >= gdal.CE_Failure

    project_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    input_data_folder = os.path.join(project_folder, 'input_data')

    selected_cities = load_selected_cities(input_data_folder)
    cities = load_city_data(input_data_folder, selected_cities)

    save_city_data(cities, input_data_folder)

    gdal.PopErrorHandler()