# -----------------------------------------------------------
# This script downloads OSM data and stores the data in graphml
# format
#
#
# Johannes Conradi, 2020 ETH Zuerich
# email: conradij@ethz.ch
# -----------------------------------------------------------

import osmnx as ox
import numpy as np
import utm
from shapely.geometry import Point
from proj_sp_conradi import utils
import os


def get_store_osm(folder_path, filename, city, n_type):
    # Get OSM layer
    G = ox.graph_from_place(city, network_type=n_type, simplify=False)

    # Save as graph ml
    ox.save_graphml(G, filename=filename, folder=folder_path, gephi=False)

def simplify_graph(G, simplify, tol):
    """
    This function gets OSM graph of given type and city.
    It returns the intersections and roadsecmemts of OSM graph in rad.
    """
    if not simplify:
        G = ox.simplify_graph(G)
        return ox.graph_to_gdfs(G, nodes=True, edges=False), ox.graph_to_gdfs(G, nodes=False, edges=True)

    else:
        # Project graph to get nodes in meter
        G_proj = ox.project_graph(G)

        # Simplify graph
        G2 = ox.simplify_graph(G_proj)

        # Get merge nodes that are closer than tolerance and project back to lang/long
        intersections = ox.clean_intersections(G2, tolerance=tol, dead_ends=False)
        points = np.array([point.xy for point in intersections])
        for i, point in enumerate(points):
            points[i] = utm.to_latlon(point[0], point[1], 32, 'U')
            intersections[i] = Point(points[i, 1, 0], points[i, 0, 0])

        # Project graph back to degrees
        G3 = ox.project_graph(G2, to_crs={'init': 'epsg:4326'})

        # Get edges Graph inn lang/long
        edges = ox.graph_to_gdfs(G3, nodes=False, edges=True)

        return intersections, edges


def get_osm(dirname, city):
    # Network type
    n_type = 'drive'

    # Construct directories
    osm_graph_path = 'resources/osm_graph'
    filename = city + '.graphml'
    folder_path = os.path.join(dirname, osm_graph_path)
    file_path = os.path.join(folder_path, filename)

    if os.path.isfile(file_path):
        print('OSM data has already been downloaded and stored in ' + file_path)
        # Gets OSM layer from file
        print('Will load data in app..')
        G = ox.load_graphml(filename=filename, folder=folder_path)
    else:
        print('OSM data has not been downloaded. It will be downloaded and stored in ' + file_path)
        try:
            get_store_osm(folder_path, filename, city, n_type)
            G = ox.load_graphml(filename=filename, folder=folder_path)
            print('Successfully downloaded and stored')
        except:
            print('Error while downloading and storing')

    print('Do you want to simplify the graph? (y/n)')
    simplify = input()
    while not utils.valid_yn_input(simplify):
        print('Wrong input, try again:')
        simplify = input()
    if simplify == 'y':
        simplify = True
        print('The graph will be simplified, please give a range in meters to merge nodes:')
        tolerance = int(input())
        print('simplifying..')
    else:
        simplify = False
        print('The graph will not be simplified')
        tolerance = 0
    return simplify_graph(G, simplify, tolerance)

# TODO plot
