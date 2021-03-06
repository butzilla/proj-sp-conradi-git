# -----------------------------------------------------------
# This script provides functions OSM data handling.
#
#
# Johannes Conradi, 2020 ETH Zuerich
# email: conradij@ethz.ch
# -----------------------------------------------------------

import osmnx as ox
import numpy as np
from shapely.geometry import Point
import os
import matplotlib.pyplot as plt
import pyproj



def get_store_osm(folder_path, filename, city, n_type):
    """
    This function downloads OSM graph and stores as graphml in resource directory.
    """
    # Get OSM layer
    G = ox.graph_from_place(city, network_type=n_type, simplify=False)

    # Save as graph ml
    ox.save_graphml(G, filename=filename, folder=folder_path, gephi=False)

def simplify_graph(G, simplify, tol, plot, path_fig_osm):
    """
    This function either simplifies the OSM graph with ox.simplify_graph or with both ox.simplify_graph and
    ox.clean_intersections.
    It returns the intersections and road segmemts of OSM graph as dfs in rad.
    """
    # If not supposed to simplify, still use osmnx function to simplify.
    if not simplify:
        G = ox.simplify_graph(G)
        if plot:
            fig, ax = ox.plot_graph(G, fig_height=10, show=False, close=False)
            plt.savefig(path_fig_osm)
        points = ox.graph_to_gdfs(G, nodes=True, edges=False)
        edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
        #return points[['osmid', 'geometry']], edges[['u', 'v', 'geometry', 'highway', 'lanes', 'length',  'name', 'oneway', 'maxspeed']]
        return points[['osmid', 'geometry']], edges[['u', 'v', 'geometry', 'highway', 'lanes', 'length', 'name', 'oneway', 'maxspeed']]

    # If supposed to simplify use both osmnx function to simplify as well as clean_intersections to merge multiple
    # nodes on intersections.
    else:
        print("Simplifying graph...")
        proj_wgs84 = pyproj.Proj(init="epsg:4326")
        proj_gk4 = pyproj.Proj(init="epsg:31468")
        # Project graph to get nodes in meter
        G_proj = ox.project_graph(G, to_crs="epsg:31468")
        # Simplify graph
        G2 = ox.simplify_graph(G_proj)
        # Get merged nodes that are not closer than tolerance
        intersections = ox.clean_intersections(G2, tolerance=tol, dead_ends=False) #TODO: New version of ox has funciton called consolidate_intersections, implement that
        points = np.array([point.xy for point in intersections])
        for i, point in enumerate(points):
            points[i] = pyproj.transform(proj_gk4, proj_wgs84, point[0], point[1])
            intersections[i] = Point(points[i, 1, 0], points[i, 0, 0])
        # Project graph back to degrees
        G3 = ox.project_graph(G2, to_crs={'init': 'epsg:4326'})

        # Get edges Graph in lat/long
        edges = ox.graph_to_gdfs(G3, nodes=False, edges=True)
        if plot:
            fig, ax = ox.plot_graph(G3, fig_height=10, show=False, close=False, node_alpha=0)
            ax.scatter(x=points[:, 0], y=points[:, 1], zorder=2, color='#66ccff', edgecolors='k')
            plt.savefig(path_fig_osm)

        return intersections, edges[['u', 'v', 'geometry', 'highway', 'lanes', 'length',  'name', 'oneway', 'maxspeed']]


def get_osm(dirname, city, simplify, tolerance, plot, path_fig_osm):
    """"This function works as the main for the osm layer."""
    # Network type
    n_type = 'drive'
    # Construct directories
    osm_graph_path = 'resources/osm_graph'
    filename = city + '.graphml'
    folder_path = os.path.join(dirname, osm_graph_path)
    file_path = os.path.join(folder_path, filename)
    # Check if data has already been downloaded
    if os.path.isfile(file_path):
        print('OSM data has already been downloaded and stored in ' + file_path)
        # Gets OSM layer from file
        print('Will load data in app...')
        G = ox.load_graphml(filename=filename, folder=folder_path)
    else:
        print('OSM data has not been downloaded. It will be downloaded and stored in ' + file_path)
        try:
            # Download data
            get_store_osm(folder_path, filename, city, n_type)
            # Gets OSM layer from file
            G = ox.load_graphml(filename=filename, folder=folder_path)
            print('Successfully downloaded and stored')
        except:
            print('Error while downloading and storing')
    return simplify_graph(G, simplify, tolerance, plot, path_fig_osm)

