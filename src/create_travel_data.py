# -*- coding: utf-8 -*-
from osgeo import gdal, ogr, osr
from gdal_error_handler import GdalErrorHandler
from city import City
from municipality import Municipality

import datetime
import os
import pyperclip
import rtree


def load_city_data(input_folder):

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
        count += 1
        population = int(current_feature.GetFieldAsString('indbyggertal'))
        name = current_feature.GetFieldAsString('navn_1_skrivemaade')
        in_type = current_feature.GetFieldAsString('bebyggelsestype')

        result[count] = City(name, current_feature.GetGeometryRef().Clone(), population)
        current_feature = in_layer.GetNextFeature()

        #if count > 15:
        #    break

    return result


def load_city_connection_data(input_folder):

    result = []

    driver = ogr.GetDriverByName('GPKG')
    in_ds = driver.Open(os.path.join(input_folder, 'support_data', 'support_data.gpkg'))
    in_layer = in_ds.GetLayerByName('additional_city_connections')

    count = 0
    total = in_layer.GetFeatureCount()
    current_feature = in_layer.GetNextFeature()

    while current_feature is not None:
        count += 1

        result.append(current_feature.GetGeometryRef().Clone())
        current_feature = in_layer.GetNextFeature()

        #if count > 15:
        #    break

    return result


def load_municipality_data(input_folder):

    result = {}

    driver = ogr.GetDriverByName('GML')
    in_ds = driver.Open(os.path.join(input_folder, 'dagi', 'dagi_10m_nohist_l1.kommuneinddeling.gml'))
    in_layer = in_ds.GetLayerByIndex(0)

    count = 0
    total = in_layer.GetFeatureCount()
    current_feature = in_layer.GetNextFeature()

    while current_feature is not None:
        count += 1
        code = current_feature.GetFieldAsString('kommunekode')
        name = current_feature.GetFieldAsString('navn')

        result[int(code)] = Municipality(name, code, current_feature.GetGeometryRef().Clone())
        current_feature = in_layer.GetNextFeature()

        #if count > 15:
        #    break

    return result
    

def select_largest_city_in_municipality(cities, city_tree, municipalities):
    '''
    For each municipality, select the city with the largest population.
    '''

    result = {}

    print('Looking for the largest cities...')
    for code, municipality in municipalities.items():
        print('  {}: '.format(municipality.name), end='')
        # Find all cities within the municipality.
        bbox = municipality.geometry.GetEnvelope()
        candidate_ids = list(city_tree.intersection((bbox[0], bbox[2], bbox[1], bbox[3])))

        max_population = 0
        best_city_id = None

        for candidate_id in candidate_ids:
            # Does the city actually intersect the municipality?
            if not cities[candidate_id].geometry.Intersects(municipality.geometry):
                # No.
                continue

            # Determine how large a part of the city which intersects the municipality.
            intersection = cities[candidate_id].geometry.Intersection(municipality.geometry)

            if intersection.Area() / cities[candidate_id].geometry.Area() < 0.5:
                # This city is not primarily inside this municipality.
                continue
            
            # Yes, check the population.
            if cities[candidate_id].population > max_population:
                max_population = cities[candidate_id].population
                best_city_id = candidate_id
        
        if best_city_id is None:
            print('None')
        else:
            print('{}'.format(cities[best_city_id].name))

            cities[best_city_id].municipality_code = municipality.code
            cities[best_city_id].municipality_name = municipality.name

            # Store the best candidate.
            result[municipality.code] = cities[best_city_id]
    
    return result


def locate_city_neighbours(cities, municipalities, municipality_tree, additional_city_connections):
    '''
    For the municipality belonging to a city, determine which municipalities are neighbouring.

    This way each city will get a list of neighbour cities.

    A city might be connected by road or ferry, and the additional connections are used to add these
    kinds of connections.
    '''

    print('Locating neighbours for each city...')

    for code, city in cities.items():
        print('  {}: '.format(city.name), end='')
        municipality = municipalities[int(code)]

        # Find all municipalities close to this municipality.
        bbox = municipality.geometry.GetEnvelope()
        candidate_ids = list(municipality_tree.intersection((bbox[0], bbox[2], bbox[1], bbox[3])))

        for candidate_id in candidate_ids:
            if candidate_id == int(code):
                # We found us.
                continue 

            # Is the municipality a neighbour?
            if municipalities[candidate_id].geometry.Distance(municipality.geometry) > 1:
                # No.
                continue

            # Yes.
            city.neighbours.append('0{}'.format(candidate_id))

        print('{}'.format(', '.join([municipalities[int(x)].name for x in city.neighbours])))

    print('Add additional connections between cities...')

    # Add the extra connections provided by roads or ferry.
    for line in additional_city_connections:
        # Determine which two municipalities the line connects.
        p1 = line.GetPoint_2D(0)
        p2 = line.GetPoint_2D(line.GetPointCount() - 1)

        connection = []

        for point in [p1, p2]:
            # Find the municipality close to this point.
            candidate_ids = list(municipality_tree.intersection((point[0] - 1, point[0] + 1, point[1] - 1, point[1] + 1)))

            p = ogr.Geometry(ogr.wkbPoint)
            p.AddPoint_2D(point[0], point[1])

            for candidate_id in candidate_ids:
                # If the point is inside the municipality, we have found the one were looking for.
                if not municipalities[candidate_id].geometry.Contains(p):
                    continue

                # We have found the municipality.
                connection.append('0{}'.format(candidate_id))

                # Just stop here.
                break
            
        # Add the connection to the cities.
        cities[connection[0]].neighbours.append(connection[1])
        cities[connection[1]].neighbours.append(connection[0])

        print('  {} to {}'.format(cities[connection[0]].name, cities[connection[1]].name))


def save_city_data(cities, output_folder):
    '''
    Save the computed results into a geopackage.
    '''
    projection = osr.SpatialReference()
    projection.ImportFromEPSG(25832)
    driver = ogr.GetDriverByName('GPKG')
    ds = driver.CreateDataSource(os.path.join(output_folder, 'data.gpkg'))
    layer = ds.CreateLayer('cities', projection, geom_type=ogr.wkbPoint)

    layer.CreateField(ogr.FieldDefn('name', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('municipality_name', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('municipality_code', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('population', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('neighbours', ogr.OFTString))

    for ref_id, city in cities.items():
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetField('name', city.name)
        feature.SetField('population', city.population)
        feature.SetField('municipality_name', city.municipality_name)
        feature.SetField('municipality_code', city.municipality_code)
        feature.SetField('neighbours', ','.join(city.neighbours))
        feature.SetGeometry(city.get_centroid())

        layer.CreateFeature(feature)

    layer = None
    ds = None


def save_city_points_as_json(cities, output_folder):
    projection = osr.SpatialReference()
    projection.ImportFromEPSG(25832)
    driver = ogr.GetDriverByName('GeoJSON')
    ds = driver.CreateDataSource(os.path.join(output_folder, 'city_points.json'))
    layer = ds.CreateLayer('cities', projection, geom_type=ogr.wkbPoint)

    layer.CreateField(ogr.FieldDefn('name', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('municipality_name', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('municipality_code', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('population', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('neighbours', ogr.OFTString))

    for ref_id, city in cities.items():
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetField('name', city.name)
        feature.SetField('population', city.population)
        feature.SetField('municipality_name', city.municipality_name)
        feature.SetField('municipality_code', city.municipality_code)
        feature.SetField('neighbours', ','.join(city.neighbours))
        feature.SetGeometry(city.get_centroid())

        layer.CreateFeature(feature)

    layer = None
    ds = None


def save_city_polygons_as_json(cities, output_folder):
    projection = osr.SpatialReference()
    projection.ImportFromEPSG(25832)
    driver = ogr.GetDriverByName('GeoJSON')
    ds = driver.CreateDataSource(os.path.join(output_folder, 'city_polygons.json'))
    layer = ds.CreateLayer('cities', projection, geom_type=ogr.wkbPoint)

    layer.CreateField(ogr.FieldDefn('name', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('municipality_name', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('municipality_code', ogr.OFTString))
    
    for ref_id, city in cities.items():
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetField('name', city.name)
        feature.SetField('municipality_name', city.municipality_name)
        feature.SetField('municipality_code', city.municipality_code)
        feature.SetGeometry(city.geometry.Clone())

        layer.CreateFeature(feature)

    layer = None
    ds = None


if __name__ == "__main__":
    err = GdalErrorHandler()
    gdal.PushErrorHandler(err.handler)
    gdal.UseExceptions()  # Exceptions will get raised on anything >= gdal.CE_Failure

    project_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    input_data_folder = os.path.join(project_folder, 'input_data')
    #public_folder = os.path.join(project_folder, 'public')
    #data_folder = os.path.join(public_folder, 'data')
    #image_folder = os.path.join(public_folder, 'images')
    max_image_size = 512


    additional_city_connections = load_city_connection_data(input_data_folder)
    cities = load_city_data(input_data_folder)
    city_tree = rtree.index.Index()
    for ref_id, city in cities.items():
        bbox = city.geometry.GetEnvelope()
        city_tree.insert(ref_id, (bbox[0], bbox[2], bbox[1], bbox[3]))

    municipalities = load_municipality_data(input_data_folder)

    municipality_tree = rtree.index.Index()
    for ref_id, municipality in municipalities.items():
        bbox = municipality.geometry.GetEnvelope()
        municipality_tree.insert(ref_id, (bbox[0], bbox[2], bbox[1], bbox[3]))

    selected_cities = select_largest_city_in_municipality(cities, city_tree, municipalities)

    # Verify unique cities.
    if len([k for k,v in selected_cities.items() if v is not None]) == len(set([v.name for k,v in selected_cities.items() if v is not None])):
        a = 1

    locate_city_neighbours(selected_cities, municipalities, municipality_tree, additional_city_connections)

    #save_city_data(selected_cities, project_folder)

    save_city_points_as_json(selected_cities, project_folder)
    save_city_polygons_as_json(selected_cities, project_folder)

    gdal.PopErrorHandler()