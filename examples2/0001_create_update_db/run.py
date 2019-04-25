import json
import logging
import sys
import time
import os
from os.path import dirname, abspath, join

CODE_DIR = abspath(join(dirname(__file__), '../..', ''))
sys.path.append(CODE_DIR)

from dm.DBUtil import DBUtil
from dm.PreProcessing import PreProcessing
from dm.DateTimeUtil import DateTimeUtil
from dm.BeeeOnClient import BeeeOnClient
from dm.ConnectionUtil import ConnectionUtil
from dm.Storage import Storage


def delete_rows(con, timestamp_from, timestamp_to, table_name):
    table = table_name
    f = timestamp_from
    t = timestamp_to
    cur = con.cursor()

    cur.execute('UPDATE {0} SET pressure_in_hpa = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET temperature_in_celsius = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET temperature_in2_celsius = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET temperature_out_celsius = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET rh_in_percentage = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET rh_in2_percentage = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET rh_in_absolute_g_m3 = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET rh_in2_absolute_g_m3 = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET rh_in_specific_g_kg = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET rh_in2_specific_g_kg = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET rh_out_percentage = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET rh_out_absolute_g_m3 = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET rh_out_specific_g_kg = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))
    cur.execute('UPDATE {0} SET co2_in_ppm = Null WHERE measured_time >= {1} AND measured_time <= {2}'.format(table, f, t))

    con.commit()


def update_invalid_values(con):
    cur = con.cursor()

    # Peto
    for table in ['measured_peto', 'measured_peto_reduced', 'measured_filtered_peto', 'measured_filtered_peto_reduced']:
        cur.execute('UPDATE ' + table + ' SET open_close = 1 WHERE measured_time = 1538920482')
        cur.execute('UPDATE ' + table + ' SET open_close = 0 WHERE measured_time >= 1539410852 AND measured_time <= 1539410865')
        cur.execute('UPDATE ' + table + ' SET open_close = 0 WHERE measured_time >= 1542011517 AND measured_time <= 1542011529')
        cur.execute('UPDATE ' + table + ' SET open_close = 0 WHERE measured_time >= 1551896814 AND measured_time <= 1551902894')
        cur.execute('UPDATE ' + table + ' SET open_close = 0 WHERE measured_time >= 1551890462 AND measured_time <= 1551890556')
        cur.execute('UPDATE ' + table + ' SET open_close = 0 WHERE measured_time >= 1540144019 AND measured_time <= 1540144924')
        cur.execute('UPDATE ' + table + ' SET open_close = 1 WHERE measured_time >= 1545208319 AND measured_time <= 1545208364')
        cur.execute('UPDATE ' + table + ' SET open_close = 0 WHERE measured_time >= 1547292105 AND measured_time <= 1547292149')
        cur.execute('UPDATE ' + table + ' SET open_close = 0 WHERE measured_time >= 1551339840 AND measured_time <= 1551339852')
        cur.execute('UPDATE ' + table + ' SET open_close = 1 WHERE measured_time >= 1554613585 AND measured_time <= 1554613592')

        delete_rows(con, 1551847133, 1551889587, table)
        delete_rows(con, 1551903872, 1551908262, table)
        delete_rows(con, 1540374284, 1540378270, table)
        delete_rows(con, 1538995201, 1539012743, table)
        delete_rows(con, 1540365694, 1540366698, table)
        delete_rows(con, 1541870939, 1541883662, table)
        delete_rows(con, 1543082767, 1543128959, table)
        delete_rows(con, 1540366406, 1540392145, table)
        delete_rows(con, 1541342801, 1541342997, table)
        delete_rows(con, 1541248034, 1541256678, table)
        delete_rows(con, 1541336415, 1541343035, table)
        delete_rows(con, 1541265886, 1541268330, table)
        delete_rows(con, 1547017612, 1547017804, table)
        delete_rows(con, 1547764885, 1547797834, table)
        delete_rows(con, 1549952386, 1549954380, table)

        delete_rows(con, 1538951188, 1538951527, table)
        delete_rows(con, 1542105369, 1542106204, table)
        delete_rows(con, 1543180780, 1543182998, table)
        delete_rows(con, 1544377532, 1544378399, table)
        delete_rows(con, 1544733452, 1544736700, table)
        delete_rows(con, 1546466972, 1546529446, table)
        delete_rows(con, 1546792707, 1546812008, table)
        delete_rows(con, 1548016983, 1548076447, table)
        delete_rows(con, 1548117828, 1548135492, table)
        delete_rows(con, 1548211577, 1548228314, table)
        delete_rows(con, 1548238685, 1548239010, table)
        delete_rows(con, 1548279855, 1548280843, table)
        delete_rows(con, 1548826585, 1548828602, table)
        delete_rows(con, 1547291955, 1547292307, table)
        delete_rows(con, 1554060946, 1554063977, table)
        delete_rows(con, 1539170291, 1539187647, table)
        delete_rows(con, 1539332345, 1539382163, table)
        delete_rows(con, 1542496507, 1542497157, table)
    con.commit()

    # Klarka
    for table in ['measured_klarka', 'measured_klarka_reduced']:
        cur.execute('UPDATE ' + table + ' SET open_close = 0 WHERE measured_time = 1547490233')
        cur.execute('UPDATE ' + table + ' SET open_close = 0 WHERE measured_time = 1547642276')
        delete_rows(con, 1543778231, 1543780663, table)
        delete_rows(con, 1543870389, 1543872050, table)
        delete_rows(con, 1543957520, 1543959601, table)
        delete_rows(con, 1543997375, 1543999203, table)
        delete_rows(con, 1544083221, 1544085985, table)
        delete_rows(con, 1544853244, 1544854638, table)
        delete_rows(con, 1544858207, 1544859522, table)
        delete_rows(con, 1544872040, 1544873665, table)
        delete_rows(con, 1545245340, 1545248670, table)
        delete_rows(con, 1545557366, 1545559131, table)
        delete_rows(con, 1545627631, 1545629640, table)
        delete_rows(con, 1545719336, 1545720430, table)
        delete_rows(con, 1545977374, 1545979301, table)
        delete_rows(con, 1546058643, 1546061636, table)
        delete_rows(con, 1546242220, 1546242512, table)
        delete_rows(con, 1546334479, 1546335248, table)
        delete_rows(con, 1546517881, 1546518855, table)
        delete_rows(con, 1547060502, 1547061743, table)
        delete_rows(con, 1547099682, 1547100651, table)
        delete_rows(con, 1547276544, 1547277427, table)
        delete_rows(con, 1547386299, 1547392041, table)
        delete_rows(con, 1547507658, 1547508639, table)
        delete_rows(con, 1547528889, 1547529718, table)
        delete_rows(con, 1547585580, 1547586257, table)
        delete_rows(con, 1547705649, 1547707389, table)
        delete_rows(con, 1547710355, 1547711841, table)
        delete_rows(con, 1547794549, 1547795467, table)
        delete_rows(con, 1547800149, 1547801075, table)
        delete_rows(con, 1547978575, 1547979117, table)
        delete_rows(con, 1549023730, 1549025070, table)
        delete_rows(con, 1549261021, 1549262220, table)
        delete_rows(con, 1549274799, 1549276027, table)
        delete_rows(con, 1549482223, 1549482942, table)
        delete_rows(con, 1549774951, 1549775512, table)
        delete_rows(con, 1549802642, 1549803647, table)
        delete_rows(con, 1549999713, 1550000336, table)
        delete_rows(con, 1550041705, 1550043003, table)
        delete_rows(con, 1550065278, 1550065742, table)
        delete_rows(con, 1550127551, 1550135344, table)
        delete_rows(con, 1550313983, 1550315187, table)
        delete_rows(con, 1550386479, 1550387654, table)
        delete_rows(con, 1550425625, 1550427306, table)
        delete_rows(con, 1550911707, 1550912637, table)
        delete_rows(con, 1550990225, 1550991041, table)
        delete_rows(con, 1551075714, 1551077034, table)
        delete_rows(con, 1551114681, 1551115090, table)
        delete_rows(con, 1551472217, 1551474696, table)
        delete_rows(con, 1551497002, 1551498131, table)
        delete_rows(con, 1551535157, 1551535854, table)
        delete_rows(con, 1551603043, 1551604570, table)
        delete_rows(con, 1551611897, 1551612707, table)
        delete_rows(con, 1551615797, 1551616512, table)
        delete_rows(con, 1551773395, 1551774278, table)
        delete_rows(con, 1551847552, 1551848069, table)
        delete_rows(con, 1551852471, 1551852740, table)
        delete_rows(con, 1551934301, 1551935989, table)
        delete_rows(con, 1552028555, 1552031024, table)
        delete_rows(con, 1552579048, 1552580015, table)
        delete_rows(con, 1552678283, 1552679648, table)
        delete_rows(con, 1552805692, 1552806603, table)
        delete_rows(con, 1552820722, 1552822268, table)
        delete_rows(con, 1553081434, 1553082352, table)
        delete_rows(con, 1553193785, 1553196264, table)
        delete_rows(con, 1553404359, 1553405932, table)
        delete_rows(con, 1553416708, 1553418395, table)
        delete_rows(con, 1553454456, 1553455531, table)
        delete_rows(con, 1553501914, 1553503068, table)
        delete_rows(con, 1553576079, 1553578058, table)

        delete_rows(con, 1553125531, 1553135913, table)
        delete_rows(con, 1553212877, 1553225588, table)
        delete_rows(con, 1555104457, 1555105702, table)
        delete_rows(con, 1555958944, 1555960296, table)
        delete_rows(con, 1556168621, 1556182367, table)
    con.commit()

    for table in ['measured_klarka_shower', 'measured_klarka_shower_reduced']:
        delete_rows(con, 1543691739, 1543692802, table)
        delete_rows(con, 1543763354, 1543765783, table)
        delete_rows(con, 1543768918, 1543771764, table)
        delete_rows(con, 1543867909, 1543869942, table)
        delete_rows(con, 1544033698, 1544035813, table)
        delete_rows(con, 1544040744, 1544041792, table)
        delete_rows(con, 1544071291, 1544072531, table)
        delete_rows(con, 1544123600, 1544124611, table)
        delete_rows(con, 1544765501, 1544766004, table)
        delete_rows(con, 1544855407, 1544857498, table)
        delete_rows(con, 1544900701, 1544902516, table)
        delete_rows(con, 1544912466, 1544913135, table)
        delete_rows(con, 1544963217, 1544964542, table)
        delete_rows(con, 1544981395, 1544982187, table)
        delete_rows(con, 1545070652, 1545072295, table)
        delete_rows(con, 1545075421, 1545077116, table)
        delete_rows(con, 1545108753, 1545109405, table)
        delete_rows(con, 1545110920, 1545111711, table)
        delete_rows(con, 1545283812, 1545284350, table)
        delete_rows(con, 1545308109, 1545309888, table)
        delete_rows(con, 1545336923, 1545338519, table)
        delete_rows(con, 1545577036, 1545578297, table)
        delete_rows(con, 1545588610, 1545590175, table)
        delete_rows(con, 1545595024, 1545598810, table)
        delete_rows(con, 1545674780, 1545675524, table)
        delete_rows(con, 1545678932, 1545679614, table)
        delete_rows(con, 1545760372, 1545762405, table)
        delete_rows(con, 1545853669, 1545854644, table)
        delete_rows(con, 1545863051, 1545864591, table)
        delete_rows(con, 1545891711, 1545892821, table)
        delete_rows(con, 1545983681, 1545984176, table)
        delete_rows(con, 1546204528, 1546209592, table)
        delete_rows(con, 1546232917, 1546233497, table)
    con.commit()


def devices(filename='devices.json'):
    with open(filename, 'r') as f:
        data = json.load(f)

    return data


def create_update_table(con, clients, start, end, devices, tables):
    step_size = 600
    time_shift = 1200
    min_commit_size = 10000
    precision = 2

    total_min = None
    last_inserted_table = tables[0][0]
    str_tables = ''

    # odstranenie posledneho intervalu, ktory mohol obsahovat chybajuce hodnoty
    # z dovodu, ze tento interval este neexistoval
    delete_step = 1 * step_size

    for table in tables:
        DBUtil.create_table(con, table[0])

        DBUtil.delete_from_time(con, table[0], delete_step)
        str_tables += table[0] + ', '

        last_inserted_row = DBUtil.last_inserted_values(con, table[0])
        if last_inserted_row is None:
            continue

        if total_min is None or total_min > last_inserted_row[0]:
            total_min = last_inserted_row[0]
            last_inserted_table = table[0]

    last_open_close_state = 0
    actual_commit_size = 0

    logging.info('table: %s' % str_tables)

    for interval_from in range(start - delete_step, end, step_size):
        interval_to = interval_from + step_size

        # ak sa v databaze nachadzaju nejake data a timestamp posledne vlozeneho casu,
        # je vacsi ako aktualne spracovavany koniec intervalu, tak sa spracovanie
        # tohto intervalu preskoci, inak sa zacne od tohto timestampu a tabulka sa doplna
        # o nove udaje
        if total_min is not None:
            if interval_to < total_min:
                # skip inserted interval
                continue

        logging.debug('processed interval %s' % DateTimeUtil.create_interval_str(interval_from,
                                                                                 interval_to))

        maps, values = PreProcessing.prepare(clients, devices, interval_from, interval_to,
                                             last_open_close_state, time_shift)

        for table in tables:
            if 'filtered' in table[0]:
                values = PreProcessing.ppm_filter(values)

            PreProcessing.insert_values(con, table[0], values, maps, table[1], precision)
            actual_commit_size += step_size // table[1]

        if actual_commit_size > min_commit_size:
            logging.debug('commit %s rows' % actual_commit_size)
            con.commit()
            actual_commit_size = 0

        last_open_close_state = DBUtil.last_inserted_open_close_state(con, last_inserted_table)

    logging.debug('commit %s rows' % actual_commit_size)
    con.commit()

    logging.info('table %s created and updated' % str_tables)


def peto_intrak_db(con, cls, start, end, devs):
    # v tomto case doslo k zmene DeviceID Protronix CO2 senzora
    middle = int(DateTimeUtil.local_time_str_to_utc('2019/02/20 03:00:00').timestamp())

    tables = [
        ('measured_peto', 1),
        ('measured_peto_reduced', 15),
        ('measured_filtered_peto', 1),
        ('measured_filtered_peto_reduced', 15),
    ]

    create_update_table(con, cls, start, middle, devs['peto'], tables)
    create_update_table(con, cls, middle, end, devs['peto2'], tables)


def klarka_izba_db(con, cls, start, end, devs):
    tables = [
        ('measured_klarka', 1),
        ('measured_klarka_reduced', 15),
    ]
    create_update_table(con, cls, start, end, devs['klarka'], tables)

    # druha DB obsahuje od urciteho datumu vonkajsi IQ Home senzor
    middle = int(DateTimeUtil.local_time_str_to_utc('2019/02/19 12:00:00').timestamp())
    tables = [
        ('measured_klarka_iqhome', 1),
        ('measured_klarka_iqhome_reduced', 15),
    ]
    create_update_table(con, cls, start, middle, devs['klarka'], tables)
    create_update_table(con, cls, middle, end, devs['klarka2'], tables)


def klarka_sprcha_db(con, cls, start, end, devs):
    tables = [
        ('measured_klarka_shower', 1),
        ('measured_klarka_shower_reduced', 15),
    ]
    create_update_table(con, cls, start, end, devs['klarka_shower2'], tables)

    update_shower(con, 'examples/events_klarka_shower.json', ['measured_klarka_shower', 'measured_klarka_shower_reduced'])


def update_shower(con, filename, table_names):
    pwd = os.path.dirname(__file__)
    os.path.abspath(os.path.join(pwd, './..', '')) + '/'

    events = Storage(filename, 0, '').read_meta()

    cur = con.cursor()
    for table in table_names:
        cur.execute('UPDATE {0} SET open_close = 0'.format(table))
    con.commit()

    for event in events:
        start = event['e_start']['timestamp']
        end = event['e_end']['timestamp']

        for timestamp in range(start, end):
            for table in table_names:
                DBUtil.update_attribute(con, table, 'open_close', 1, timestamp)
        con.commit()


def david(con, cls, start, end, devs):
    tables = [
        ('measured_david', 1),
        ('measured_david_reduced', 15),
    ]
    create_update_table(con, cls, start, end, devs['david'], tables)


def martin(con, cls, start, end, devs):
    tables = [
        ('measured_martin', 1),
        ('measured_martin_reduced', 15),
    ]
    create_update_table(con, cls, start, end, devs['martin'], tables)


def martin_door(con, cls, start, end, devs):
    tables = [
        ('measured_martin_door', 1),
        ('measured_martin_door_reduced', 15),
    ]
    create_update_table(con, cls, start, end, devs['martin_door'], tables)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    devs = devices()

    con = ConnectionUtil.create_con()
    cur = con.cursor()

    cls = {
        "ant-work": BeeeOnClient("ant-work.fit.vutbr.cz", 8010),
        "rehivetech": BeeeOnClient("beeeon.rehivetech.com", 8010),
    }

    cls['ant-work'].api_key = ConnectionUtil.api_key('ant-work')
    cls['rehivetech'].api_key = ConnectionUtil.api_key('rehivetech')

    # from 2018/09/20 00:01:00
    start = int(DateTimeUtil.local_time_str_to_utc('2018/09/20 01:00:00').timestamp())
    end = int(time.time())

    peto_intrak_db(con, cls, start, end, devs)
    klarka_izba_db(con, cls, start, end, devs)

    start = int(DateTimeUtil.local_time_str_to_utc('2018/07/18 06:00:00').timestamp())
    klarka_sprcha_db(con, cls, start, end, devs)

    start = int(DateTimeUtil.local_time_str_to_utc('2019/04/03 15:00:00').timestamp())
    david(con, cls, start, end, devs)

    start = int(DateTimeUtil.local_time_str_to_utc('2019/04/01 15:00:00').timestamp())
    martin(con, cls, start, end, devs)
    martin_door(con, cls, start, end, devs)

    update_invalid_values(con)
