from astropy.table import Table, TimeSeries
from astropy.time import Time

from datetime import datetime

date = datetime(2018, 7, 1, 10, 10, 10)

time = Time(['2016-03-22T12:30:31', '2015-01-21T12:30:32', '2016-03-22T12:30:40'])
a = TimeSeries(time=time, data=[[1, 2, 3], [4, 5, 6]], names=['a', 'b'])

# works
print(a['a'])
print(a['a'].time[0])

# TODO
print(a.columns['a'])
print(a['a'][()])

# failing
# a[0]

t = Table([[1,2],[4,3]], names=['a', 'b'])
t.add_index('b')

a.sort('time')
"""
Decisions:

For slicing, implement things like timeseries[datetime] using methods like timeseries.closest(datetime) instead.
For integers it works as expected
For strings (t[‘flux’]) always include time column ⇐ maybe not, start with the more implicit one, this would just return the ‘flux’ column
t.columns[‘flux’] to access “raw” Column data without the Time column returned, too
Subclass Row -> TimeSeriesRow
Timeseries is always autosorted (==> we need to override Table operations, too to have a vstack 

timeseries[‘col_b’] -> returns TimeSeriesColumn (impleemnts >, < , >=, etc)
Timeseries[‘col_b’][0] -> returns value of col_b
timeseries[‘col_b’].time[0]

Have timeseries.time and maybe later we can alias timeseries.index

timeseries[‘col_b’][()] -> returns Column object


multi_row_timeseries = timeseries[timeseries['col_b'] > 5.2]

Using:


>>> ts = SampledTimeSeries(time=['2016-03-22T12:30:31', '2016-03-22T12:30:32', '2016-03-22T12:30:40'], data=[1, 4, 3]

>>> ts.closest(datetime)
>>> ts.select(datetime_start:datetime_end)  # all values within range


Class BaseTimeSeries(object):

Class TimeSeriesRow(Row):
    # Time column is still special, this is returned when indexed with a scalar rather than the usual Row that’s returned for normal Tables
"""