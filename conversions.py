###############################################################################
# $Id$
#
# Project:	GDAL2Tiles, Google Summer of Code 2007 & 2008
#           Global Map Tiles Classes
# Purpose:	Convert a raster into TMS tiles, create KML SuperOverlay EPSG:4326,
#			generate a simple HTML viewers based on Google Maps and OpenLayers
# Author:	Klokan Petr Pridal, klokan at klokan dot cz
# Web:		http://www.klokan.cz/projects/gdal2tiles/
#
###############################################################################
# Copyright (c) 2008 Klokan Petr Pridal. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################

# This is a modified version of the above mentioned program code 

import math

tileSize = 256
initialResolution = 2 * math.pi * 6378137 / tileSize # 156543.03392804062 for tileSize 256 pixels
originShift = 2 * math.pi * 6378137 / 2.0 # 20037508.342789244

# Converts given lat/lon in WGS84 Datum to XY in Spherical Mercator EPSG:900913
def LatLonToMeters(lat, lon ):
    mx = lon * originShift / 180.0
    my = math.log(math.tan((90.0 + lat) * math.pi / 360.0)) / (math.pi / 180.0)

    my = my * originShift / 180.0
    return mx, my

# Converts XY point from Spherical Mercator EPSG:900913 to lat/lon in WGS84 Datum
def MetersToLatLon(mx, my ):
    lon = (mx / originShift) * 180.0
    lat = (my / originShift) * 180.0

    lat = 180 / math.pi * (2 * math.atan( math.exp( lat * math.pi / 180.0)) - math.pi / 2.0)

    return lat, lon

# Converts pixel coordinates in given zoom level of pyramid to EPSG:900913
def PixelsToMeters(px, py, zoom):
    res = Resolution(zoom)
    mx = px * res - originShift
    my = py * res - originShift

    return mx, my

# Converts EPSG:900913 to pyramid pixel coordinates in given zoom level
def MetersToPixels(mx, my, zoom):
    res = Resolution(zoom)
    px = (mx + originShift) / res
    py = (my + originShift) / res
    return px, py

# Resolution (meters/pixel) for given zoom level (measured at Equator)
def Resolution(zoom):
    return initialResolution / (2**zoom)
