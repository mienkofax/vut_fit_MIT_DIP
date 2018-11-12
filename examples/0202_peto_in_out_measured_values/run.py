#!/usr/bin/env python3

from os.path import dirname, abspath, join
import sys

THIS_DIR = dirname(__file__)
CODE_DIR = abspath(join(THIS_DIR, '../..', ''))
sys.path.append(CODE_DIR)

import env_dp.core as dp
import logging
import datetime
import numpy as np
from scipy.optimize import curve_fit


def gen_emission(activities):
    emissions = 0

    for activity in activities.split(','):
        activity = activity.strip()
        if 'kancelarska_praca' == activity:
            emissions += 19
        elif 'spanok' == activity:
            emissions += 10
        else:
            raise ValueError('neznama aktivita: ' + activity)

    return emissions


def fill_estimate(events, module_name, V, Q, co2_ppm_out):
    for i in range(0, len(events)):
        event = events[i]
        emissions = gen_emission(event['activity'])

        for j in range(0, len(event['data'][0]['values'])):
            module = event['data'][0]['values'][j]

            if module['custom_name'] != 'co2':
                continue

            for k in range(0, len(module['measured'])):
                value = module['measured'][k]

                if 'time_shift' in event and k <= event['time_shift']:
                    value[module_name] = module['measured'][0]['value']
                    continue

                if 'time_shift' in event:
                    value[module_name] = dp.UtilCO2.estimate_ppm(
                        (k - event['time_shift']) / 3600,
                        module['measured'][event['time_shift']]['value'],
                        co2_ppm_out,
                        V,
                        Q,
                        emissions)
                else:
                    value[module_name] = dp.UtilCO2.estimate_ppm(
                        k / 3600,
                        module['measured'][0]['value'],
                        co2_ppm_out,
                        V,
                        Q,
                        emissions)


def prepare_weka_files(events):
    file = open('co2_weka.arff', 'w')
    file.write('@relation events\n\n')

    class_name = 'graph_type'
    out = ''

    values = []
    for ev in events:
        m_protronix_temperature = dp.find_module_measured(ev, 'protronix_temperature')
        m_beeeon_temperature_out = dp.find_module_measured(ev, 'beeeon_temperature_out')
        m_protronix_humidity = dp.find_module_measured(ev, 'protronix_humidity')
        m_beeeon_humidity_out = dp.find_module_measured(ev, 'beeeon_humidity_out')

        precision = 2

        values = [
            ('people', ev['people']),
            ('wind', ev['wind']),
            ('sky', ev['sky']),
            ('slnko', ev['sun']),
            ('teplota_dnu', round(m_protronix_temperature[0]['value'], precision)),
            ('teplota_von', round(m_beeeon_temperature_out[0]['value'], precision)),
            ('rozdiel_teplot', round(abs(
                m_beeeon_temperature_out[0]['value'] - m_protronix_temperature[0]['value']),
                                     precision)),

            ('rh_dnu', round(m_protronix_humidity[0]['value'], precision)),
            ('rh_von', round(m_beeeon_humidity_out[0]['value'], precision)),
            ('rozdiel_rh',
             round(abs(m_protronix_humidity[0]['value'] - m_beeeon_humidity_out[0]['value']),
                   precision)),

            ('abs_rh_dnu', round(m_protronix_humidity[0]['absolute_humidity'], precision)),
            ('abs_rh_von', round(m_beeeon_humidity_out[0]['absolute_humidity'], precision)),
            ('rozdiel_abs_rh', round(abs(
                m_protronix_humidity[0]['absolute_humidity'] - m_beeeon_humidity_out[0][
                    'absolute_humidity']), precision)),

            ('spec_rh_dnu', round(m_protronix_humidity[0]['specific_humidity'], precision)),
            ('spec_rh_von', round(m_beeeon_humidity_out[0]['specific_humidity'], precision)),
            ('rozdiel_spec_rh', round(abs(
                m_protronix_humidity[0]['specific_humidity'] - m_beeeon_humidity_out[0][
                    'specific_humidity']), precision)),
            (class_name, ev['graph_type']),
        ]

        for i in range(0, len(values)):
            value = values[i]

            out += str(value[1])

            if i != len(values) - 1:
                out += ','

        out += "\n"

    for item, _ in values:
        if item == class_name:
            file.write('@attribute class {exponential, linear, uneven}\n')
            continue

        file.write('@attribute %s numeric\n' % item)

    file.write('\n')
    file.write('@data\n\n')

    file.write('%s' % out)
    file.close()


def gen_f_variant0(co2_start, co2_out):
    return lambda x, a: co2_out + (co2_start - co2_out) * np.exp(-a * x)


def gen_f_variant1(co2_start, co2_out, volume):
    return lambda x, a: co2_out + (co2_start - co2_out) * np.exp(-a / volume * x)


def gen_f_variant2(co2_start):
    return lambda x, a, b: b + (co2_start - b) * np.exp(-a * x)


# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
def exp_regression(events, co2_out, volume):
    for i in range(0, len(events)):
        event = events[i]

        for j in range(0, len(event['data'][0]['values'])):
            module = event['data'][0]['values'][j]

            if module['custom_name'] != 'co2':
                continue

            x = []
            y = []

            for k in range(event['time_shift'], len(module['measured'])):
                value = module['measured'][k]

                x.append(k - event['time_shift'])
                y.append(value['value'])

            x = np.asarray(x)
            y = np.asarray(y)

            f_0 = gen_f_variant0(module['measured'][0]['value'], co2_out)
            popt_0, pcov_0 = curve_fit(f_0, x, y)

            f_1 = gen_f_variant1(module['measured'][0]['value'], co2_out, volume)
            popt_1, pcov_1 = curve_fit(f_1, x, y)

            f_2 = gen_f_variant2(module['measured'][0]['value'])
            popt_2, pcov_2 = curve_fit(f_2, x, y, maxfev=1500)

            event['exp_reg'] = {
                'variant_0':
                    {
                        'a': tuple(popt_0)[0],
                        # co2_out + (co2_start - co2_out) * np.exp(-a * x)
                        'eq': str(co2_out) + ' + (' + str(
                            module['measured'][0]['value']) + ' - ' + str(
                            co2_out) + ') * exp(-' + str(tuple(popt_0)[0]) + ' * x)',
                    },
                'variant_1':
                    {
                        'a': tuple(popt_1)[0],
                        # co2_out + (co2_start - co2_out) * np.exp(-a / volume * x)
                        'eq': str(co2_out) + ' + (' + str(
                            module['measured'][0]['value']) + ' - ' + str(
                            co2_out) + ') * exp(-(' + str(
                            tuple(popt_1)[0]) + ') / ' + str(volume) + ' * x)',
                    },
                'variant_2':
                    {
                        'a': tuple(popt_2)[0],
                        'b': tuple(popt_2)[1],
                        # b + (co2_start - b) * np.exp(-a * x)
                        'eq': str(tuple(popt_2)[1]) + ' + (' + str(
                            module['measured'][0]['value']) + ' - ' + str(
                            tuple(popt_2)[1]) + ') * exp(-' + str(
                            tuple(popt_2)[0]) + ' * x)',
                    }
            }

            for k in range(0, len(module['measured'])):
                value = module['measured'][k]

                if k < event['time_shift']:
                    value['exp_reg_v1'] = value['value']
                    value['exp_reg_v2'] = value['value']
                    continue

                t = k - event['time_shift']

                value['exp_reg_v1'] = f_1(t, event['exp_reg']['variant_1']['a'])
                value['exp_reg_v2'] = f_2(t,
                                          event['exp_reg']['variant_2']['a'],
                                          event['exp_reg']['variant_2']['b'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    client = dp.BeeeOnClient("ant-work.fit.vutbr.cz", 8010, cache=True)
    client.api_key = dp.api_key(CODE_DIR + '/api_key.config')

    storage = dp.DataStorage(client, dp.WeatherData(cache=True), cache=False)
    storage.read_meta_data('../devices_peto.json', '../events_peto.json')

    modules = [
        'co2',
        'protronix_temperature',
        'protronix_humidity',
        'beeeon_temperature_out',
        'beeeon_humidity_out',
    ]
    all = storage.download_data_for_normalization(modules)

    # vystrihnutie prvych 10 minut
    all = dp.cut_events(all, 0, 604)

    # zobrazenie grafov, ktore obsahuju prave tych 10 minut
    all = dp.filter_number_events(all, 604)

    norm = storage.filter_general_attribute_value(all, 'out_sensor', 'yes')

    norm = dp.convert_relative_humidity_to_absolute_humidity(norm, 'protronix_temperature', 'protronix_humidity')
    norm = dp.convert_relative_humidity_to_absolute_humidity(norm, 'beeeon_temperature_out', 'beeeon_humidity_out')

    norm = dp.convert_relative_humidity_to_specific_humidity(norm, 'protronix_temperature', 'protronix_humidity')
    norm = dp.convert_relative_humidity_to_specific_humidity(norm, 'beeeon_temperature_out', 'beeeon_humidity_out')

    norm = dp.norm_all(norm)

    dp.UtilCO2.generate_time_shift(norm, 10, 10)
    fill_estimate(norm, "odhad1", 48, 500, 460)

    exp_regression(norm, 500, 48)
    prepare_weka_files(norm)

    one_norm_graph = []
    graphs = []

    for i in range(0, len(norm)):
        ev = norm[i]
        co2 = dp.filter_one_values(norm[i], 'co2')
        protronix_temperature = dp.filter_one_values(norm[i], 'protronix_temperature')
        protronix_humidity = dp.filter_one_values(norm[i], 'protronix_humidity')
        beeeon_temperature_out = dp.filter_one_values(norm[i], 'beeeon_temperature_out')
        beeeon_humidity_out = dp.filter_one_values(norm[i], 'beeeon_humidity_out')

        abs_in = dp.filter_one_values(norm[i], 'protronix_humidity')
        abs_out = dp.filter_one_values(norm[i], 'beeeon_humidity_out')

        start = norm[i]['times']['event_start']
        end = norm[i]['times']['event_end']

        t = datetime.datetime.fromtimestamp(start).strftime('%d.%m. %H:%M:%S')
        t += ' - '
        t += datetime.datetime.fromtimestamp(end).strftime('%H:%M:%S')

        m_protronix_temperature = dp.find_module_measured(ev, 'protronix_temperature')
        m_beeeon_temperature_out = dp.find_module_measured(ev, 'beeeon_temperature_out')
        m_protronix_humidity = dp.find_module_measured(ev, 'protronix_humidity')
        m_beeeon_humidity_out = dp.find_module_measured(ev, 'beeeon_humidity_out')

        precision = 2

        stat = [
            ('description', ev['description']),
            ('graph_type', ev['graph_type']),
            ('people', ev['people']),
            ('wind', ev['wind']),
            ('obloha', ev['sky']),
            ('slnko', ev['sun']),
            ('', ''),
            ('teplota dnu', round(m_protronix_temperature[0]['value'], precision)),
            ('teplota von', round(m_beeeon_temperature_out[0]['value'], precision)),
            ('rozdiel teplot', round(abs(m_beeeon_temperature_out[0]['value'] - m_protronix_temperature[0]['value']), precision)),

            ('', ''),
            ('rh dnu', round(m_protronix_humidity[0]['value'], precision)),
            ('rh von', round(m_beeeon_humidity_out[0]['value'], precision)),
            ('rozdiel rh', round(abs(m_protronix_humidity[0]['value'] - m_beeeon_humidity_out[0]['value']), precision)),

            ('', ''),
            ('abs rh dnu', round(m_protronix_humidity[0]['absolute_humidity'], precision)),
            ('abs rh von', round(m_beeeon_humidity_out[0]['absolute_humidity'], precision)),
            ('rozdiel abs rh', round(abs(m_protronix_humidity[0]['absolute_humidity'] - m_beeeon_humidity_out[0]['absolute_humidity']), precision)),

            ('', ''),
            ('spec rh dnu', round(m_protronix_humidity[0]['specific_humidity'], precision)),
            ('spec rh von', round(m_beeeon_humidity_out[0]['specific_humidity'], precision)),
            ('rozdiel spec rh', round(abs(m_protronix_humidity[0]['specific_humidity'] - m_beeeon_humidity_out[0]['specific_humidity']), precision)),

            ('', ''),
            ('varianta0', ''),
            ('eq', ev['exp_reg']['variant_0']['eq']),
            ('a (intenzita vetrania [s<sup>-1</sup>])', round(ev['exp_reg']['variant_0']['a'], 6)),
            ('a (intenzita vetrania [h<sup>-1</sup>])', round(ev['exp_reg']['variant_0']['a'] * 3600, precision)),

            ('', ''),
            ('varianta1', ''),
            ('eq', ev['exp_reg']['variant_1']['eq']),
            ('a (velkost vymeny vzduchu [m<sup>3</sup>/s])', round(ev['exp_reg']['variant_1']['a'], 6)),
            ('a (velkost vymeny vzduchu [m<sup>3</sup>/hs])', round(ev['exp_reg']['variant_1']['a'] * 3600, precision)),

            ('', ''),
            ('varianta2', ''),
            ('eq', ev['exp_reg']['variant_2']['eq']),
            ('a (intenzita vetrania [s<sup>-1</sup>])', round(ev['exp_reg']['variant_2']['a'], 6)),
            ('a (intenzita vetrania [h<sup>-1</sup>])', round(ev['exp_reg']['variant_2']['a'] * 3600, precision)),
            ('b (vonkajcia koncentracia CO2 [ppm])', round(ev['exp_reg']['variant_2']['b'], precision)),
        ]

        g = {
            'title': 'CO2 in: ' + t,
            'stat': stat,
            'graphs': [
                dp.gen_simple_graph(co2, 'blue', 'CO2 in', 'value', 100),
                dp.gen_simple_graph(co2, 'red', 'Odhad CO2 in', 'odhad1', 100),
                dp.gen_simple_graph(co2, 'green', 'Exp reg. v1', 'exp_reg_v1', 100),
                dp.gen_simple_graph(co2, 'orange', 'Exp reg. v2', 'exp_reg_v2', 100),
            ]
        }
        graphs.append(g)
        continue

        g = {
            'title': 'Abs humidity in/out: ' + t,
            'graphs': [
                dp.gen_simple_graph(abs_in, 'red', 'Humidity in', 'absolute_humidity', 50),
                dp.gen_simple_graph(abs_out, 'blue', 'Humidity out', 'absolute_humidity', 50),
            ]
        }
        graphs.append(g)

        g = {
            'title': 'Humidity in/out: ' + t,
            'graphs': [
                dp.gen_simple_graph(co2, 'blue', 'CO2 in', 'value_norm', 50),
                dp.gen_simple_graph(protronix_temperature, 'red', 'Temperature in', 'value_norm', 50),
                dp.gen_simple_graph(protronix_humidity, 'orange', 'Humidity in', 'value_norm', 50),
                dp.gen_simple_graph(abs_in, 'green', 'Humidity in abs', 'absolute_humidity_norm', 50),
                dp.gen_simple_graph(abs_out, 'black', 'Humidity out abs', 'absolute_humidity_norm', 50),
            ]
        }
        graphs.append(g)

    print('number of events: %d' % len(norm))

    g = dp.Graph("./../../src/graph")
    g.gen(graphs, 'test_g.html', 0, 0)