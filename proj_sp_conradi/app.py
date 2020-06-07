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
    countries = ['Switzerland', 'US']

    ### Start of user interaction ###

    # Introduction in app and city selection
    print('Dear user, thanks for using this app! You can generate standardized mobility data sets of a specific city'
          'In the following you can choose whether to add different layers to the data sets. Please start with '
          'choosing a country: (US)')
    country = input()
    while not utils.valid_city_input(country, countries):
        print('Country not list, please choose a different city:')
        country = input()
    print('Please choose a city in ' + country)
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
    if ad == 'y' and not city == 'Zurich' and not country == 'US':
        print("If you want to get additional informations for "+city+" please add the information to the folder "
                                                     "/resources/additional_info in the same format as shown on the "
                                                     "example of Zurich")
    if ad == 'y' and country == 'US':
        print('Please provide the state nr. of ' + city + ' (17)')
        state = input()
        print('Please also provide the county nr. of ' + city + ' (031)')
        county = input()

    # Parking user interaction
    print('Do you want to add parking spots to road segments (y/n)')
    parking = input()
    while not utils.valid_yn_input(pt):
        print('Wrong input, try again:')
        parking = input()
    if parking == 'y' and not city == 'Zurich':
        print("If you want to get parking for "+city+" please add the information to the folder "
                                                     "/resources/additional_info in the same format as shown on the "
                                                     "example of Zurich")

    ### End of user interaction ###

    # Directories
    osm_eges_filename = 'osm_edges_' + city + '.csv'
    gtfs_eges_filename = 'gtfs_edges_' + city + '.csv'
    gtfs_nodes_filename = 'gtfs_nodes_' + city + '.csv'
    gtfs_stop_times_filename = 'gtfs_stop_times_' + city + '.csv'
    output_path = os.path.join(dirname, 'output')
    osm_edges_path = os.path.join(output_path, osm_eges_filename)
    gtfs_edges_path = os.path.join(output_path, gtfs_eges_filename)
    gtfs_nodes_path = os.path.join(output_path, gtfs_nodes_filename)
    stop_times_path = os.path.join(output_path, gtfs_stop_times_filename)

    # Get and plot osm layer
    osm_nodes, osm_edges = osm_layer.get_osm(dirname, city, simplify, tolerance, plot_osm)

    # Get and plot GTFS layer
    if pt == 'y':
        gtfs_layer.download_store_gtfs(url, city, dirname, gtfs_edges_path, gtfs_nodes_path, stop_times_path)

    # Get additional information on region layer
    if ad == 'y' and not country == 'US':
        # Gets "Statistische Quartiere" for Zurich and adds further info to each region
        geomdf = region_info_layer.get_geom(dirname, city)

        # Map each node to a geograpic region
        osm_nodes = region_info_layer.get_geo_node(osm_nodes, geomdf)
        if osm_nodes == 0:
            print('Please add additional informations to folder and run app again')
            return
    if ad == 'y' and country == 'US':
        # Gets "census tracts" for city object in US and adds further info to each region
        geomdf = region_info_layer.get_geom_us(dirname, city, county, state)
        print(geomdf)
        # Map each node to a geograpic region
        osm_nodes = region_info_layer.get_geo_node_us(dirname, osm_nodes, state, county)
        print(osm_nodes)
        # Add speed-limit to each edge and
        # calculate time it takes to travel on road-segment.
        #osm_edges = region_info_layer.get_speed_time(osm_edges)

    if parking == 'y':
        # Add number of parking spots available at each edge
        osm_edges = region_info_layer.get_parking(osm_edges, dirname, city)

    osm_edges.to_csv(osm_edges_path)



