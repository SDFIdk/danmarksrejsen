# -*- coding: utf-8 -*-
from osgeo import gdal, ogr, osr
from gdal_error_handler import GdalErrorHandler
from city import City
from municipality import Municipality

import datetime
import json
import networkx as nx
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


def build_network(cities):

    graph = nx.Graph()

    # Add nodes.
    for municipality_code, city in cities.items():
        graph.add_node(municipality_code)

    # Add edges.
    for municipality_code, city in cities.items():
        for neighbour in city.neighbours:        
            # Check if an edge has already been created.
            node_ids = [municipality_code, neighbour]
            node_ids.sort()
            from_id = node_ids[0]
            to_id = node_ids[1]

            if graph.has_edge(from_id, to_id):
                continue

            graph.add_edge(from_id, to_id)

            line = ogr.Geometry(ogr.wkbLineString)
            line.AddPoint_2D(*city.geometry.GetPoint_2D())
            line.AddPoint_2D(*cities[neighbour].geometry.GetPoint_2D())

            graph[from_id][to_id]['weight'] = line.Length()
    
    return graph


def calculate_routes(graph):
    # Go through all combinations.

    result = {}

    # Calculate the routes between all nodes and return the length for each route.
    route_set = nx.shortest_path_length(graph, weight='weight')

    for from_id, routes in route_set:
        valid_destinations = [k for k,v in routes.items() if v > 200000]

        for to_id in valid_destinations:
            if from_id not in result:
                result[from_id] = []
            
            result[from_id].append(to_id)

    return result


def save_route_data(routes, output_folder):
    '''
    Save the computed results into a geopackage.
    '''
    
    with open(os.path.join(os.path.dirname(output_folder), 'routes.json'), 'w') as fp:
        json.dump(routes, fp)


if __name__ == "__main__":
    err = GdalErrorHandler()
    gdal.PushErrorHandler(err.handler)
    gdal.UseExceptions()  # Exceptions will get raised on anything >= gdal.CE_Failure

    project_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    input_data_folder = os.path.join(project_folder, 'input_data')

    selected_cities = load_selected_cities(input_data_folder)

    graph = build_network(selected_cities)    

    routes = calculate_routes(graph)

    save_route_data(routes, input_data_folder)

    gdal.PopErrorHandler()