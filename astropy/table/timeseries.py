# Licensed under a 3-clause BSD style license - see LICENSE.rst

from .table import QTable, Column, Row, MaskedColumn, TableColumns


class TimeSeriesColumn(Column):
    pass


class TimeSeriesRow(Row):
    pass


class TimeSeriesyMaskedColumn(MaskedColumn):
    pass


class TimeSeriesTableColumns(TableColumns):
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

    Row = TimeSeriesRow
    Column = TimeSeriesColumn
    MaskedColumn = TimeSeriesyMaskedColumn
    TableColumns = TimeSeriesTableColumns

    def __init__():
        """
        """
        pass
