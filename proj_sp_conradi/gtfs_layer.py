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
import peartree as pt
from shapely.geometry import Point, shape
from collections import OrderedDict
from proj_sp_conradi import utils

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
    print('Copy and past feed URL you want to get:')
    zip_url = input()
    while not utils.valid_url_input(zip_url, urls):
        print('Invalid URL, please try again:')
        zip_url = input()
    return zip_url
