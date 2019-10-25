# Note that we test the main astropy.wcs.WCS class directly rather than testing
# the mix-in class on its own (since it's not functional without being used as
# a mix-in)

import warnings

import numpy as np
import pytest
from numpy.testing import assert_equal, assert_allclose

from astropy import units as u
from astropy.time import Time
from astropy.tests.helper import assert_quantity_allclose
from astropy.units import Quantity
from astropy.coordinates import ICRS, FK5, Galactic, SkyCoord
from astropy.io.fits import Header
from astropy.io.fits.verify import VerifyWarning
from astropy.units.core import UnitsWarning
from astropy.utils.data import get_pkg_data_filename
from astropy.wcs.wcs import WCS, FITSFixedWarning
from astropy.wcs.wcsapi.fitswcs import custom_ctype_to_ucd_mapping

###############################################################################
# The following example is the simplest WCS with default values
###############################################################################


WCS_EMPTY = WCS(naxis=1)
WCS_EMPTY.wcs.crpix = [1]


def test_empty():

    wcs = WCS_EMPTY

    # Low-level API

    assert wcs.pixel_n_dim == 1
    assert wcs.world_n_dim == 1
    assert wcs.array_shape is None
    assert wcs.pixel_shape is None
    assert wcs.world_axis_physical_types == [None]
    assert wcs.world_axis_units == ['']
    assert wcs.pixel_axis_names == ['']
    assert wcs.world_axis_names == ['']

    assert_equal(wcs.axis_correlation_matrix, True)

    assert wcs.world_axis_object_components == [('world', 0, 'value')]

    assert wcs.world_axis_object_classes['world'][0] is Quantity
    assert wcs.world_axis_object_classes['world'][1] == ()
    assert wcs.world_axis_object_classes['world'][2]['unit'] is u.one

    assert_allclose(wcs.pixel_to_world_values(29), 29)
    assert_allclose(wcs.array_index_to_world_values(29), 29)

    assert np.ndim(wcs.pixel_to_world_values(29)) == 0
    assert np.ndim(wcs.array_index_to_world_values(29)) == 0

    assert_allclose(wcs.world_to_pixel_values(29), 29)
    assert_equal(wcs.world_to_array_index_values(29), (29,))

    assert np.ndim(wcs.world_to_pixel_values(29)) == 0
    assert np.ndim(wcs.world_to_array_index_values(29)) == 0

    # High-level API

    coord = wcs.pixel_to_world(29)
    assert_quantity_allclose(coord, 29 * u.one)
    assert np.ndim(coord) == 0

    coord = wcs.array_index_to_world(29)
    assert_quantity_allclose(coord, 29 * u.one)
    assert np.ndim(coord) == 0

    coord = 15 * u.one

    x = wcs.world_to_pixel(coord)
    assert_allclose(x, 15.)
    assert np.ndim(x) == 0

    i = wcs.world_to_array_index(coord)
    assert_equal(i, 15)
    assert np.ndim(i) == 0


###############################################################################
# The following example is a simple 2D image with celestial coordinates
###############################################################################

HEADER_SIMPLE_CELESTIAL = """
WCSAXES = 2
CTYPE1  = RA---TAN
CTYPE2  = DEC--TAN
CRVAL1  = 10
CRVAL2  = 20
CRPIX1  = 30
CRPIX2  = 40
CDELT1  = -0.1
CDELT2  =  0.1
CROTA2  = 0.
CUNIT1  = deg
CUNIT2  = deg
"""

with warnings.catch_warnings():
    warnings.simplefilter('ignore', VerifyWarning)
    WCS_SIMPLE_CELESTIAL = WCS(Header.fromstring(
        HEADER_SIMPLE_CELESTIAL, sep='\n'))


def test_simple_celestial():

    wcs = WCS_SIMPLE_CELESTIAL

    # Low-level API

    assert wcs.pixel_n_dim == 2
    assert wcs.world_n_dim == 2
    assert wcs.array_shape is None
    assert wcs.pixel_shape is None
    assert wcs.world_axis_physical_types == ['pos.eq.ra', 'pos.eq.dec']
    assert wcs.world_axis_units == ['deg', 'deg']
    assert wcs.pixel_axis_names == ['', '']
    assert wcs.world_axis_names == ['', '']

    assert_equal(wcs.axis_correlation_matrix, True)

    assert wcs.world_axis_object_components == [('celestial', 0, 'spherical.lon.degree'),
                                                ('celestial', 1, 'spherical.lat.degree')]

    assert wcs.world_axis_object_classes['celestial'][0] is SkyCoord
    assert wcs.world_axis_object_classes['celestial'][1] == ()
    assert isinstance(wcs.world_axis_object_classes['celestial'][2]['frame'], ICRS)
    assert wcs.world_axis_object_classes['celestial'][2]['unit'] is u.deg

    assert_allclose(wcs.pixel_to_world_values(29, 39), (10, 20))
    assert_allclose(wcs.array_index_to_world_values(39, 29), (10, 20))

    assert_allclose(wcs.world_to_pixel_values(10, 20), (29., 39.))
    assert_equal(wcs.world_to_array_index_values(10, 20), (39, 29))

    # High-level API

    coord = wcs.pixel_to_world(29, 39)
    assert isinstance(coord, SkyCoord)
    assert isinstance(coord.frame, ICRS)
    assert coord.ra.deg == 10
    assert coord.dec.deg == 20

    coord = wcs.array_index_to_world(39, 29)
    assert isinstance(coord, SkyCoord)
    assert isinstance(coord.frame, ICRS)
    assert coord.ra.deg == 10
    assert coord.dec.deg == 20

    coord = SkyCoord(10, 20, unit='deg', frame='icrs')

    x, y = wcs.world_to_pixel(coord)
    assert_allclose(x, 29.)
    assert_allclose(y, 39.)

    i, j = wcs.world_to_array_index(coord)
    assert_equal(i, 39)
    assert_equal(j, 29)

    # Check that if the coordinates are passed in a different frame things still
    # work properly

    coord_galactic = coord.galactic

    x, y = wcs.world_to_pixel(coord_galactic)
    assert_allclose(x, 29.)
    assert_allclose(y, 39.)

    i, j = wcs.world_to_array_index(coord_galactic)
    assert_equal(i, 39)
    assert_equal(j, 29)

    # Check that we can actually index the array

    data = np.arange(3600).reshape((60, 60))

    coord = SkyCoord(10, 20, unit='deg', frame='icrs')
    index = wcs.world_to_array_index(coord)
    assert_equal(data[index], 2369)

    coord = SkyCoord([10, 12], [20, 22], unit='deg', frame='icrs')
    index = wcs.world_to_array_index(coord)
    assert_equal(data[index], [2369, 3550])


###############################################################################
# The following example is a spectral cube with axes in an unusual order
###############################################################################

HEADER_SPECTRAL_CUBE = """
WCSAXES = 3
CTYPE1  = GLAT-CAR
CTYPE2  = FREQ
CTYPE3  = GLON-CAR
CNAME1  = Latitude
CNAME2  = Frequency
CNAME3  = Longitude
CRVAL1  = 10
CRVAL2  = 20
CRVAL3  = 25
CRPIX1  = 30
CRPIX2  = 40
CRPIX3  = 45
CDELT1  = -0.1
CDELT2  =  0.5
CDELT3  =  0.1
CUNIT1  = deg
CUNIT2  = Hz
CUNIT3  = deg
"""

with warnings.catch_warnings():
    warnings.simplefilter('ignore', VerifyWarning)
    WCS_SPECTRAL_CUBE = WCS(Header.fromstring(HEADER_SPECTRAL_CUBE, sep='\n'))


def test_spectral_cube():

    # Spectral cube with a weird axis ordering

    wcs = WCS_SPECTRAL_CUBE

    # Low-level API

    assert wcs.pixel_n_dim == 3
    assert wcs.world_n_dim == 3
    assert wcs.array_shape is None
    assert wcs.pixel_shape is None
    assert wcs.world_axis_physical_types == ['pos.galactic.lat', 'em.freq', 'pos.galactic.lon']
    assert wcs.world_axis_units == ['deg', 'Hz', 'deg']
    assert wcs.pixel_axis_names == ['', '', '']
    assert wcs.world_axis_names == ['Latitude', 'Frequency', 'Longitude']

    assert_equal(wcs.axis_correlation_matrix, [[True, False, True],
                                               [False, True, False],
                                               [True, False, True]])

    assert wcs.world_axis_object_components == [('celestial', 1, 'spherical.lat.degree'),
                                                ('freq', 0, 'value'),
                                                ('celestial', 0, 'spherical.lon.degree')]

    assert wcs.world_axis_object_classes['celestial'][0] is SkyCoord
    assert wcs.world_axis_object_classes['celestial'][1] == ()
    assert isinstance(wcs.world_axis_object_classes['celestial'][2]['frame'], Galactic)
    assert wcs.world_axis_object_classes['celestial'][2]['unit'] is u.deg

    assert wcs.world_axis_object_classes['freq'][0] is Quantity
    assert wcs.world_axis_object_classes['freq'][1] == ()
    assert wcs.world_axis_object_classes['freq'][2] == {'unit': 'Hz'}

    assert_allclose(wcs.pixel_to_world_values(29, 39, 44), (10, 20, 25))
    assert_allclose(wcs.array_index_to_world_values(44, 39, 29), (10, 20, 25))

    assert_allclose(wcs.world_to_pixel_values(10, 20, 25), (29., 39., 44.))
    assert_equal(wcs.world_to_array_index_values(10, 20, 25), (44, 39, 29))

    # High-level API

    coord, spec = wcs.pixel_to_world(29, 39, 44)
    assert isinstance(coord, SkyCoord)
    assert isinstance(coord.frame, Galactic)
    assert coord.l.deg == 25
    assert coord.b.deg == 10
    assert isinstance(spec, Quantity)
    assert spec.to_value(u.Hz) == 20

    coord, spec = wcs.array_index_to_world(44, 39, 29)
    assert isinstance(coord, SkyCoord)
    assert isinstance(coord.frame, Galactic)
    assert coord.l.deg == 25
    assert coord.b.deg == 10
    assert isinstance(spec, Quantity)
    assert spec.to_value(u.Hz) == 20

    coord = SkyCoord(25, 10, unit='deg', frame='galactic')
    spec = 20 * u.Hz

    x, y, z = wcs.world_to_pixel(coord, spec)
    assert_allclose(x, 29.)
    assert_allclose(y, 39.)
    assert_allclose(z, 44.)

    # Order of world coordinates shouldn't matter
    x, y, z = wcs.world_to_pixel(spec, coord)
    assert_allclose(x, 29.)
    assert_allclose(y, 39.)
    assert_allclose(z, 44.)

    i, j, k = wcs.world_to_array_index(coord, spec)
    assert_equal(i, 44)
    assert_equal(j, 39)
    assert_equal(k, 29)

    # Order of world coordinates shouldn't matter
    i, j, k = wcs.world_to_array_index(spec, coord)
    assert_equal(i, 44)
    assert_equal(j, 39)
    assert_equal(k, 29)


HEADER_SPECTRAL_CUBE_NONALIGNED = HEADER_SPECTRAL_CUBE.strip() + '\n' + """
PC2_3 = -0.5
PC3_2 = +0.5
"""

with warnings.catch_warnings():
    warnings.simplefilter('ignore', VerifyWarning)
    WCS_SPECTRAL_CUBE_NONALIGNED = WCS(Header.fromstring(
        HEADER_SPECTRAL_CUBE_NONALIGNED, sep='\n'))


def test_spectral_cube_nonaligned():

    # Make sure that correlation matrix gets adjusted if there are non-identity
    # CD matrix terms.

    wcs = WCS_SPECTRAL_CUBE_NONALIGNED

    assert wcs.world_axis_physical_types == ['pos.galactic.lat', 'em.freq', 'pos.galactic.lon']
    assert wcs.world_axis_units == ['deg', 'Hz', 'deg']
    assert wcs.pixel_axis_names == ['', '', '']
    assert wcs.world_axis_names == ['Latitude', 'Frequency', 'Longitude']

    assert_equal(wcs.axis_correlation_matrix, [[True, True, True],
                                               [False, True, True],
                                               [True, True, True]])

    # NOTE: we check world_axis_object_components and world_axis_object_classes
    # again here because in the past this failed when non-aligned axes were
    # present, so this serves as a regression test.

    assert wcs.world_axis_object_components == [('celestial', 1, 'spherical.lat.degree'),
                                                ('freq', 0, 'value'),
                                                ('celestial', 0, 'spherical.lon.degree')]

    assert wcs.world_axis_object_classes['celestial'][0] is SkyCoord
    assert wcs.world_axis_object_classes['celestial'][1] == ()
    assert isinstance(wcs.world_axis_object_classes['celestial'][2]['frame'], Galactic)
    assert wcs.world_axis_object_classes['celestial'][2]['unit'] is u.deg

    assert wcs.world_axis_object_classes['freq'][0] is Quantity
    assert wcs.world_axis_object_classes['freq'][1] == ()
    assert wcs.world_axis_object_classes['freq'][2] == {'unit': 'Hz'}

###############################################################################
# The following example is from Rots et al (2015), Table 5. It represents a
# cube with two spatial dimensions and one time dimension
###############################################################################


HEADER_TIME_CUBE = """
SIMPLE  = T / Fits standard
BITPIX  = -32 / Bits per pixel
NAXIS   = 3 / Number of axes
NAXIS1  = 2048 / Axis length
NAXIS2  = 2048 / Axis length
NAXIS3  = 11 / Axis length
DATE    = '2008-10-28T14:39:06' / Date FITS file was generated
OBJECT  = '2008 TC3' / Name of the object observed
EXPTIME = 1.0011 / Integration time
MJD-OBS = 54746.02749237 / Obs start
DATE-OBS= '2008-10-07T00:39:35.3342' / Observing date
TELESCOP= 'VISTA' / ESO Telescope Name
INSTRUME= 'VIRCAM' / Instrument used.
TIMESYS = 'UTC' / From Observatory Time System
TREFPOS = 'TOPOCENT' / Topocentric
MJDREF  = 54746.0 / Time reference point in MJD
RADESYS = 'ICRS' / Not equinoctal
CTYPE2  = 'RA---ZPN' / Zenithal Polynomial Projection
CRVAL2  = 2.01824372640628 / RA at ref pixel
CUNIT2  = 'deg' / Angles are degrees always
CRPIX2  = 2956.6 / Pixel coordinate at ref point
CTYPE1  = 'DEC--ZPN' / Zenithal Polynomial Projection
CRVAL1  = 14.8289418840003 / Dec at ref pixel
CUNIT1  = 'deg' / Angles are degrees always
CRPIX1  = -448.2 / Pixel coordinate at ref point
CTYPE3  = 'UTC' / linear time (UTC)
CRVAL3  = 2375.341 / Relative time of first frame
CUNIT3  = 's' / Time unit
CRPIX3  = 1.0 / Pixel coordinate at ref point
CTYPE3A = 'TT' / alternative linear time (TT)
CRVAL3A = 2440.525 / Relative time of first frame
CUNIT3A = 's' / Time unit
CRPIX3A = 1.0 / Pixel coordinate at ref point
OBSGEO-B= -24.6157 / [deg] Tel geodetic latitute (=North)+
OBSGEO-L= -70.3976 / [deg] Tel geodetic longitude (=East)+
OBSGEO-H= 2530.0000 / [m] Tel height above reference ellipsoid
CRDER3  = 0.0819 / random error in timings from fit
CSYER3  = 0.0100 / absolute time error
PC1_1   = 0.999999971570892 / WCS transform matrix element
PC1_2   = 0.000238449608932 / WCS transform matrix element
PC2_1   = -0.000621542859395 / WCS transform matrix element
PC2_2   = 0.999999806842218 / WCS transform matrix element
CDELT1  = -9.48575432499806E-5 / Axis scale at reference point
CDELT2  = 9.48683176211164E-5 / Axis scale at reference point
CDELT3  = 13.3629 / Axis scale at reference point
PV1_1   = 1. / ZPN linear term
PV1_3   = 42. / ZPN cubic term
"""

with warnings.catch_warnings():
    warnings.simplefilter('ignore', (VerifyWarning, FITSFixedWarning))
    WCS_TIME_CUBE = WCS(Header.fromstring(HEADER_TIME_CUBE, sep='\n'))


def test_time_cube():

    # Spectral cube with a weird axis ordering

    wcs = WCS_TIME_CUBE

    assert wcs.pixel_n_dim == 3
    assert wcs.world_n_dim == 3
    assert wcs.array_shape == (11, 2048, 2048)
    assert wcs.pixel_shape == (2048, 2048, 11)
    assert wcs.world_axis_physical_types == ['pos.eq.dec', 'pos.eq.ra', 'time']
    assert wcs.world_axis_units == ['deg', 'deg', 's']
    assert wcs.pixel_axis_names == ['', '', '']
    assert wcs.world_axis_names == ['', '', '']

    assert_equal(wcs.axis_correlation_matrix, [[True, True, False],
                                               [True, True, False],
                                               [False, False, True]])

    components = wcs.world_axis_object_components
    assert components[0] == ('celestial', 1, 'spherical.lat.degree')
    assert components[1] == ('celestial', 0, 'spherical.lon.degree')
    assert components[2][:2] == ('time', 0)
    assert callable(components[2][2])

    assert wcs.world_axis_object_classes['celestial'][0] is SkyCoord
    assert wcs.world_axis_object_classes['celestial'][1] == ()
    assert isinstance(wcs.world_axis_object_classes['celestial'][2]['frame'], ICRS)
    assert wcs.world_axis_object_classes['celestial'][2]['unit'] is u.deg

    assert wcs.world_axis_object_classes['time'][0] is Time
    assert wcs.world_axis_object_classes['time'][1] == ()
    assert wcs.world_axis_object_classes['time'][2] == {}
    assert callable(wcs.world_axis_object_classes['time'][3])

    assert_allclose(wcs.pixel_to_world_values(-449.2, 2955.6, 0),
                    (14.8289418840003, 2.01824372640628, 2375.341))

    assert_allclose(wcs.array_index_to_world_values(0, 2955.6, -449.2),
                    (14.8289418840003, 2.01824372640628, 2375.341))

    assert_allclose(wcs.world_to_pixel_values(14.8289418840003, 2.01824372640628, 2375.341),
                    (-449.2, 2955.6, 0))
    assert_equal(wcs.world_to_array_index_values(14.8289418840003, 2.01824372640628, 2375.341),
                 (0, 2956, -449))

    # High-level API

    coord, time = wcs.pixel_to_world(29, 39, 44)
    assert isinstance(coord, SkyCoord)
    assert isinstance(coord.frame, ICRS)
    assert_allclose(coord.ra.deg, 1.7323356692202325)
    assert_allclose(coord.dec.deg, 14.783516054817797)
    assert isinstance(time, Time)
    assert_allclose(time.mjd, 54746.03429755324)

    coord, time = wcs.array_index_to_world(44, 39, 29)
    assert isinstance(coord, SkyCoord)
    assert isinstance(coord.frame, ICRS)
    assert_allclose(coord.ra.deg, 1.7323356692202325)
    assert_allclose(coord.dec.deg, 14.783516054817797)
    assert isinstance(time, Time)
    assert_allclose(time.mjd, 54746.03429755324)

    x, y, z = wcs.world_to_pixel(coord, time)
    assert_allclose(x, 29.)
    assert_allclose(y, 39.)
    assert_allclose(z, 44.)

    # Order of world coordinates shouldn't matter
    x, y, z = wcs.world_to_pixel(time, coord)
    assert_allclose(x, 29.)
    assert_allclose(y, 39.)
    assert_allclose(z, 44.)

    i, j, k = wcs.world_to_array_index(coord, time)
    assert_equal(i, 44)
    assert_equal(j, 39)
    assert_equal(k, 29)

    # Order of world coordinates shouldn't matter
    i, j, k = wcs.world_to_array_index(time, coord)
    assert_equal(i, 44)
    assert_equal(j, 39)
    assert_equal(k, 29)

###############################################################################
# The following tests are to make sure that Time objects are constructed
# correctly for a variety of combinations of WCS keywords
###############################################################################


HEADER_TIME_1D = """
SIMPLE  = T
BITPIX  = -32
NAXIS   = 1
NAXIS1  = 2048
TIMESYS = 'UTC'
TREFPOS = 'TOPOCENT'
MJDREF  = 50002.6
CTYPE1  = 'UTC'
CRVAL1  = 5
CUNIT1  = 's'
CRPIX1  = 1.0
CDELT1  = 2
OBSGEO-L= -20
OBSGEO-B= -70
OBSGEO-H= 2530
"""

@pytest.fixture
def header_time_1d():
    return Header.fromstring(HEADER_TIME_1D, sep='\n')


def assert_time_at(header, position, jd1, jd2, scale, format):
    wcs = WCS(header)
    time = wcs.pixel_to_world(position)
    assert_allclose(time.jd1, jd1, rtol=1e-10)
    assert_allclose(time.jd2, jd2, rtol=1e-10)
    assert time.format == format
    assert time.scale == scale


@pytest.mark.parametrize('scale', ('tai', 'tcb', 'tcg', 'tdb', 'tt', 'ut1', 'utc', 'local'))
def test_time_1d_values(header_time_1d, scale):

    # Check that Time objects are instantiated with the correct values,
    # scales, and formats.

    header_time_1d['CTYPE1'] = scale.upper()
    assert_time_at(header_time_1d, 1, 2450003, 0.1 + 7 / 3600 / 24, scale, 'mjd')


def test_time_1d_values_gps(header_time_1d):
    # Special treatment for GPS scale
    header_time_1d['CTYPE1'] = 'GPS'
    assert_time_at(header_time_1d, 1, 2450003, 0.1 + (7 + 19) / 3600 / 24, 'tai', 'mjd')


def test_time_1d_values_deprecated(header_time_1d):
    # Deprecated (in FITS) scales
    header_time_1d['CTYPE1'] = 'TDT'
    assert_time_at(header_time_1d, 1, 2450003, 0.1 + 7 / 3600 / 24, 'tt', 'mjd')
    header_time_1d['CTYPE1'] = 'IAT'
    assert_time_at(header_time_1d, 1, 2450003, 0.1 + 7 / 3600 / 24, 'tai', 'mjd')
    header_time_1d['CTYPE1'] = 'GMT'
    assert_time_at(header_time_1d, 1, 2450003, 0.1 + 7 / 3600 / 24, 'utc', 'mjd')
    header_time_1d['CTYPE1'] = 'ET'
    assert_time_at(header_time_1d, 1, 2450003, 0.1 + 7 / 3600 / 24, 'tt', 'mjd')


@pytest.mark.parametrize('scale', ('tai', 'tcb', 'tcg', 'tdb', 'tt', 'ut1', 'utc'))
def test_time_1d_roundtrip(header_time_1d, scale):

    # Check that coordinates round-trip

    pixel_in = np.arange(3, 10)

    header_time_1d['CTYPE1'] = scale.upper()
    wcs = WCS(header_time_1d)

    # Simple test
    time = wcs.pixel_to_world(pixel_in)
    pixel_out = wcs.world_to_pixel(time)
    assert_allclose(pixel_in, pixel_out)

    # Test with an intermediate change to a different scale/format
    time = wcs.pixel_to_world(pixel_in).tdb
    time.format = 'isot'
    pixel_out = wcs.world_to_pixel(time)
    assert_allclose(pixel_in, pixel_out)


def test_time_1d_high_precision(header_time_1d):

    # Case where the MJDREF is split into two for high precision
    del header_time_1d['MJDREF']
    header_time_1d['MJDREFI'] = 52000.
    header_time_1d['MJDREFF'] = 1e-11

    wcs = WCS(header_time_1d)
    time = wcs.pixel_to_world(10)

    # Here we have to use a very small rtol to really test that MJDREFF is
    # taken into account
    assert_allclose(time.jd1, 2452001.0, rtol=1e-12)
    assert_allclose(time.jd2, -0.5 + 25 / 3600 / 24 + 1e-11, rtol=1e-13)


def test_time_1d_location_geodetic(header_time_1d):

    # Make sure that the location is correctly returned (geodetic case)

    wcs = WCS(header_time_1d)
    time = wcs.pixel_to_world(10)

    lon, lat, alt = time.location.to_geodetic()

    # FIXME: alt won't work for now because ERFA doesn't implement the IAU 1976
    # ellipsoid (https://github.com/astropy/astropy/issues/9420)
    assert_allclose(lon.degree, -20)
    assert_allclose(lat.degree, -70)
    # assert_allclose(alt.to_value(u.m), 2530.)


@pytest.fixture
def header_time_1d_noobs():
    header = Header.fromstring(HEADER_TIME_1D, sep='\n')
    del header['OBSGEO-L']
    del header['OBSGEO-B']
    del header['OBSGEO-H']
    return header


def test_time_1d_location_geocentric(header_time_1d_noobs):

    # Make sure that the location is correctly returned (geocentric case)

    header = header_time_1d_noobs

    header['OBSGEO-X'] = 10
    header['OBSGEO-Y'] = -20
    header['OBSGEO-Z'] = 30

    wcs = WCS(header)
    time = wcs.pixel_to_world(10)

    x, y, z = time.location.to_geocentric()

    assert_allclose(x.to_value(u.m), 10)
    assert_allclose(y.to_value(u.m), -20)
    assert_allclose(z.to_value(u.m), 30)


def test_time_1d_location_geocenter(header_time_1d_noobs):

    header_time_1d_noobs['TREFPOS'] = 'GEOCENTER'

    wcs = WCS(header_time_1d_noobs)
    time = wcs.pixel_to_world(10)

    x, y, z = time.location.to_geocentric()

    assert_allclose(x.to_value(u.m), 0)
    assert_allclose(y.to_value(u.m), 0)
    assert_allclose(z.to_value(u.m), 0)


def test_time_1d_location_missing(header_time_1d_noobs):

    # Check what happens when no location is present

    wcs = WCS(header_time_1d_noobs)
    with pytest.warns(UserWarning,
                      match='Missing or incomplete observer location '
                            'information, setting location in Time to None'):
        time = wcs.pixel_to_world(10)

    assert time.location is None


def test_time_1d_location_incomplete(header_time_1d_noobs):

    # Check what happens when location information is incomplete

    header_time_1d_noobs['OBSGEO-L'] = 10.

    wcs = WCS(header_time_1d_noobs)
    with pytest.warns(UserWarning,
                      match='Missing or incomplete observer location '
                            'information, setting location in Time to None'):
        time = wcs.pixel_to_world(10)

    assert time.location is None


def test_time_1d_location_unsupported(header_time_1d):

    # Check what happens when TREFPOS is unsupported

    header_time_1d['TREFPOS'] = 'BARYCENTER'

    wcs = WCS(header_time_1d)
    with pytest.warns(UserWarning,
                      match="Observation location 'barycenter' is not "
                            "supported, setting location in Time to None"):
        time = wcs.pixel_to_world(10)

    assert time.location is None


def test_time_1d_unsupported_ctype(header_time_1d):

    # For cases that we don't support yet, e.g. UT(...), use Time and drop sub-scale

    # Case where the MJDREF is split into two for high precision
    header_time_1d['CTYPE1'] = 'UT(WWV)'

    wcs = WCS(header_time_1d)
    with pytest.warns(UserWarning,
                      match="Dropping unsupported sub-scale WWV from scale UT"):
        time = wcs.pixel_to_world(10)

    assert isinstance(time, Time)


###############################################################################
# Extra corner cases
###############################################################################


def test_unrecognized_unit():
    # TODO: Determine whether the following behavior is desirable
    wcs = WCS(naxis=1)
    with pytest.warns(UnitsWarning):
        wcs.wcs.cunit = ['bananas // sekonds']
        assert wcs.world_axis_units == ['bananas // sekonds']


def test_distortion_correlations():

    filename = get_pkg_data_filename('../../tests/data/sip.fits')
    with pytest.warns(FITSFixedWarning):
        w = WCS(filename)
    assert_equal(w.axis_correlation_matrix, True)

    # Changing PC to an identity matrix doesn't change anything since
    # distortions are still present.
    w.wcs.pc = [[1, 0], [0, 1]]
    assert_equal(w.axis_correlation_matrix, True)

    # Nor does changing the name of the axes to make them non-celestial
    w.wcs.ctype = ['X', 'Y']
    assert_equal(w.axis_correlation_matrix, True)

    # However once we turn off the distortions the matrix changes
    w.sip = None
    assert_equal(w.axis_correlation_matrix, [[True, False], [False, True]])

    # If we go back to celestial coordinates then the matrix is all True again
    w.wcs.ctype = ['RA---TAN', 'DEC--TAN']
    assert_equal(w.axis_correlation_matrix, True)

    # Or if we change to X/Y but have a non-identity PC
    w.wcs.pc = [[0.9, -0.1], [0.1, 0.9]]
    w.wcs.ctype = ['X', 'Y']
    assert_equal(w.axis_correlation_matrix, True)


def test_custom_ctype_to_ucd_mappings():

    wcs = WCS(naxis=1)
    wcs.wcs.ctype = ['SPAM']

    assert wcs.world_axis_physical_types == [None]

    # Check simple behavior

    with custom_ctype_to_ucd_mapping({'APPLE': 'food.fruit'}):
        assert wcs.world_axis_physical_types == [None]

    with custom_ctype_to_ucd_mapping({'APPLE': 'food.fruit', 'SPAM': 'food.spam'}):
        assert wcs.world_axis_physical_types == ['food.spam']

    # Check nesting

    with custom_ctype_to_ucd_mapping({'SPAM': 'food.spam'}):
        with custom_ctype_to_ucd_mapping({'APPLE': 'food.fruit'}):
            assert wcs.world_axis_physical_types == ['food.spam']

    with custom_ctype_to_ucd_mapping({'APPLE': 'food.fruit'}):
        with custom_ctype_to_ucd_mapping({'SPAM': 'food.spam'}):
            assert wcs.world_axis_physical_types == ['food.spam']

    # Check priority in nesting

    with custom_ctype_to_ucd_mapping({'SPAM': 'notfood'}):
        with custom_ctype_to_ucd_mapping({'SPAM': 'food.spam'}):
            assert wcs.world_axis_physical_types == ['food.spam']

    with custom_ctype_to_ucd_mapping({'SPAM': 'food.spam'}):
        with custom_ctype_to_ucd_mapping({'SPAM': 'notfood'}):
            assert wcs.world_axis_physical_types == ['notfood']


def test_caching_components_and_classes():

    # Make sure that when we change the WCS object, the classes and components
    # are updated (we use a cache internally, so we need to make sure the cache
    # is invalidated if needed)

    wcs = WCS_SIMPLE_CELESTIAL

    assert wcs.world_axis_object_components == [('celestial', 0, 'spherical.lon.degree'),
                                                ('celestial', 1, 'spherical.lat.degree')]

    assert wcs.world_axis_object_classes['celestial'][0] is SkyCoord
    assert wcs.world_axis_object_classes['celestial'][1] == ()
    assert isinstance(wcs.world_axis_object_classes['celestial'][2]['frame'], ICRS)
    assert wcs.world_axis_object_classes['celestial'][2]['unit'] is u.deg

    wcs.wcs.radesys = 'FK5'

    frame = wcs.world_axis_object_classes['celestial'][2]['frame']
    assert isinstance(frame, FK5)
    assert frame.equinox.jyear == 2000.

    wcs.wcs.equinox = 2010

    frame = wcs.world_axis_object_classes['celestial'][2]['frame']
    assert isinstance(frame, FK5)
    assert frame.equinox.jyear == 2010.


def test_sub_wcsapi_attributes():

    # Regression test for a bug that caused some of the WCS attributes to be
    # incorrect when using WCS.sub or WCS.celestial (which is an alias for sub
    # with lon/lat types).

    wcs = WCS_SPECTRAL_CUBE
    wcs.pixel_shape = (30, 40, 50)
    wcs.pixel_bounds = [(-1, 11), (-2, 18), (5, 15)]

    # Use celestial shortcut

    wcs_sub1 = wcs.celestial

    assert wcs_sub1.pixel_n_dim == 2
    assert wcs_sub1.world_n_dim == 2
    assert wcs_sub1.array_shape == (50, 30)
    assert wcs_sub1.pixel_shape == (30, 50)
    assert wcs_sub1.pixel_bounds == [(-1, 11), (5, 15)]
    assert wcs_sub1.world_axis_physical_types == ['pos.galactic.lat', 'pos.galactic.lon']
    assert wcs_sub1.world_axis_units == ['deg', 'deg']
    assert wcs_sub1.world_axis_names == ['Latitude', 'Longitude']

    # Try adding axes

    wcs_sub2 = wcs.sub([0, 2, 0])

    assert wcs_sub2.pixel_n_dim == 3
    assert wcs_sub2.world_n_dim == 3
    assert wcs_sub2.array_shape == (None, 40, None)
    assert wcs_sub2.pixel_shape == (None, 40, None)
    assert wcs_sub2.pixel_bounds == [None, (-2, 18), None]
    assert wcs_sub2.world_axis_physical_types == [None, 'em.freq', None]
    assert wcs_sub2.world_axis_units == ['', 'Hz', '']
    assert wcs_sub2.world_axis_names == ['', 'Frequency', '']

    # Use strings

    wcs_sub3 = wcs.sub(['longitude', 'latitude'])

    assert wcs_sub3.pixel_n_dim == 2
    assert wcs_sub3.world_n_dim == 2
    assert wcs_sub3.array_shape == (30, 50)
    assert wcs_sub3.pixel_shape == (50, 30)
    assert wcs_sub3.pixel_bounds == [(5, 15), (-1, 11)]
    assert wcs_sub3.world_axis_physical_types == ['pos.galactic.lon', 'pos.galactic.lat']
    assert wcs_sub3.world_axis_units == ['deg', 'deg']
    assert wcs_sub3.world_axis_names == ['Longitude', 'Latitude']

    # Now try without CNAME set

    wcs.wcs.cname = [''] * wcs.wcs.naxis
    wcs_sub4 = wcs.sub(['longitude', 'latitude'])

    assert wcs_sub4.pixel_n_dim == 2
    assert wcs_sub4.world_n_dim == 2
    assert wcs_sub4.array_shape == (30, 50)
    assert wcs_sub4.pixel_shape == (50, 30)
    assert wcs_sub4.pixel_bounds == [(5, 15), (-1, 11)]
    assert wcs_sub4.world_axis_physical_types == ['pos.galactic.lon', 'pos.galactic.lat']
    assert wcs_sub4.world_axis_units == ['deg', 'deg']
    assert wcs_sub4.world_axis_names == ['', '']
