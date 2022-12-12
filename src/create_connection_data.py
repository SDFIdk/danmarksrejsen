# -*- coding: utf-8 -*-
from osgeo import gdal, ogr, osr
from gdal_error_handler import GdalErrorHandler
from city import City
from municipality import Municipality

import datetime
import networkx
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
        population = current_feature.GetFieldAsInteger('population')
        municipality_code = current_feature.GetFieldAsString('municipality_code')
        neighbours = current_feature.GetFieldAsString('neighbours')

        result[municipality_code] = City(name, current_feature.GetGeometryRef().Clone(), population)
        result[municipality_code].neighbours = neighbours.split(',')
        current_feature = in_layer.GetNextFeature()

    return result


def build_connections(cities):
    lines = {}

    for municipality_code, city in cities.items():
        for neighbour in city.neighbours:
            point_ids = [municipality_code, neighbour]
            point_ids.sort()
            point_ids = '-'.join(point_ids)

            if point_ids in lines:
                continue

            line = ogr.Geometry(ogr.wkbLineString)
            line.AddPoint_2D(*city.geometry.GetPoint_2D())
            line.AddPoint_2D(*cities[neighbour].geometry.GetPoint_2D())

            lines[point_ids] = line.Clone()
    
    return lines


def save_connection_data(connections, output_folder):
    '''
    Save the computed results into a geopackage.
    '''
    projection = osr.SpatialReference()
    projection.ImportFromEPSG(25832)
    driver = ogr.GetDriverByName('GeoJSON')
    ds = driver.CreateDataSource(os.path.join(os.path.dirname(output_folder), 'connections.js'))
    layer = ds.CreateLayer('cities', projection, geom_type=ogr.wkbLineString)

    # layer.CreateField(ogr.FieldDefn('name', ogr.OFTString))
    # layer.CreateField(ogr.FieldDefn('municipality_name', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('from', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('to', ogr.OFTString))
    # layer.CreateField(ogr.FieldDefn('population', ogr.OFTInteger))
    # layer.CreateField(ogr.FieldDefn('neighbours', ogr.OFTString))

    for from_to, line in connections.items():
        feature = ogr.Feature(layer.GetLayerDefn())
        
        from_id, to_id = from_to.split('-')
        feature.SetField('from', from_id)
        feature.SetField('to', to_id)
        # feature.SetField('neighbours', ','.join(city.neighbours))
        feature.SetGeometry(line.Clone())

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

    connections = build_connections(selected_cities)
    save_connection_data(connections, input_data_folder)

    gdal.PopErrorHandler()