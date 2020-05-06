# -----------------------------------------------------------
# This script downloads GTFS data and stores it as an
# adjacency matrix.
#
#
# Johannes Conradi, 2020 ETH Zuerich
# email: conradij@ethz.ch
# -----------------------------------------------------------

import os
import requests
import tempfile

import geopandas as gpd
import networkx as nx
import osmnx as ox
import numpy as np
import peartree as pt
from shapely.geometry import Point, shape
import pandas as pd
from collections import OrderedDict

def nominatim_query(query):
    """
    This function gets the coordinates for a given city.
    """
    params = OrderedDict()
    params['format'] = 'json'
    params['limit'] = 1
    params['dedupe'] = 0
    params['polygon_geojson'] = 1
    params['q'] = query

    url = 'https://nominatim.openstreetmap.org/search'
    prepared_url = requests.Request('GET', url, params=params).prepare().url

    response = requests.get(url, params=params)
    response_json = response.json()
    return shape(response_json[0]['geojson'])