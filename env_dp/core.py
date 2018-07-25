import copy
import datetime
import hashlib
import http.client
import json
import logging
import os
import requests
import ssl


class HTTPClient:
    """Simple http client."""

    def __init__(self, host, port, end_point, method, verify_ssl_cert=True):
        self.__host = host
        self.__port = port
        self.__method = method
        self.__end_point = end_point
        self.__headers = {}
        self.__body = None
        self.__verify_ssl_cert = verify_ssl_cert

    def __setitem__(self, key, value):
        self.__headers[key] = value

    def __getitem__(self, key):
        return self.__headers[key]

    def __delitem__(self, key):
        del self.__headers[key]

    def body(self, body):
        self.__body = body

    def authorize(self, session_id):
        self.__headers['Authorization'] = 'Bearer ' + session_id

    def perform(self):
        if self.__verify_ssl_cert:
            conn = http.client.HTTPSConnection(self.__host, self.__port, timeout=10)
        else:
            conn = http.client.HTTPSConnection(self.__host, self.__port,
                                               context=ssl._create_unverified_context(),
                                               timeout=10)

        conn.request(self.__method, self.__end_point,
                     headers=self.__headers, body=self.__body)

        response = conn.getresponse()
        content = str(response.read(), 'utf-8')
        conn.close()
        return response, content


class BeeeOnClient:
    """Client for communication with server supporting BeeeOn api."""

    def __init__(self, host, port, cache=True, cache_folder='cache'):
        self.__host = host
        self.__port = port
        self.__api_key = ""
        self.__token_id = ""
        self.__cache_folder = cache_folder
        self.__cache = cache
        self.__log = logging.getLogger(self.__class__.__name__)

        if cache:
            if not os.path.exists(cache_folder):
                os.makedirs(cache_folder)

    def refresh_token(self):
        data = {'key': self.__api_key, 'provider': 'apikey'}
        try:
            req = HTTPClient(self.__host, self.__port, "/auth", "POST", False)
            req.body(json.dumps(data))
            res, body = req.perform()
        except Exception as e:
            self.__log.error(e)
            return

        json_res = json.loads(body)

        if 'code' not in json_res:
            raise LookupError('return code not found')

        if int(json_res['code']) != 200:
            self.__log.warning("invalid token_id")
            exit(1)
            return

        return json_res['data']['id']

    def sensors_info(self, gateway_id, device_id):
        if not self.__token_id:
            self.__token_id = self.refresh_token()

        endpoint = '/gateways/' + str(gateway_id) + '/devices/' + str(
            device_id) + '/sensors'

        h = hashlib.sha256()
        h.update(endpoint.encode("utf8"))
        filename = self.__cache_folder + '/cache_sensor_info_' + h.hexdigest()

        if os.path.isfile(filename) and self.__cache:
            self.__log.debug('from cache: sensor_info, %s, %s' % (gateway_id, device_id))
            with open(filename) as f:
                for line in f:
                    return json.loads(line.strip())

        req = HTTPClient(self.__host, self.__port, endpoint, "GET", False)
        req.authorize(self.__token_id)

        res, body = req.perform()

        if self.__cache:
            file = open(filename, 'w')
            file.write(json.dumps(json.loads(body)['data']))
            file.close()

        return json.loads(body)['data']

    def history(self, gateway, device, sensor, start, end, interval=1, aggregation='avg'):
        if not self.__token_id:
            self.__token_id = self.refresh_token()

        endpoint = '/gateways/' + gateway
        endpoint += '/devices/' + device
        endpoint += '/sensors/' + str(sensor)
        endpoint += '/history'
        endpoint += '?range=' + str(start) + ',' + str(end)
        endpoint += '&interval=' + str(interval)
        endpoint += '&aggregation=' + aggregation

        h = hashlib.sha256()
        h.update(endpoint.encode("utf8"))
        filename = self.__cache_folder + '/cache_history_' + h.hexdigest()

        if os.path.isfile(filename) and self.__cache:
            self.__log.debug('from cache: history, %s, %s, %s, %s - %s' % (
                gateway, device, sensor, start, end))
            with open(filename) as f:
                for line in f:
                    return json.loads(line.strip())

        req = HTTPClient(self.__host, self.__port, endpoint, "GET", False)
        req.authorize(self.__token_id)

        res, body = req.perform()

        if self.__cache:
            file = open(filename, 'w')
            file.write(body)
            file.close()

        return json.loads(body)

    def logout(self):
        if not self.__token_id:
            return

        endpoint = '/auth'

        req = HTTPClient(self.__host, self.__port, endpoint, "DELETE", False)
        req.authorize(self.__token_id)

        req.perform()

    @property
    def api_key(self):
        return self.__api_key

    @api_key.setter
    def api_key(self, key):
        self.__api_key = key


class WeatherData:
    """Weather data extraction from weather.com."""

    def __init__(self, precision=1, cache=True, cache_folder='cache'):
        self.__precision = precision
        self.__cache = cache
        self.__cache_folder = cache_folder
        self.__log = logging.getLogger(self.__class__.__name__)

        if cache:
            if not os.path.exists(cache_folder):
                os.makedirs(cache_folder)

    def __download_data(self, start, end):
        day_time_start = datetime.datetime.fromtimestamp(start).strftime('%Y%m%d %H:%M:%S')
        day_start = day_time_start[:-9]
        day_time_end = datetime.datetime.fromtimestamp(end).strftime('%Y%m%d %H:%M:%S')
        day_end = day_time_end[:-9]

        url = 'https://api.weather.com/v1/geocode/49.15139008/16.69388962/observations/'
        url += 'historical.json?apiKey=6532d6454b8aa370768e63d6ba5a832e'
        url += '&startDate=' + str(day_start) + '&endDate=' + str(day_end)

        h = hashlib.sha256()
        h.update(url.encode("utf8"))
        filename = self.__cache_folder + '/cache_weather_' + h.hexdigest()

        if os.path.isfile(filename) and self.__cache:
            self.__log.debug('from cache: %s - %s' % (start, end))
            with open(filename) as f:
                for line in f:
                    return line.strip()

        json_data = requests.get(url).text

        if self.__cache:
            file = open(filename, 'w')
            file.write(json_data)
            file.close()

        return json_data

    def weather_data(self, start, end):
        json_data = self.__download_data(start, end)

        python_obj = json.loads(json_data)

        out_general = []
        for element in python_obj['observations']:
            out_general.append({
                'at': element['valid_time_gmt'],
                'temperature': element['temp'],
                'relative_humidity': element['rh'],
                'pressure': element['pressure'],
                'wind_speed': element['wspd']
            })

        generate_weather_data = self.__generate_weather_data(out_general)
        out_detailed = []

        for i in range(0, len(generate_weather_data)):
            weather = generate_weather_data[i]
            if weather['at'] < start or generate_weather_data[i]['at'] > end:
                continue

            out_detailed.append(generate_weather_data[i])

        return out_detailed

    def __generate_weather_data(self, out_general):
        out_detailed = []
        for i in range(0, len(out_general) - 1):
            temp_start = out_general[i]['temperature']
            temp_end = out_general[i + 1]['temperature']
            if temp_start - temp_end == 0:
                temp_increase = 0
            else:
                temp_diff = temp_end - temp_start
                temp_increase = temp_diff / 1800.0

            rh_start = out_general[i]['relative_humidity']
            rh_end = out_general[i + 1]['relative_humidity']
            if rh_start - rh_end == 0:
                rh_increase = 0
            else:
                rh_diff = rh_end - rh_start
                rh_increase = rh_diff / 1800.0

            pressure_start = out_general[i]['pressure']
            pressure_end = out_general[i + 1]['pressure']
            if pressure_start - pressure_end == 0:
                pressure_increase = 0
            else:
                pressure_diff = pressure_end - pressure_start
                pressure_increase = pressure_diff / 1800.0

            wspd_start = out_general[i]['wind_speed']
            wspd_end = out_general[i + 1]['wind_speed']
            if wspd_start - wspd_end == 0:
                wspd_increase = 0
            else:
                wspd_diff = wspd_end - wspd_start
                wspd_increase = wspd_diff / 1800.0

            temp = temp_start
            rh = rh_start
            pressure = pressure_start
            wind_speed = wspd_start
            for j in range(0, 1800):
                out_detailed.append({
                    'at': int(out_general[i]['at']) + j,
                    'temperature': round(float(temp), self.__precision),
                    'relative_humidity': round(float(rh), self.__precision),
                    'pressure': round(float(pressure), self.__precision),
                    'wind_speed': round(float(wind_speed), self.__precision),
                })
                temp = temp + temp_increase
                rh = rh + rh_increase
                pressure = pressure + pressure_increase
                wind_speed = wind_speed + wspd_increase

        return out_detailed


class DataStorage:
    def __init__(self, client, weather_client, precision=1):
        self.__client = client
        self.__meta_data = []
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__weather_client = weather_client
        self.__precision = precision

    def __parser_date(self, date):
        return datetime.datetime.strptime(date, "%Y/%m/%d %H:%M:%S").timestamp()

    def __download_sensor_modules(self, gateway, device):
        data = self.__client.sensors_info(gateway, device)

        out = []
        for sensor in data:
            out.append({
                'id': int(sensor['id']),
                'type_id': sensor['type_id']
            })

        return out

    def __requested_modules(self, gateway, device, sensors):
        supported_modules = self.__download_sensor_modules(gateway, device)

        out = []
        for sensor in sensors:
            found = False
            for supported_module in supported_modules:
                if sensor['id'] == supported_module['id']:
                    supported_module['custom_name'] = sensor['custom_name']
                    out.append(supported_module)
                    found = True
                    break

            if not found:
                self.__log.warning("module %s not supported" % sensor)

        return out

    def read_meta_data(self, devices, events):
        with open(devices) as f:
            j_devices = json.load(f)

        with open(events) as f:
            j_events = json.load(f)

        for event in j_events['events']:
            new = copy.deepcopy(event)
            new['times']['event_start'] = int(
                self.__parser_date(event['times']['event_start']))
            new['data'] = []
            del (new['devices'])

            types = ['event_start', 'no_event_start']

            for type_id in types:
                one_sensor = {
                    'type': type_id,
                    'weather': [],
                    'values': [],
                }

                for key, device in event['devices'].items():
                    for dev in j_devices['devices']:
                        if dev['id'] != key:
                            continue

                        sensors = self.__requested_modules(dev['gateway'], dev['device'],
                                                           dev['sensors'])

                        for event_device in device:
                            found = False
                            for sensor in sensors:
                                if event_device != sensor['custom_name']:
                                    continue

                                found = True
                                one_sensor['values'].append({
                                    'id': key,
                                    'measured': [],
                                    'module_id': sensor['id'],
                                    'custom_name': sensor['custom_name'],
                                    'type_id': sensor['type_id'],
                                    'gateway': dev['gateway'],
                                    'device': dev['device']
                                })
                                break

                            if not found:
                                self.__log.warning(
                                    'sensor %s not found in input files with devices'
                                    % event_device)

                new['data'].append(one_sensor)
            self.__meta_data.append(new)

    def download_data(self, shift_before, shift_after):
        out_json = copy.deepcopy(self.__meta_data)

        for event in out_json:
            for event_type in event['data']:
                e_start_before_timestamp = int(
                    float(event['times'][event_type['type']]) - shift_before)
                e_start_after_timestamp = int(
                    float(event['times'][event_type['type']]) + shift_after)

                event_type['weather'] = self.__weather_client.weather_data(
                    e_start_before_timestamp, e_start_after_timestamp)

                for module in event_type['values']:
                    if module['type_id'] == 'open_close':
                        if 'no_event_start' in event_type['type']:
                            module['measured'].append({
                                'at': event['times']['no_event_start'],
                                'value': '1.0'
                            })
                            continue

                    module['measured'] = self.__client.history(
                        module['gateway'],
                        module['device'],
                        module['module_id'],
                        e_start_before_timestamp,
                        e_start_after_timestamp
                    )['data']

        return out_json

    def __switch_value(self, value):
        if value == 1:
            return 0

        return 1

    def __generate_event_data(self, event):
        out = copy.deepcopy(event)
        out['values'] = []

        for item in event['values']:
            if len(item['measured']) <= 1:
                if item['type_id'] == 'open_close':
                    out['values'].append(item)
                    continue

                if len(item['measured']) == 0:
                    self.__log.debug(
                        'prazdne hodnoty v modulu: %s, skip' % item['custom_name'])
                    continue

                if len(item['measured']) == 1 and item['type_id'] != 'open_close':
                    self.__log.debug(
                        'len jedna hodnota v modulu: %s, skip' % item['custom_name'])
                    continue

            out_values = []
            for i in range(0, len(item['measured']) - 1):
                value_start = item['measured'][i]['value']
                value_end = item['measured'][i + 1]['value']

                if value_start is None or value_end is None:
                    continue

                value_start = float(item['measured'][i]['value'])
                value_end = float(item['measured'][i + 1]['value'])

                time_start = item['measured'][i]['at']
                time_end = item['measured'][i + 1]['at']

                if value_start - value_end == 0:
                    value_increase = 0
                else:
                    value_diff = value_end - value_start
                    value_increase = value_diff / (time_end - time_start)

                value = value_start
                for j in range(0, time_end - time_start):
                    out_values.append({
                        "at": time_start + j,
                        "value": round(value, self.__precision)
                    })
                    value = value + value_increase

            out_values.append({
                "at": item['measured'][len(item['measured']) - 1]['at'],
                "value": round(value, self.__precision)
            })

            item['measured'] = out_values
            out['values'].append(item)

        return out

    def __find_before_after_shift(self, events, event_type):
        shift_before = None
        shift_after = None

        for event in events:
            for data in event['data']:
                if data['type'] != event_type:
                    continue

                time = event['times'][event_type]
                for item in data['values']:
                    values_cnt = len(item['measured']) - 1
                    if len(item['measured']) <= 1 or item['type_id'] == "open_close":
                        continue

                    first = item['measured'][0]['at']
                    last = item['measured'][values_cnt]['at']
                    if shift_before is None:
                        shift_before = time - first
                    elif shift_before > time - first:
                        shift_before = time - first

                    if shift_after is None:
                        shift_after = last - time
                    elif last - time < shift_after:
                        shift_after = last - time

        return shift_before, shift_after

    def __cut_common_data(self, event, data, times):
        a, b = self.__find_before_after_shift(data, 'event_start')
        c, d = self.__find_before_after_shift(data, 'no_event_start')

        event = self.__generate_event_data(event)

        local_min = None
        local_max = None

        out = []
        for item in event['values']:
            measured_out = []

            if event['type'] == 'event_start':
                local_min = times['event_start'] - a
                local_max = times['event_start'] + b
            elif event['type'] == 'no_event_start':
                local_min = times['no_event_start'] - c
                local_max = times['no_event_start'] + d

            if item['type_id'] == "open_close":
                value = 0
                switch = True

                if event['type'] == 'no_event_start':
                    switch = False

                for timestamp in range(local_min, local_max + 1):
                    if timestamp >= item['measured'][0]['at'] and switch:
                        value = self.__switch_value(value)
                        switch = False

                    measured_out.append({
                        "at": timestamp,
                        "value": round(float(value), self.__precision)
                    })

                item['measured'] = measured_out
            else:
                measured_out = []
                for value in item['measured']:
                    if value['at'] < local_min or value['at'] > local_max:
                        continue

                    measured_out.append(value)

                item['measured'] = measured_out
            out.append(item)

        weather_out = []
        for item in event['weather']:
            if item['at'] < local_min or item['at'] > local_max:
                continue

            weather_out.append(item)

        event['values'] = out
        event['weather'] = weather_out

        return event

    def common_data(self, data):
        out = []
        for row in data:
            out_row = copy.deepcopy(row)
            out_row['data'] = []

            for event_type in row['data']:
                values = self.__cut_common_data(event_type, data, row['times'])
                out_row['data'].append(values)

            out.append(out_row)

        return out

    def __common_count(self, events, event_type):
        count_before = None
        count_after = None

        for event in events:
            for data in event['data']:
                if data['type'] != event_type:
                    continue

                local_before = 0
                local_after = 0
                for value in data['values'][0]['measured']:
                    if value['tag'] == 'before':
                        local_before += 1
                    elif value['tag'] == 'after':
                        local_after += 1
                    else:
                        print('skip')

                if count_before is None:
                    count_before = local_before
                else:
                    count_before = min(count_before, local_before)

                if count_after is None:
                    count_after = local_after
                else:
                    count_after = min(count_after, local_after)

        return count_before, count_after

    def set_no_event_time(self, no_event_start_time_shift):
        """
        Vytvorenie casovej znacky, kde sa event nevyskytoval. Znacka sa vytvori pre zaciatok a
        koniec eventu osobitne. Hodnoty pre zaciatok a koniec eventu sa vypocitaju posunom
        o zadanu hodnotu dopredu (kladna hodnota) alebo dozadu (zaporna hodnota). Dopredu je
        mysleny cas, ktory je vacsi ako aktualny.
        """

        for e in self.__meta_data:
            new_value = e['times']['event_start'] + no_event_start_time_shift
            e['times']['no_event_start'] = new_value

    @property
    def meta_data(self):
        return self.__meta_data


def api_key(filename='api_key.config'):
    with open(filename) as file:
        for line in file:
            return line.strip()

    raise EnvironmentError('api key not found')


def main():
    pass
