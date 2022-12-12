# -*- coding: utf-8 -*-
from osgeo import gdal, ogr, osr
from gdal_error_handler import GdalErrorHandler
from municipality import Municipality
from question import Question

import datetime
import json
import networkx as nx
import os
import pyperclip
import rtree

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


def load_rail_data(input_folder):

    result = {}

    driver = ogr.GetDriverByName('GML')
    in_ds = driver.Open(os.path.join(input_folder, 'geodk', 'jernbane.gml'))
    in_layer = in_ds.GetLayerByIndex(0)

    count = 0
    total = in_layer.GetFeatureCount()
    current_feature = in_layer.GetNextFeature()

    while current_feature is not None:
        count += 1

        result[count] = current_feature.GetGeometryRef().Clone()
        current_feature = in_layer.GetNextFeature()

    return result


def create_question(rail_data, municipality_data):

    result = {}
    # Build a search tree for the rail data.
    rail_tree = rtree.index.Index()
    for ref_id, line in rail_data.items():
        bbox = line.GetEnvelope()
        rail_tree.insert(ref_id, (bbox[0], bbox[2], bbox[1], bbox[3]))
    
    # Go through each municipality.
    for municipality_code, municipality in municipality_data.items():
        print('Processing railroad track length inside {}...'.format(municipality.name))
        question = { 
            'text': 'Hvor mange kilometer jernbane er der indenfor {} kommunes grænse?'.format(municipality.name),
            'answer': 0, 
            'answer_type': 'float'
        }

        # Locate all railroad tracks inside the municipality.
        bbox = municipality.geometry.GetEnvelope()
        candidate_ids = list(rail_tree.intersection((bbox[0], bbox[2], bbox[1], bbox[3])))

        for candidate_id in candidate_ids:
            # Check if the railroad track actually intersects the municipality.
            if not rail_data[candidate_id].Intersects(municipality.geometry):
                continue

            # Get the part which is inside the municipality.
            line = rail_data[candidate_id].Intersection(municipality.geometry)

            if line.IsEmpty():
                continue

            # Save the length as kilometers.
            question['answer'] += line.Length() / 1000.0
    
        result[municipality.code] = question

    return result


def save_question_data(question, output_folder):
    '''
    Save the computed results into json.
    '''

    #json_data = {k:v.to_json() for k,v in question.items()}
    
    with open(os.path.join(os.path.dirname(output_folder), 'q_jernbane_kommune.json'), 'w', encoding='utf8') as fp:
        json.dump(question, fp, ensure_ascii=False)
        #fp.write(json_data)
        #json.dump(question, fp)


if __name__ == "__main__":
    err = GdalErrorHandler()
    gdal.PushErrorHandler(err.handler)
    gdal.UseExceptions()  # Exceptions will get raised on anything >= gdal.CE_Failure

    project_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    input_data_folder = os.path.join(project_folder, 'input_data')

    rail_data = load_rail_data(input_data_folder)
    municipality_data = load_municipality_data(input_data_folder)

    question = create_question(rail_data, municipality_data)

    save_question_data(question, input_data_folder)

    gdal.PopErrorHandler()