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
# This file is a TUI example to assign boundary condition on the model 
# using SALOME python functionality
#
# Note: This TUI can be extended to add several other boundary conditions.
# ======================================================================

import numpy as np
from hydrogeo_salome import macros

# get grid model: name 'Grid'
o = salome.myStudy.FindObjectByPath('/Mesh/Grid').GetObject()
m = o.GetMesh()

# add boundary condition
mesh = macros.CreateBorderGroupsFromRegions(m, [np.asarray([[0,0],[0.1,0],[0.1,0.1],[0,0.1]])], (0.05, 0.08), 'bdr')

# update obj. browser
salome.sg.updateObjBrowser()
