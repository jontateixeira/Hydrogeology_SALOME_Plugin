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
