"""

"""
from dm.Storage import Storage
from dm.selectors.interval.AbstractIntervalSelector import AbstractIntervalSelector

__author__ = ''
__email__ = ''


class SimpleIntervalSelector(AbstractIntervalSelector):
    def interval(self, column_name, start, end):
        return Storage.select_interval(self.con, start, end, column_name, self.table_name)
