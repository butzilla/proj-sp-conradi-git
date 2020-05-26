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
from proj_sp_conradi import osm_layer
from proj_sp_conradi import gtfs_layer
from proj_sp_conradi import region_info_layer
from proj_sp_conradi import utils


def run():
    """
    This function dictates the control flow of the app. It first gets all the necessary information from the user and
    then collects the data.
    """
    # Directory
    dirname = os.path.dirname(__file__)

    # List of possible cities
    cities = ['Zurich', 'Chicago']

    ### Start of user interaction ###

    # Introduction in app and city selection
    print('Dear user, thanks for using this app! You can generate standardized mobility data sets of a specific city'
          'In the following you can choose whether to add different layers to the data sets. Please start with '
          'choosing a city: (Zurich)')
    city = input()
    while not utils.valid_city_input(city, cities):
        print('City not list, please choose a different city:')
        city = input()

    # OSM layer user interaction
    print('Do you want to simplify the OSM graph? (y/n)')
    simplify = input()
    while not utils.valid_yn_input(simplify):
        print('Wrong input, try again:')
        simplify = input()
    if simplify == 'y':
        simplify = True
        print('The graph will be simplified, please give a range in meters to merge nodes (1<tolerance<50):')
        tolerance = int(input())
    else:
        simplify = False
        print('The graph will not be simplified')
        tolerance = 0
    print('Do you want to plot the OSM graph? (y/n)')
    plot_osm = input()
    while not utils.valid_yn_input(plot_osm):
        print('Wrong input, try again:')
        plot_osm = input()
    if plot_osm == 'y':
        plot_osm = True
    else:
        plot_osm = False

    # GTFS layer user interaction
    print('Do you want to get public transport layer? (y/n)')
    pt = input()
    while not utils.valid_yn_input(pt):
        print('Wrong input, try again:')
        pt = input()
    if pt == 'y':
        url = gtfs_layer.get_gtfs_url(city)
        print('Do you plot public transport layer? (y/n)')
        plot_gtfs = input()
        while not utils.valid_yn_input(pt):
            print('Wrong input, try again:')
            plot_gtfs = input()
    else:
        print('Will not get GTFS layer.')

    # Additional information user interaction
    print('Do you want to get additional information on region layer? (y/n)')
    ad = input()
    while not utils.valid_yn_input(pt):
        print('Wrong input, try again:')
        ad = input()

    # Additional information user interaction
    print('Do you want to add parking spots to road segments (y/n)')
    parking = input()
    while not utils.valid_yn_input(pt):
        print('Wrong input, try again:')
        parking = input()

    ### End of user interaction ###

    # Get and plot osm layer
    osm_nodes, osm_edges = osm_layer.get_osm(dirname, city, simplify, tolerance, plot_osm)

    # Get and plot GTFS layer
    if pt == 'y':
        G = gtfs_layer.get_gtfs(city, url, plot_gtfs)

    # Get additional information on region layer
    if ad == 'y':
        # Gets "Statistische Quartiere" for Zurich and adds further info to each region
        geomdf = region_info_layer.get_geom()

        # Map each node to a geograpic region
        osm_nodes = region_info_layer.get_geo_node(osm_nodes, geomdf)

        # Add speed-limit to each edge and
        # calculate time it takes to travel on road-segment.
        osm_edges = region_info_layer.get_speed_time(osm_edges)

    if parking:
        # Add number of parking spots available at each edge
        osm_edges = region_info_layer.get_parking(osm_edges)




    # TODO add census and demand data data
