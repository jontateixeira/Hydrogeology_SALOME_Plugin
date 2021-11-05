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
# This file is a TUI example to generated automatically a real geology
# model from horizons using SALOME python functionality
#
# Note: This TUI can be extended to add several other layers separately 
# and then merge them to build a unique model.
# ======================================================================




import numpy as np
import shapefile # pyshp
from matplotlib import path
import matplotlib.pyplot as plt
import scipy.interpolate as inter
import hydrogeo_salome as hgs
from hydrogeo_salome import utilities as utils

# Open shapefile
sf = shapefile.Reader("C:\DFiles\Projects\SalomePluginsDev\HydrogeologySalome\data\TikunaAquifer.shp")

# Get points ~ model limits must have only one shape!!
shp = sf.shapes()[0]

# Collect points
pts = np.asarray(shp.points)

## used out of salome interface
# plt.plot(pts[:, 0], pts[:, 1], '-o')
# plt.show()

# discretization of grid
dx = 5000  # dx ~ 5km
dy = 5000  # dy ~ 5km
nz = 4
x = np.linspace(shp.bbox[0], shp.bbox[2], int(
    np.floor((shp.bbox[2]-shp.bbox[0])/dx)))
y = np.linspace(shp.bbox[1], shp.bbox[3], int(
    np.floor((shp.bbox[3]-shp.bbox[1])/dy)))
z = np.linspace(0, 1, nz+1)
(nodes, cells) = utils.CartGrid(x, y, z)

cell_center = np.zeros((cells.shape[0], 3))
for c in range(cells.shape[0]):
    cell_center[c, :] = np.mean(nodes[cells[c, :], :], axis=0)

utils.write_unv('gridbase.unv', nodes, cells + 1)


p = path.Path(pts)
msk = p.contains_points(cell_center[:, [0, 1]])
cnodes = cells[msk]
vnodes = np.unique(cnodes.reshape(cnodes.size))
idx = np.zeros((int(vnodes.max()+1),))
idx[vnodes] = np.arange(0, vnodes.size)
vert = nodes[vnodes]
hexa = np.reshape(idx[cnodes].ravel(), (cnodes.shape[0], 8))

## used out of salome interface
# # plot nodes
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.plot3D(vert[:, 0], vert[:, 1], vert[:, 2], 'r.')

utils.write_unv('cube-1.unv', vert, np.int64(hexa) + 1)

# top horizon
top = vert[:, -1] == 1
D = np.loadtxt('"C:\DFiles\Projects\SalomePluginsDev\HydrogeologySalome\data\Tikuna_top_horizon.txt', 
               skiprows=1, usecols=[1, 2, 3])
xt = D[:, 0]
xx = [np.min(x), np.max(x)]
yt = D[:, 1]
yy = [np.min(y), np.max(y)]
zt = D[:, 2]

# base horizon
base = vert[:, -1] == 0
D = np.loadtxt('"C:\DFiles\Projects\SalomePluginsDev\HydrogeologySalome\data\Tikuna_base_horizon.txt', 
               skiprows=1, usecols=[1, 2, 3])
xb = D[:, 0]
xx = [np.min(x), np.max(x)]
yb = D[:, 1]
yy = [np.min(y), np.max(y)]
zb = D[:, 2]

# interpolate function
top_fun = inter.Rbf(xt, yt, zt, function='linear', smooth=100)
base_fun = inter.Rbf(xb, yb, zb, function='linear', smooth=100

# create aquifer model
mesh = hgs.macros.CreateMeshFromTopBase(vert, hexa, top, base)

# export grid
utils.write_coords_lnods('aquifer.unv', mesh)
# utils.write_vtk('aquifer.unv', mesh)
# utils.write_mesh('aquifer.unv', mesh)
