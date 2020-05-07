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
from proj_sp_conradi import utils


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
    while not utils.valid_city_input(city, cities):
        print('City not list, please choose a different city:')
        city = input()

    # Get and plot osm layer
    osm_nodes, osm_edges = osm_layer.get_osm(dirname, city)

    # Get and plot GTFS layer
    print('Do you also want to get public transport layer? (y/n)')
    pt = input()
    while not utils.valid_yn_input(pt):
        print('Wrong input, try again:')
        pt = input()
    if pt == 'y':
        G = gtfs_layer.get_gtfs(dirname, city)
    elif pt == 'n':
        print('Will not get public transport layer')
    gtfs_layer.plot(G)
    # TODO add census and demand data data
