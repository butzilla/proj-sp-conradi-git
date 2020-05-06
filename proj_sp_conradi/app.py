# -----------------------------------------------------------
# This module works as a interactive UI for getting and
# storing data sets.
#
#
# Johannes Conradi, 2020 ETH Zuerich
# email: conradij@ethz.ch
# -----------------------------------------------------------

import os
import osmnx as ox
from proj_sp_conradi import get_store_osm


def valid_yn_input(pt):
    """Helper function, to check if input was valid"""
    if pt == 'y' or pt == 'n':
        return True
    else:
        return False


def valid_city_input(city, cities):
    """Helper function, to check if input was valid"""
    if city in cities:
        return True
    else:
        return False

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
            get_store_osm.get_store_osm(folder_path, filename, city, n_type)
            G = ox.load_graphml(filename=filename, folder=folder_path)
            print('Successfully downloaded and stored')
        except:
            print('Error while downloading and storing')

    print('Do you want to simplify the graph? (y/n)')
    simplify = input()
    while not valid_yn_input(simplify):
        print('Wrong input, try again:')
        simplify = input()
    if simplify == 'y':
        simplify = True
        print('The graph will be simplified, please give a range in meters to merge nodes:')
        tolerance = int(input())
    else:
        simplify = False
        tolerance = 0
        print('The graph will not be simplified')

    return simplify_graph(G, simplify, tolerance)



def run():
    """
    This function dictates the control flow of the app.
    """
    # Directory
    dirname = os.path.dirname(__file__)

    # List of possible cities
    cities = ['Zurich', 'Chicago']

    # Introduction in app and city selection
    print('Dear user, thanks for using this app! You can generate standardized mobility data sets of a specific city'
          'In the following you can choose whether to add different layers to the data sets. Please start with '
          'choosing a city: (Zurich)')
    city = input()
    while not valid_city_input(city, cities):
        print('City not list, please choose a different city:')
        city = input()

    # Get different layers for data set
    osm_nodes, osm_edges = get_osm(dirname, city)


    print('Do you also want to get PT layer? (y/n)')
    pt = 'y'
    while not valid_yn_input(pt):
        print('Wrong input, try again:')
        pt = input()
    if pt == 'y':
        print('yes')
    elif pt == 'n':
        print('Will not get PT layer')
