from astropy.table import Table, TimeSeries
from astropy.time import Time

from datetime import datetime

import astropy

date = datetime(2018, 7, 1, 10, 10, 10)

time = Time(['2016-03-22T12:30:31', '2015-01-21T12:30:32', '2016-03-22T12:30:40'])
a = TimeSeries(time=time, data=[[10, 2, 3], [4, 5, 6]], names=['a', 'b'])
b = Table([[1, 2, 11], [3, 4, 1], [1, 1, 1]], names=['a', 'b', 'c'])
c = TimeSeries()

# works, but the types are off, a['a'] is not a TimeSeries but a Table with 18b941a9
# failing to initialize an empty TimeSeries with 18b941a9
print(9991, type(a['a']), a['a'])
print(9992, type(a['a'].time[0]), a['a'].time[0])
print(9993, a['time'])
print(9994, type(c), c)

# TODO
print(8993, a.columns['a'])  # This should give back 'a' as a normal Column
print(8994, a['a'][()])   # This should give back 'a' as a normal Column
print(8996, type(a[0]), a[0])   # This should give back a TimeRow rather than a normal Row

# TODO
# For this we need to be able to do TimeSeries([TimeSeries, TimeSeries, Time]) type initialization, or override TimeSeries.__getitem__
# print(a['a', 'b'])

# failing
# hstack TimeSeries

t = Table([[1,2],[4,3]], names=['a', 'b'])
t.add_index('b', engine=astropy.table.BST)

# Works:
# b.sort('b')
# print(99995, b)

from astropy.table.index import get_index

get_index(a, a['a'])
print(a.sort('a'))

# failing
# a.add_index('a')  # Failing with ValueError: too many values to unpack (expected 2)
# a.add_index('time') # Failing with ValueError: Cannot replace column 'time'.  Use Table.replace_column() instead.
# a.sort('time')



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