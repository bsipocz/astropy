# Licensed under a 3-clause BSD style license - see LICENSE.rst

from ..table import QTable, Column, Row, MaskedColumn, TableColumns, vstack, hstack
from ..time import Time, TimeDelta


__all__ = ['TimeSeries']


class TimeSeriesColumn(Column):
    pass


class TimeSeriesRow(Row):
    pass


class TimeSeriesMaskedColumn(MaskedColumn):
    pass


class TimeSeriesTableColumns(TableColumns):

    def __init__(self, cols={}, time=None):
        print(6)
#        cols['time'] = time
        super().__init__(cols)
        print(7)

    def __getitem__(self, item):
        print(8)
        columns = non_time_column = super().__getitem__(item)
        print(item, print(type(item)))
        try:
            time_column = super().__getitem__('time')
            columns = hstack([time_column, non_time_column])
        except KeyError:
            pass
        print(10)
        return(columns)


class TimeColumn(Column):
    pass


class TimeSeries(QTable):
    # Required functionality listed in APE9
    #    Extending timeseries with extra rows
    #    Concatenating multiple timeseries objects
    #    Sorting
    #    Slicing / selecting time ranges (indexing)
    #    Re-binning and re-sampling timeseries
    #    Interpolating to different time stamps.
    #    Masking
    #    Support for subtraction and addition (e.g. background).
    #    Plotting and visualisation.
    #    Have high performance into ~millions of rows.

    #    Converting between time systems
    #    Astropy unit support
    #    Support variable width time bins.

    #    A 'Time' index column exists which enforces unique indexes.
    #    The table is always sorted in terms of increasing time.

#    Row = TimeSeriesRow
#    Column = TimeSeriesColumn
#    MaskedColumn = TimeSeriesMaskedColumn

    TableColumns = TimeSeriesTableColumns

    def __init__(self, data, time, time_delta=None, **kwargs):
        """
        Time Series.

        Parameters
        ==========
        """
        if not isinstance(time, (Time, TimeDelta)):
            raise ValueError("'time' should be Time or TimeDelta")
        print(3)
        self.time = self.Column(time, name='time')
        print(4)
        super().__init__(data=data, **kwargs)
        # TODO: check whether data had a 'time' column already
        self.columns['time'] = self.time
        print(5)

#    def __getitem__(self, item):
#        if isinstance(item, str):
#            return self.columns[item, self.time]
#        elif isinstance(item, (int, np.integer)):
#            return self.Row(self, item)
#        elif (isinstance(item, np.ndarray) and item.shape == () and item.dtype.kind == 'i'):
#            return self.Row(self, item.item())
#        elif self._is_list_or_tuple_of_str(item):
#            out = self.__class__([self[x] for x in item],
#                                 meta=deepcopy(self.meta),
#                                 copy_indices=self._copy_indices)
#            out._groups = groups.TableGroups(out, indices=self.groups._indices,
#                                             keys=self.groups._keys)
#            return out
#        elif ((isinstance(item, np.ndarray) and item.size == 0) or
#              (isinstance(item, (tuple, list)) and not item)):
#            # If item is an empty array/list/tuple then return the table with no rows
#            return self._new_from_slice([])
#        elif (isinstance(item, slice) or
#              isinstance(item, np.ndarray) or
#              isinstance(item, list) or
#              isinstance(item, tuple) and all(isinstance(x, np.ndarray)
#                                              for x in item)):
#            # here for the many ways to give a slice; a tuple of ndarray
#            # is produced by np.where, as in t[np.where(t['a'] > 2)]
#            # For all, a new table is constructed with slice of all columns
#            return self._new_from_slice(item)
#        else:
#            raise ValueError('Illegal type {0} for table item access'
#                             .format(type(item)))
