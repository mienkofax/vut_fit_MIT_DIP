#!/usr/bin/env python3

from os.path import dirname, abspath, join
import sys

THIS_DIR = dirname(__file__)
CODE_DIR = abspath(join(THIS_DIR, '../..', ''))
sys.path.append(CODE_DIR)

import env_dp.core as dp
import logging


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    client = dp.BeeeOnClient("ant-work.fit.vutbr.cz", 8010, cache=True)
    client.api_key = dp.api_key(CODE_DIR + '/api_key.config')

    storage = dp.DataStorage(client, dp.WeatherData(cache=True))
    storage.read_meta_data('../devices_klarka.json', '../events_klarka.json')

    dw1 = storage.download_data_for_normalization(['temperature_in'])
    dw2 = storage.download_data_for_normalization(['humidity_in'])
    dw3 = storage.download_data_for_normalization(['temperature_out'])
    dw4 = storage.download_data_for_normalization(['humidity_out'])

    dw1_filtered, dw2_filtered, dw3_filtered, dw4_filtered = \
        storage.filter_downloaded_data(dw1, dw2, dw3, dw4, 07.0, 100.0, 5.0, 100.0)

    client.logout()

    his_data = dp.gen_histogram(dw2_filtered, 10, 10, 70, 2, 'value')
    histograms = dp.gen_histogram_graph(his_data)

    g = dp.Graph("./../../src/graph")
    g.gen(histograms, 'test_g.html', 0, 0, 'bar')