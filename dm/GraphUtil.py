from os.path import dirname, abspath, join
import sys
import matplotlib.pyplot as plt
import numpy as np

THIS_DIR = dirname(__file__)
CODE_DIR = abspath(join(THIS_DIR, '../..', ''))
sys.path.append(CODE_DIR)

from dm.ValueUtil import ValueUtil


class GraphUtil:
    @staticmethod
    def gen_duration_histogram(events, action, extensions, title,
                               intervals, threshold):
        """ Vygenerovanie histogramu dlzok vetrania.

        :param events: zoznam eventov
        :param action: show|save - pre ulozenie alebo zobrazenie histogramu
        :param extensions: zoznam pripon v pripade, ze sa ma subor ulozit
        :param title: nazov grafu
        :param intervals: zoznam intervalov v minutach, pre ktore sa ma pocitat pocet hodnot
        :param threshold: hodnota, ktora sa pripocita/odpocita od intervalu a vytvori sa rozsah hodnot
                          pre dany stlpec v histograme
        :return:
        """
        durations = ValueUtil.events_duration(events, None)

        x = []
        y = []
        for interval in intervals:
            x.append('%d - %d' % (interval - threshold, interval + threshold))
            y.append(0)

        threshold *= 60
        for value in durations:
            for k in range(0, len(intervals)):
                interval = intervals[k] * 60

                if (interval - threshold) < value < (interval + threshold):
                    y[k] += 1
                    break

        fig, ax = plt.subplots(figsize=(8, 5))
        y_pos = np.arange(len(x))

        plt.bar(y_pos, y, align='center', alpha=0.5, color='#0504aa')
        plt.grid(axis='y', alpha=0.5)
        plt.xticks(y_pos, x)
        plt.xlabel('Ventilation length [min]')
        plt.ylabel('Frequency')
        plt.title(title)

        text = 'celkom eventov: {0}\n'.format(len(events))
        text += 'eventy, ktore vyhovuju intervalom: {0}'.format(sum(y))
        plt.text(len(x) * 0.5, max(y)*0.8, text)

        # nastavenie, aby sa aj pri malej figsize zobrazoval nazov X osy
        plt.tight_layout()

        if 'save' in action:
            filename = '{0}_{1}'.format('histogram_delays', title)
            for extension in extensions:
                fig.savefig(filename + '.' + extension, bbox_inches='tight', pad_inches=0)

        if 'show' in action:
            plt.show()

    @staticmethod
    def gen_stacked_bar_graph(first_col, second_col, third_col):
        ind = np.arange(3)
        width = 0.35
        y_offset = np.zeros(3)
        fig = plt.figure()

        p1 = plt.bar(ind, first_col, width, bottom=y_offset)
        y_offset = y_offset + first_col

        p2 = plt.bar(ind, second_col, width, bottom=y_offset)
        y_offset = y_offset + second_col

        p3 = plt.bar(ind, third_col, width, bottom=y_offset)
        plt.xticks(ind, ('5 minutes', '10 minutes', '25 minutes'))

        plt.legend((p1[0], p2[1], p3[2]), ('pred 5 min', 'pred 10 min', 'pred 25 min'),
                   loc='lower center', bbox_to_anchor=(0.5, -0.1), bbox_transform=fig.transFigure)

        plt.subplots_adjust(bottom=0.15)

        fig.savefig('result.png', bbox_inches="tight")

        plt.show()