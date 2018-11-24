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
    client.api_key = dp.api_key(CODE_DIR + '/config.ini')

    storage = dp.DataStorage(client, dp.WeatherData(cache=True))
    storage.read_meta_data('../devices_examples.json', '../events_examples.json')

    dw1 = storage.download_data_for_normalization(['co2'])
    dw1 = dp.cut_events(dw1, 0, 300)
    dw1 = dp.filter_number_events(dw1, 300)

    norm = dp.norm_all(dw1)

    one_norm_graph = []
    graphs = []

    for i in range(0, len(dw1)):
        values = dp.filter_one_values(norm[i], 'co2')

        norm_graph = dp.gen_simple_graph(values, dp.COLORS[i], 'Namerana hodnota', 'value_norm')
        one_norm_graph.append(norm_graph)

        g = {
            'title': 'Measured values',
            'graphs': [
                dp.gen_simple_graph(values, 'green', 'Namerana hodnota', 'value')
            ]
        }

        graphs.append(g)

    graphs.append({
        'title': 'Measured values',
        'graphs': one_norm_graph
    })

    g = dp.Graph("./../../src/graph")
    g.gen(graphs, 'test_g.html', 0, 0)
