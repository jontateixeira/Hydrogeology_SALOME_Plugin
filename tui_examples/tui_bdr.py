#!/usr/bin/env python

# Copyright (c) 2017-2021 JCT
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# Main authors: JCT ~ Jonathan Teixeira (https://github.com/jontateixeira)
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
