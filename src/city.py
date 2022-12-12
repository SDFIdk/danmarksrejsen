# -*- encoding: utf-8 -*-
from osgeo import ogr

class City(object):

    def __init__(self, name, geometry, population):
        self.name = name
        self.municipality_code = None
        self.municipality_name = None
        self.population = population
        self.geometry = geometry
        self.neighbours = []

    
    def get_centroid(self):
        # Special case when dealing with copenhagen.
        if self.municipality_code == '0101' or self.name == 'København':
            p = ogr.Geometry(ogr.wkbPoint)
            p.AddPoint_2D(725083, 6175839)
            return p.Clone()
        
        return self.geometry.Centroid()