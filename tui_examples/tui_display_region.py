#!/usr/bin/env python

# Copyright (C) 2018-2020
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
#
#
# Main authors: Jonathan Teixeira (https://github.com/jontateixeira)
#

# ======================================================================
# This file is a TUI example to display some regions from shapefile 
# using SALOME python functionality
#
# Note: This TUI can be extended to add several other layers separately 
# and then merge them to build a unique model.
# ======================================================================

import hydrogeo_salome as hgs

# shapefile
shp = "C:\DFiles\Projects\SalomePluginsDev\HydrogeologySalome\data\outcrops_simp.shp")
closed = True # all shapes are closed polygons

# read abd display shapes as polylines
hgs.macros.CreatePolylinesFromShapefile(shp, closed)