from os.path import dirname, abspath, join
import sys
import logging
import matplotlib.pyplot as plt
from matplotlib import colors

THIS_DIR = dirname(__file__)
CODE_DIR = abspath(join(THIS_DIR, '../..', ''))
sys.path.append(CODE_DIR)

from dm.FilterUtil import FilterUtil
from dm.ConnectionUtil import ConnectionUtil
from dm.Storage import Storage
from dm.ValueUtil import ValueUtil


# https://matplotlib.org/gallery/statistics/hist.html
# https://realpython.com/python-histograms/
# https://matplotlib.org/1.2.1/examples/pylab_examples/histogram_demo.html
def gen_graph(data, action, extensions, title):
    fig, ax = plt.subplots(figsize=(8, 5))

    n, bins, patches = plt.hist(x=data, bins=50, color='#0504aa',
                                alpha=0.7, rwidth=0.85)

    fracs = n / n.max()
    norm = colors.Normalize(fracs.min(), fracs.max())
    for thisfrac, thispatch in zip(fracs, patches):
        color = plt.cm.viridis(norm(thisfrac))
        thispatch.set_facecolor(color)

    plt.grid(axis='y', alpha=0.5)
    plt.xlabel('Oneskorenie senzora [s]')
    plt.ylabel('Frequency')
    plt.xlim(0, 200)
    plt.ylim(0, 50)
    plt.title(title)

    # plt.text(4, 3, r'$\mu=15, b=3$')

    # nastavenie, aby sa aj pri malej figsize zobrazoval nazov X osy
    plt.tight_layout()

    if 'save' in action:
        filename = '{0}_{1}'.format('histogram_delays', title)
        for extension in extensions:
            fig.savefig(filename + '.' + extension, bbox_inches='tight', pad_inches=0)

    if 'show' in action:
        plt.show()


def delays(events, extensions: list, action, window_size, threshold):
    logger = logging.getLogger()
    logger.disabled = True

    logging.info('start detecting of sensor delays')
    ev = ValueUtil.detect_sensor_delays(events, window_size, threshold, 'co2_in_ppm',
                                        'co2_sensor_delays')
    events_delays = ValueUtil.delays(ev, 'co2_sensor_delays')
    logging.info('end detecting of sensor delays')

    title = 'window_size:{0},threshold:{1}'.format(window_size, threshold)
    gen_graph(events_delays, action, extensions, title)

    logger.disabled = False


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info('start')
    table_name = 'measured_peto'

    # stiahnutie dat
    con = ConnectionUtil.create_con()
    storage = Storage('examples/events_peto.json', 0, table_name)
    d = storage.load_data(con, 0, 0, 'co2_in_ppm')
    logging.info('downloaded events: %d' % len(d))

    # aplikovanie filtrov na eventy
    filtered = FilterUtil.only_valid_events(d)
    logging.info('events after applying the filter: %d' % len(filtered))

    extensions = ['png']
    delays(filtered, extensions, ['save'], 11, 15)
    delays(filtered, extensions, ['save'], 16, 10)
    delays(filtered, extensions, ['save'], 16, 15)
    delays(filtered, extensions, ['save'], 16, 20)
    delays(filtered, extensions, ['save'], 16, 25)
    delays(filtered, extensions, ['save'], 21, 15)
    delays(filtered, extensions, ['save'], 21, 20)
    delays(filtered, extensions, ['save'], 21, 25)
    delays(filtered, extensions, ['save'], 21, 30)
    delays(filtered, extensions, ['save'], 21, 35)
    delays(filtered, extensions, ['save'], 21, 40)

    logging.info('end')