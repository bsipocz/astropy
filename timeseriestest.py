from astropy.table import Table, TimeSeries
from astropy.time import Time

time = Time(['2016-03-22T12:30:31', '2016-03-22T12:30:32', '2016-03-22T12:30:40'])
a=TimeSeries(time=time, data=[[1, 4, 3],[4,5,6]], names=['a', 'b'])

a['a']
