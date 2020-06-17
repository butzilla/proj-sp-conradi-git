# -----------------------------------------------------------
# This script provides functions for the GTFS interactions.
#
#
# Johannes Conradi, 2020 ETH Zuerich
# email: conradij@ethz.ch
# -----------------------------------------------------------

import os
import requests
from shapely.geometry import Point, shape
from collections import OrderedDict
from proj_sp_conradi import utils

import urbanaccess as ua
from urbanaccess.gtfsfeeds import feeds
from urbanaccess import gtfsfeeds

# Pandana currently uses depreciated parameters in matplotlib, this hides the warning until its fixed
import warnings
import matplotlib.cbook
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

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

"""
def get_gtfs(city, zip_url, plot):
    td = tempfile.mkdtemp()
    path = os.path.join(td, 'mta_bk.zip')

    resp = requests.get(zip_url)
    open(path, 'wb').write(resp.content)

    print('Downloading GTFS feed..')
    # Automatically identify the busiest day and
    # read that in as a Partidge feed
    feed = pt.get_representative_feed(path)

    # Set a target time period to
    # use to summarize impedance
    start = 7 * 60 * 60  # 7:00 AM
    end = 10 * 60 * 60  # 10:00 AM

    # Converts feed subset into a directed
    # network multigraph
    G = pt.load_feed_as_graph(feed, start, end)

    if plot:
        pt.generate_plot(G)
    return G
"""
def download_store_gtfs(url, city, dirname, gtfs_edges_path, gtfs_nodes_path, stop_times_path, plot, path_fig_gtfs):
    folder_path = 'resources/gtfs_feed'
    folder_path_text = 'resources/gtfs_feed/gtfsfeed_text/' + city
    download_path = os.path.join(dirname, folder_path)
    text_path = os.path.join(dirname, folder_path_text)
    feeds.add_feed(add_dict={city: url})
    gtfsfeeds.download(data_folder=download_path)

    stop_times = False
    loaded_feeds = ua.gtfs.load.gtfsfeed_to_df(gtfsfeed_path=text_path)
    ua.gtfs.network.create_transit_net(gtfsfeeds_dfs=loaded_feeds,
                                       day='monday',
                                       timerange=['07:00:00', '10:00:00'],
                                       calendar_dates_lookup=None)
    urbanaccess_net = ua.network.ua_network
    edges = urbanaccess_net.transit_edges
    edges['geometry'] = 'NA'
    edges['lanes'] = 'NA'
    edges = edges[
        ['node_id_from', 'node_id_to', 'geometry', 'route_type', 'lanes', 'weight', 'unique_trip_id', 'unique_route_id',
         'net_type']]
    headways = ua.gtfs.headways.headways(loaded_feeds, ['07:00:00', '10:00:00'])
    nodes = urbanaccess_net.transit_nodes
    nodes = nodes[['x', 'y']]
    headways = headways.headways[['mean', 'unique_stop_id', 'unique_route_id']]
    headways = headways.set_index('unique_stop_id')
    nodes = nodes.join(headways)
    nodes = nodes.rename(columns={"mean": "headways_mean"})
    nodes = nodes.drop_duplicates()
    edges.to_csv(gtfs_edges_path)
    nodes.to_csv(gtfs_nodes_path)

    if plot:
        fig, ax = ua.plot.plot_net(nodes=urbanaccess_net.transit_nodes,
                                edges=urbanaccess_net.transit_edges)
        plt.savefig(path_fig_gtfs)

    if stop_times:
        stop_times = loaded_feeds.stop_times
        stop_times.to_csv(stop_times_path)


def get_gtfs_url(city):
    print('Looking on https://transit.land/api for possible GTFS feeds for ' + city)
    base_link = 'https://transit.land/api/v1/feeds?bbox='
    city_bbox = nominatim_query(city).bounds
    query_link = base_link + str(city_bbox[0]) + ',' + str(city_bbox[1]) + ',' + str(city_bbox[2]) + ',' + str(
        city_bbox[3])

    # Possible feeds
    resp = requests.get(query_link)
    resp_json = resp.json()
    feeds = resp_json['feeds']
    print('Found following feeds:')
    urls = []
    for f in resp_json['feeds']:
        urls.append(f['url'])
        print(f['url'])
    print('Do you want to get one of those feeds? (y/n)')
    get = input()
    while not utils.valid_yn_input(get):
        print('Wrong input, try again:')
        get = input()
    if get == 'y':
        print('Copy and past feed URL you want to get:')
        zip_url = input()
        while not utils.valid_url_input(zip_url, urls):
            print('Invalid URL, please try again:')
            zip_url = input()
        return zip_url
    else:
        print('Then please enter your own zip url:')
        return input()




