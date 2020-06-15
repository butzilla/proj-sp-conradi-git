# -----------------------------------------------------------
# This module works as a interactive UI for getting and
# storing data sets.
#
#
# Johannes Conradi, 2020 ETH Zuerich
# email: conradij@ethz.ch
# -----------------------------------------------------------

import os
from proj_sp_conradi import osm_layer
from proj_sp_conradi import gtfs_layer
from proj_sp_conradi import region_info_layer
from proj_sp_conradi import utils
from proj_sp_conradi import demand_layer
import censusdata
import pprint
import pandas as pd
import json
import zipfile


def run():
    """
    This function dictates the control flow of the app. It first gets all the necessary information from the user and
    then collects the data.
    """
    # Directory
    dirname = os.path.dirname(__file__)
    # List of possible cities
    countries = ['Switzerland', 'US']
    demand_file = pd.read_csv(dirname+'/cities_with_demand.json')
    with open('/Users/johannesconradi/proj-sp-conradi-git/proj_sp_conradi/cities_with_demand.json') as json_file:
        demand_file = json.load(json_file)
    cities_with_demand = demand_file['Cities']
    #print(cities_with_demand)

    ### Start of user interaction ###

    # Introduction in app and city selection
    print('Dear user, thanks for using this app! You can generate standardized mobility data sets of a specific city'
          'In the following you can choose whether to add different layers to the data sets. There are 4 layers in total.'
          'OSM street layer, GTFS public transport, additional information for specific region and demand layer.'
          'Please start with choosing a country: (US/Switzerland)')
    country = input()
    while not utils.valid_city_input(country, countries):
        print('Country not list, please choose a different city:')
        country = input()
    print('Please choose a city in ' + country)
    city = input()
    print('Do you want to continue with '+ city +'? (y/n)')
    cont = input()
    while not cont == 'y':
        print('Please type in new city:')
        city = input()
        print('Do you want to continue with ' + city + '? (y/n)')
        cont = input()

    # OSM layer user interaction
    print('-------------------------------- \n'
          '*****OSM Street Layer*****\nDo you want to get OSM graph? (y/n)')
    osm = input()
    while not utils.valid_yn_input(osm):
        print('Wrong input, try again:')
        osm = input()
    if osm == 'y':
        print('Do you want to simplify the OSM graph? If the graph is simplified there will be no OSM IDs per node anymore'
              '(y/n)')
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
    print('-------------------------------- \n'
          '*****GTFS Public Transport Layer*****\nDo you want to get public transport layer? (y/n)')
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
    if country == 'US':
        print('-------------------------------- \n'
              '*****Addtional Information Layer*****\nDo you want to get additional information on region layer? The default '
          'informations for the US are population, income $/year and housing value. (y/n)')
    if country == 'Switzerland':
        print('-------------------------------- \n'
              '*****Addtional Information Layer*****\nDo you want to get additional information on region layer? The default '
          'informations for Switzerland are income, population and housing prices (y/n)')
    ad = input()
    while not utils.valid_yn_input(pt):
        print('Wrong input, try again:')
        ad = input()
    if ad == 'y':
        if not city == 'Zurich' and not country == 'US':
            print("If you want to get additional informations for "+city+" please add the information to the folder "
                                                     "/resources/additional_info in the same format as shown on the "
                                                     "example of Zurich")
        if country == 'US':
            print('Do you know state and county nr. of your city for asc5 2015? (Example Chicago: State=17 and County='
                  '031)? (y/n)')
            state_county = input()
            if state_county == 'n':
                print('List of states:')
                pprint.pprint(censusdata.geographies(censusdata.censusgeo([('state', '*')]), 'acs5', 2015))
                print('Please provide the state nr. of ' + city + ' (Example Chicago, Illinois: 17)')
                state = input()
                print('List of counties for state ' + state)
                pprint.pprint(censusdata.geographies(censusdata.censusgeo([('state', state), ('county', '*')]), 'acs5', 2015))
                print('Please also provide the county nr. of ' + city + ' (Example Chicago, Cook County, Illinois: 031)')
                county = input()
            else:
                print('Please provide the state nr. of ' + city + ' (Example Chicago: 17)')
                state = input()
                print('Please also provide the county nr. of ' + city + ' (Example Chicago: 031)')
                county = input()
            shapepath = dirname + '/resources/additional_info/state_' + state
            while not os.path.isdir(shapepath):
                print('Please download the tract shapefile for the given state from here: '
                      'https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.2015.html and unzip '
                      'the folder. Move it to the directory: /resources/additional_info and rename to state_' + state)
                print('Have you done that and want to continue? (y)?')
                cont1 = input()
                while not utils.valid_yn_input(cont1):
                    print('Wrong input, try again:')
                    cont1 = input()
            print('Do you want to add further information other then the default ones? (y/n)')
            fad = input()
            while not utils.valid_yn_input(fad):
                print('Wrong input, try again:')
                fad = input()
            if fad == 'y':
                print('Please visit https://api.census.gov/data/2015/acs/acs5/variables.html and search for your '
                      'desired variables. You can input the variables here comma-separated: (example B03002_017E,'
                      'B03002_018E,B03002_016E...)')
                var = input()
                print('Do you want to continue with: '+ var +'? (y/n)')
                cont2 = input()
                while not cont2 == 'y':
                    print('Please type variables again:')
                    var = input()
                    print('Do you want to continue with: '+ var +'? (y/n)')
                    cont2 = input()
            else:
                var = []
    # Parking user interaction
    if country == 'Switzerland':

        print('Do you want to add parking spots to road segments (y/n)')
        parking = input()
        while not utils.valid_yn_input(parking):
            print('Wrong input, try again:')
            parking = input()
        if parking == 'y' and not city == 'Zurich':
            print("If you want to get parking for "+city+" please add the information to the folder "
                                                         "/resources/additional_info in the same format as shown on the "
                                                         "example of Zurich")
    else:
        parking = 'n'

    # Demand layer user interaction
    print('-------------------------------- \n'
          '*****Demand Layer*****\nDo you want to get information on where to get demand data for ' + city + '? (y/n)')
    demand = input()
    while not utils.valid_yn_input(demand):
        print('Wrong input, try again:')
        demand = input()
    if demand == 'y':
        if not utils.valid_city_input(city,cities_with_demand):
            print('Unfortunately, we do not have any demand information on '+ city +'.Do you have demand informations and '
                                                                                    'want to add it? (y/n)')
            demand_add = input()
            while not utils.valid_yn_input(demand_add):
                print('Wrong input, try again:')
                demand_add = input()
            if demand_add == 'y':
                print('If you have demand informations please copy and past link in the following:')
                link = input()
                demand_file['Cities'].append(city)
                demand_file.update({city: link})
                with open('/Users/johannesconradi/proj-sp-conradi-git/proj_sp_conradi/cities_with_demand.json',
                          'w') as outfile:
                    json.dump(demand_file, outfile)
        if utils.valid_city_input(city, cities_with_demand):
            print('We have found following links for the demand layer:')
            print(demand_file[city])
            if country == 'US':
                print('Please download demand data in csv format, name the file demand_' +city+ '.csv and move it to '
                        '/resources/demand_layer. You should also make sure that there are the following four columns '
                        'with exact naming: 1)Pickup Centroid Latitude 2)Pickup Centroid Longitude 3)Dropoff Centroid '
                        'Latitude 4)Dropoff Centroid Longitude. Have you done that?(y)')
                cont3 = input()
                while not utils.valid_yn_input(cont3):
                    print('Will not continue until you confirm with y:')
                    cont3 = input()
                print('Do you want to map the origin destination coordinate pair to a OSM node? Please be aware that '
                      'this may take some time...(y/n)?')
                osm_mapping = input()
                while not utils.valid_yn_input(osm_mapping):
                    print('Wrong input, try again:')
                    osm_mapping = input()

            if country == 'Switzerland':
                print(
                    'Please download demand data, name the file demand_' + city + '.txt and move it to'
                    ' /output. Each street layer will get an additional column (demand_layer_region_id) that maps each '
                    ' node to a region that are used in the data that you will download. Once you have downloaded the'
                                                                                  'data press: y.')
                cont3 = input()
                while not utils.valid_yn_input(cont3):
                    print('Will not continue until you confirm with y:')
                    cont3 = input()



    print('-------------------------------- \nEnd of user interaction. Will start processing data now. Sit back and '
          'relax ;)')

    ### End of user interaction ###

    # Directories
    osm_eges_filename = 'osm_edges_' + city + '.csv'
    osm_nodes_filename = 'osm_nodes_' + city + '.csv'
    geom_filename = 'geom_' + city + '.csv'
    gtfs_eges_filename = 'gtfs_edges_' + city + '.csv'
    gtfs_nodes_filename = 'gtfs_nodes_' + city + '.csv'
    gtfs_stop_times_filename = 'gtfs_stop_times_' + city + '.csv'
    demand_filename = 'demand_w_osmid' + city + '.csv'
    output_path = os.path.join(dirname, 'output')
    osm_edges_path = os.path.join(output_path, osm_eges_filename)
    osm_nodes_path = os.path.join(output_path, osm_nodes_filename)
    gtfs_edges_path = os.path.join(output_path, gtfs_eges_filename)
    gtfs_nodes_path = os.path.join(output_path, gtfs_nodes_filename)
    stop_times_path = os.path.join(output_path, gtfs_stop_times_filename)
    geom_filename_path = os.path.join(output_path, geom_filename)
    demand_path = os.path.join(output_path, demand_filename)

    # Get and plot osm layer
    if osm == 'y':
        osm_nodes, osm_edges = osm_layer.get_osm(dirname, city, simplify, tolerance, plot_osm)
        osm_edges.to_csv(osm_edges_path)
        osm_nodes.to_csv(osm_nodes_path)

    # Get and plot GTFS layer
    if pt == 'y':
        gtfs_layer.download_store_gtfs(url, city, dirname, gtfs_edges_path, gtfs_nodes_path, stop_times_path)

    # Get additional information on region layer
    if ad == 'y' and not country == 'US':
        # Gets "Statistische Quartiere" for Zurich and adds further info to each region
        geomdf = region_info_layer.get_geom(dirname, city)
        geomdf.to_csv(geom_filename_path)
        # Map each node to a geograpic region
        osm_nodes = region_info_layer.get_geo_node(osm_nodes, geomdf, simplify)
        osm_nodes.to_csv(osm_nodes_path)
        if osm_nodes == 0:
            print('Please add additional informations to folder and run app again')
            return
    if ad == 'y' and country == 'US':
        # Gets "census tracts" for city object in US and adds further info to each region
        geomdf = region_info_layer.get_geom_us(dirname, city, county, state, var)
        geomdf.to_csv(geom_filename_path)
        # Map each node to a geograpic region
        osm_nodes = region_info_layer.get_geo_node_us(dirname, osm_nodes, state, county, simplify)
        osm_nodes.to_csv(osm_nodes_path)
        # Add speed-limit to each edge and
        # calculate time it takes to travel on road-segment.
        #osm_edges = region_info_layer.get_speed_time(osm_edges)

    if parking == 'y':
        # Add number of parking spots available at each edge
        osm_edges = region_info_layer.get_parking(osm_edges, dirname, city)
        osm_edges.to_csv(osm_edges_path)

    if demand == 'y' and not country == 'Switzerland':
        demand_df = demand_layer.get_demand_trip(dirname, city, osm_nodes, osm_mapping)
        demand_df.to_csv(demand_path)
    if demand == 'y' and country == 'Switzerland':
        # Only for Kanton ZH
        osm_nodes = demand_layer.map_osm_demandgeo(dirname, osm_nodes)
        osm_nodes.to_csv(osm_nodes_path)
    print('Done processing data.')



