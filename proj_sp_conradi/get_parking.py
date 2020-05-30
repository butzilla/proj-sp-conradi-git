# -----------------------------------------------------------
# This script creates a city graph object of zurich. It gets
# OSM data from csv files and adds additional info from external
# sources to nodes and edges. Graph object is stored as csv
#
#
# Johannes Conradi, 2020 ETH Zuerich
# email: conradij@ethz.ch
# -----------------------------------------------------------

import osmnx as ox
import numpy as np
import utm
from shapely.geometry import Point
import geopandas as gpd
import os


def get_parking(edges, city, dirname):
    """
    This function adds the number of parking spots available at each road segment to egdes.
    """
    addtional_info_path = 'resources/addtional_info'
    open_parking_house_filename = 'oeffentliche_parkhaeser_' + city + '.csv'
    open_parking_filename = 'oeffentliche_parkplätze_' + city + '.csv'
    folder_path = os.path.join(dirname, addtional_info_path)
    open_parking_house_file_path = os.path.join(folder_path, open_parking_house_filename)
    open_parking_file_path = os.path.join(folder_path, open_parking_filename)

    open_parking_df = gpd.read_file(open_parking_file_path)
    open_parking_house = gpd.read_file(open_parking_house_file_path)

    edges['parking'] = np.zeros((len(edges['geometry'])))


    for i in range(len(open_parking_df['geometry'])):
        dist = (edges['geometry']).distance(open_parking_df['geometry'][i])
        edges.loc[dist.idxmin(), 'parking'] += 1

    for i in range(len(open_parking_house['geometry'])):
        dist = (edges['geometry']).distance(open_parking_house['geometry'][i])
        edges.loc[dist.idxmin(), 'parking'] += open_parking_house['anzahl_oeffentliche_pp'][i]
    return edges

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

if __name__ == '__main__':
    # Directories
    graph_path = '/Users/johannesconradi/proj-sp-conradi/Zurich/Output'
    output_path = '/Users/johannesconradi/proj-sp-conradi/Zurich/Output/parking.csv'

    # Gets OSM layer from file
    G = ox.load_graphml(filename='graph.graphml', folder=graph_path)

    # Simplify graph and get edges and nodes
    simplify = True
    tol = 15  # In meter
    nodes, edges = simplify_graph(G, simplify, tol)
    # Adds parking spots
    edges = get_parking(edges)
    print(edges)
    parking = edges['parking']
    print(sum(parking))
    parking.to_csv(output_path)


