#!/usr/bin/env python

r"""
GeoClaw util Module  `$CLAW/geoclaw/src/python/geoclaw/util.py`

Module provides provides utility functions.


:Functions:

 - dms2decimal - Convert (degrees, minutes, seconds) to decimal degrees
 - dist_meters2latlong - Convert dx, dy distance in meters to degrees
 - dist_latlong2meters - Convert dx, dy distance in degrees to meters
 - haversine - Calculate the haversine based great circle distance
 - inv_haversine - Inverts the haversine distance
 - fetch_noaa_tide_data - Fetches water levels and tide predictions
***Note: routine fetch_noaa_tide_data has been moved to tide module in geoclaw but can still be called in this module as an imported function
"""

from __future__ import absolute_import
from __future__ import print_function
from clawpack.geoclaw.tide import fetch_noaa_tide_data

import numpy

# ==============================================================================
#  Constants
# ==============================================================================
from clawpack.geoclaw.data import Rearth, DEG2RAD, RAD2DEG, LAT2METER

# ==============================================================================
#  Functions for calculating Distances
# ==============================================================================
def dms2decimal(d,m,s,coord='N'):
    r"""Convert coordinates in (degrees, minutes, seconds) to decimal form.  
    
    If coord == 'S' or coord == 'W' then value is negated too.

    :Example: 

        >>> topotools.dms2decimal(7,30,36,'W')
        -7.51

    (Note that you might want to add 360 to resulting W coordinate
    if using E coordinates everywhere in a computation spanning date line.)

    :Returns: float

    """

    deg = d + m / 60.0 + s / 3600.0
    if coord in ['S','W']:
        deg = -deg

    return deg


def dist_latlong2meters(dx, dy, latitude=0.0):
    """Convert distance from degrees longitude-latitude to meters.

    Takes the distance described by *dx* and *dy* in degrees and converts it into
    distances in meters.

    returns (float, float) 

    """

    dym = Rearth * DEG2RAD * dy
    dxm = Rearth * numpy.cos(latitude * DEG2RAD) * dx * DEG2RAD

    return dxm,dym


def dist_meters2latlong(dx, dy, latitude=0.0):
    """Convert distance from meters to degrees of longitude-latitude.

    Takes the distance described by *dx* and *dy* in meters and converts it into
    distances in the longitudinal and latitudinal directions in degrees.  

    returns (float, float)

    """

    dxd = dx / (Rearth * numpy.cos(latitude * DEG2RAD)) * RAD2DEG
    dyd = dy * RAD2DEG / Rearth

    return dxd, dyd


def haversine(x0, y0, x1=None, y1=None, units='degrees'):

    """
    x0,y0 is assumed to be a point (or an array with the same shapes as x1,y1)
    x1,y1 is a point or two arrays of points (of the same dimension)
    returns array with same shape as x1 and y1 containing distance of each point
    from (x0,y0).

    For backward compatibility, also allows x0,y0 to be 2-tuples specifying
    two points, but this is not suggested since the notation is not consistent.
    """
    
    if x1 is None:
        # for backward compatibility, assume in this case that x0 and y0 
        # are tuples for the two desired points:
        assert len(x0)==len(y0)==2, "*** Unexpected input"
        x1,y1 = y0
        x0,y0 = x0

    if units == 'degrees':
        # convert to radians:
        x0 = x0*DEG2RAD
        y0 = y0*DEG2RAD
        x1 = x1*DEG2RAD
        y1 = y1*DEG2RAD

    dx = x1 - x0
    dy = y1 - y0

    # angle subtended by two points, using Haversine formula:
    dsigma = 2.0 * numpy.arcsin( numpy.sqrt( numpy.sin(0.5 * dy)**2   \
            + numpy.cos(y0) * numpy.cos(y1) * numpy.sin(0.5 * dx)**2))

    return Rearth * dsigma


def inv_haversine(d,x1,y1,y2,Rsphere=Rearth,units='degrees'):
    r"""Invert the Haversine function to find dx given a distance and point.


    Invert the haversine function to find dx given distance d and (x1,y1) and y2.
    The corresponding x2 can be x1+dx or x1-dx.
    May return NaN if no solution.
    """

    if units=='degrees':
        # convert to radians:
        x1 = x1 * RAD2DEG
        y1 = y1 * RAD2DEG
        y2 = y2 * RAD2DEG
    elif units != 'radians':
        raise Exception("unrecognized units")
    dsigma = d / Rsphere
    cos_dsigma = (numpy.cos(dsigma) - numpy.sin(y1)*numpy.sin(y2)) / (numpy.cos(y1)*numpy.cos(y2))
    dx = numpy.arccos(cos_dsigma)
    if units=='degrees':
        dx = dx * RAD2DEG
    return dx


def bearing(x0, y0, x1, y1, units='degrees', bearing_units='degrees'):

    """
    Compute the bearing from (x0,y0) to (x1,y1), i.e., the angle clockwise from
    due North of the great circle path from point 0 to 1.  

    The value returned is thus between 0 and 360 if bearing_units='degrees',
    or between 0 and 2*pi if bearing_units='radians'.

    Note: If using this to initialize a radially-symmetric 2d velocity on the
    sphere based on a radial velocity U(r), symmetric about (x0, y0), set:
        # lat-long assumed to be in degrees, r in meters
        r = haversine(x0,y0,x,y)
        beta = bearing(x0,y0,x,y,bearing_units='radians')
        u = U(r) * sin(beta)  # beta measured from North!
        v = U(r) * cos(beta)
    """
    from math import atan2, degrees

    if units == 'degrees':
        # convert to radians:
        x0 = x0*DEG2RAD
        y0 = y0*DEG2RAD
        x1 = x1*DEG2RAD
        y1 = y1*DEG2RAD
    elif units != 'radians':
        raise Exception("unrecognized units")

    dx = x1 - x0
    dy = y1 - y0
    xx = numpy.cos(y0)*numpy.sin(y1) - numpy.sin(y0)*numpy.cos(y1)*numpy.cos(dx)
    yy = numpy.sin(dx) * numpy.cos(y1)
    b = atan2(yy, xx)   # in radians from North (between -pi and pi)

    beta = (degrees(b) + 360) % 360  # convert to degrees clockwise from North

    if bearing_units == 'radians':
        beta = radians(beta)  # convert to radians clockwise (0 to 2*pi)

    elif bearing_units != 'degrees':
        raise Exception("unrecognized bearing_units")

    return b
    
