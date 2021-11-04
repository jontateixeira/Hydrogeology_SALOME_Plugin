# Copyright (C) 2017-2020
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
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
#
# Author : Jonathan Teixeira (jonathan.teixeira@ufpe.br)
#
"""
This file contains utility functions for interacting with Salome
"""

# plugin imports
from . import utilities as utils

# python imports
import scipy.interpolate as inter
import time
import numpy as np
import logging
LOG = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Local CONST.
DIRECTION = {"west": 0, "WEST": 0, "XMIN": 0, "xmin": 0, "left": 0, "LEFT": 0,
             "east": 1, "EAST": 1, "XMAX": 1, "xmax": 1, "right": 1,
             "RIGHT": 1,
             "north": 2, "NORTH": 2, "YMAX": 2, "ymax": 2, "back": 2,
             "BACK": 2,
             "south": 3, "SOUTH": 3, "YMIN": 3, "ymin": 3, "front": 3,
             "FRONT": 3,
             "upward": 4, "UPWARD": 4, "MAXZ": 4, "zmax": 4, "top": 4,
             "TOP": 4,
             "downward": 5, "DOWNWARD": 5, "ZMIN": 5, "zmin": 5, "bottom": 5,
             "BOTTOM": 5}

SIDE = {0: "Westside", 1: "Eastside", 2: "Northside",
        3: "Southside", 4: "Topside", 5: "Bottomside"}
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------


def PrintMeshInfo(theMesh):
    """Print mesh information"""
    aMesh = theMesh.GetMesh()
    print("Information about mesh:")
    print("Number of nodes       : {}".format(aMesh.NbNodes()))
    print("Number of faces       : {}".format(aMesh.NbFaces()))
    print("Number of hexahedron  : {}".format(aMesh.NbHexas()))
    pass


# ------------------------------------------------------------------------------
def LoadSMesh(fname: str):
    """Creates a SMESH object importing from file data"""

    # salome imports
    import SMESH
    import SALOMEDS
    from salome.smesh import smeshBuilder

    LOG.info("Loading mesh %s", fname)
    (OK, EMPTY, WARN, SKIPED, WARN2,
        FAILED) = SMESH.DriverMED_ReadStatus._items

    # initialize smesh
    smesh = smeshBuilder.New()

    # get mesh from format
    mesh_format = fname[-4:]
    if mesh_format.lower() == ".med":
        (M, status) = smesh.CreateMeshesFromMED(fname)
        # get mesh obj
        M = M[0]
    elif mesh_format.lower() == "sauv":
        (M, status) = smesh.CreateMeshesFromSAUV(fname)
        # get mesh obj
        M = M[0]
    elif mesh_format.lower() == "cgns":
        (M, status) = smesh.CreateMeshesFromCGNS(fname)
        # get mesh obj
        M = M[0]
    elif mesh_format.lower() == ".unv":
        M = smesh.CreateMeshesFromUNV(fname)
        status = OK
    elif mesh_format.lower() == ".stl":
        M = smesh.CreateMeshesFromSTL(fname)
        status = OK
    else:
        LOG.critical('Unsupported file extension: "%s"', mesh_format)

    if status != OK:
        LOG.warning("Something wrong when loading mesh from %s file:", fname)
    PrintMeshInfo(M)
    LOG.info("Done!")

    return M


# ------------------------------------------------------------------------------
def CreateBorderGroups(init_mesh):
    """Create boundary groups on mesh object"""

    import SMESH
    import SALOMEDS

    # -----------
    ##
    # 2D from 3D
    ##
    # -----------
    dim = SMESH.BND_2DFROM3D

    # boundary group in this mesh
    LOG.info("Setting boundary faces in %s", init_mesh.GetName())
    groupName = "Boundary_Faces"
    nbfaces, M, new_group = init_mesh.MakeBoundaryElements(dim, groupName)

    # get boundary faces
    bfaces = M.GetGroupByName('Boundary_Faces')[0]
    bfacesId = bfaces.GetListOfID()

    # collect centroids and normals
    bfaces_centroids = np.array([M.BaryCenter(f) for f in bfacesId])
    bfaces_normals = np.array([M.GetFaceNormal(f, True) for f in bfacesId])

    bfacesId = np.array(bfacesId, dtype=int)
    box = M.GetBoundingBox()

    # faces |_Ox
    faces_mask = bfaces_centroids[:, 0] == box.minX
    if np.sum(faces_mask) > 0:
        gface_ymin = M.CreateEmptyGroup(SMESH.FACE, "Westside_Faces")
        ii = list(np.unique(bfacesId[faces_mask]))
        indexes = [int(i) for i in ii]
        gface_ymin.Add(indexes)
    else:
        faces_mask = (bfaces_normals[:, 0] < 0) & (
            np.argmax(np.abs(bfaces_normals), axis=1) == 0)
        if np.sum(faces_mask) > 0:
            gface_ymin = M.CreateEmptyGroup(SMESH.FACE, "Westside_Faces")
            ii = list(np.unique(bfacesId[faces_mask]))
            indexes = [int(i) for i in ii]
            gface_ymin.Add(indexes)
        else:
            LOG.warning('Westside Faces not found')
    gface_ymin.SetColorNumber(1)
    gface_ymin.SetColor( SALOMEDS.Color( 1, 0, 0 ))

    faces_mask = bfaces_centroids[:, 0] == box.maxX
    if np.sum(faces_mask) > 0:
        gface_ymax = M.CreateEmptyGroup(SMESH.FACE, "Eastside_Faces")
        ii = list(np.unique(bfacesId[faces_mask]))
        indexes = [int(i) for i in ii]
        gface_ymax.Add(indexes)
    else:
        faces_mask = (bfaces_normals[:, 0] > 0) & (
            np.argmax(np.abs(bfaces_normals), axis=1) == 0)
        if np.sum(faces_mask) > 0:
            gface_ymax = M.CreateEmptyGroup(SMESH.FACE, "Eastside_Faces")
            ii = list(np.unique(bfacesId[faces_mask]))
            indexes = [int(i) for i in ii]
            gface_ymax.Add(indexes)
        else:
            LOG.warning('Eastside Faces not found')
    gface_ymax.SetColorNumber(2)
    gface_ymax.SetColor( SALOMEDS.Color(1, 1, 0))

    # faces |_Oy
    faces_mask = bfaces_centroids[:, 1] == box.minY
    if np.sum(faces_mask) > 0:
        gface_ymin = M.CreateEmptyGroup(SMESH.FACE, "Southside_Faces")
        ii = list(np.unique(bfacesId[faces_mask]))
        indexes = [int(i) for i in ii]
        gface_ymin.Add(indexes)
    else:
        faces_mask = (bfaces_normals[:, 1] < 0) & (
            np.argmax(np.abs(bfaces_normals), axis=1) == 1)
        if np.sum(faces_mask) > 0:
            gface_ymin = M.CreateEmptyGroup(SMESH.FACE, "Southside_Faces")
            ii = list(np.unique(bfacesId[faces_mask]))
            indexes = [int(i) for i in ii]
            gface_ymin.Add(indexes)
        else:
            LOG.warning('Southside Faces not found')
    gface_ymin.SetColorNumber(3)
    gface_ymin.SetColor( SALOMEDS.Color(0, 1, 0))

    faces_mask = bfaces_centroids[:, 1] == box.maxY
    if np.sum(faces_mask) > 0:
        gface_ymax = M.CreateEmptyGroup(SMESH.FACE, "Northside_Faces")
        ii = list(np.unique(bfacesId[faces_mask]))
        indexes = [int(i) for i in ii]
        gface_ymax.Add(indexes)
    else:
        faces_mask = (bfaces_normals[:, 1] > 0) & (
            np.argmax(np.abs(bfaces_normals), axis=1) == 1)
        if np.sum(faces_mask) > 0:
            gface_ymax = M.CreateEmptyGroup(SMESH.FACE, "Northside_Faces")
            ii = list(np.unique(bfacesId[faces_mask]))
            indexes = [int(i) for i in ii]
            gface_ymax.Add(indexes)
        else:
            LOG.warning('Northside Faces not found')
    gface_ymax.SetColorNumber(4)
    gface_ymax.SetColor( SALOMEDS.Color(0, 1, 1))

    # faces |_Oz
    faces_mask = bfaces_centroids[:, -1] == box.minZ
    if np.sum(faces_mask) > 0:
        gface_zmin = M.CreateEmptyGroup(SMESH.FACE, "Bottomside_Faces")
        ii = list(np.unique(bfacesId[faces_mask]))
        indexes = [int(i) for i in ii]
        gface_zmin.Add(indexes)
    else:
        faces_mask = (bfaces_normals[:, -1] < 0) & (
            np.argmax(np.abs(bfaces_normals), axis=1) == 2)
        if np.sum(faces_mask) > 0:
            gface_zmin = M.CreateEmptyGroup(SMESH.FACE, "Bottomside_Faces")
            ii = list(np.unique(bfacesId[faces_mask]))
            indexes = [int(i) for i in ii]
            gface_zmin.Add(indexes)
        else:
            LOG.warning('Bottomside Faces not found')
    gface_zmin.SetColorNumber(5)
    gface_zmin.SetColor( SALOMEDS.Color( 1, 0, 1))

    faces_mask = bfaces_centroids[:, -1] == box.maxZ
    if np.sum(faces_mask) > 0:
        gface_zmax = M.CreateEmptyGroup(SMESH.FACE, "Topside_Faces")
        ii = list(np.unique(bfacesId[faces_mask]))
        indexes = [int(i) for i in ii]
        gface_zmax.Add(indexes)
    else:
        faces_mask = (bfaces_normals[:, -1] > 0) & (
            np.argmax(np.abs(bfaces_normals), axis=1) == 2)
        if np.sum(faces_mask) > 0:
            gface_zmax = M.CreateEmptyGroup(SMESH.FACE, "Topside_Faces")
            ii = list(np.unique(bfacesId[faces_mask]))
            indexes = [int(i) for i in ii]
            gface_zmax.Add(indexes)
        else:
            LOG.warning('Topside Faces not found')
    gface_zmax.SetColorNumber(6)
    gface_zmax.SetColor( SALOMEDS.Color(0, 0, 1))

    LOG.info("Done!")
    return M


# ------------------------------------------------------------------------------
def CreateBorderGroupsFromRegions(mesh, regions, dx, group_name, only_one_bface=False):
    """Create boundary groups on mesh object"""
    import SMESH
    import SALOMEDS
    from matplotlib import path

    # check if mesh has 'Boundary_Faces' group
    groups = mesh.GetGroups()
    bfaces = None
    for g in groups:
        if g.GetName() == 'Boundary_Faces':
            bfaces = g
            break

    if bfaces is None:
        dim = SMESH.BND_2DFROM3D

        # boundary group in this mesh
        LOG.info("Setting boundary faces in %s", mesh.GetName())
        groupName = "Boundary_Faces"
        nbfaces, mesh, new_group = mesh.MakeBoundaryElements(dim, groupName)

        # get boundary faces
        bfaces = mesh.GetGroupByName('Boundary_Faces')[0]

    bfacesId = bfaces.GetListOfID()
    nbfaces = len(bfacesId)

    # collect centroids and normals
    bfaces_centroids = np.array([mesh.BaryCenter(f) for f in bfacesId])
    bfacesId = np.array(bfacesId, dtype=int)
    ibfaces = np.arange(nbfaces)
    # msk = np.zeros((nbfaces,), dtype=bool)
    r = max(*dx)
    count = 0
    # create color scales
    col = np.random.uniform(0,1,3*len(regions))
    for region in regions:
        # make a path
        p = path.Path(region)
        msk = p.contains_points(bfaces_centroids[:, [0, 1]])
        # mark regions closed to region conform criterio (dx, dy)
        for p in region:
            dist = np.sqrt(np.sum((p - bfaces_centroids[:,:-1])*(p - bfaces_centroids[:,:-1]),axis=1))
            msk[dist < r] = True
        # collect bfaces
        bfaces_marked = ibfaces[msk]
        if only_one_bface: 
            # mark only the face with maximum z-coordinate
            for f in bfaces_marked:
                if msk[f]:
                    # mark faces with same x,y coordinates
                    b = np.all(bfaces_centroids[f,:-1] == bfaces_centroids[:,:-1], axis=1)
                    idx = ibfaces[b] # faces with same coordinates
                    imx = np.argmax(bfaces_centroids[idx,-1]) # index of maximum z
                    # unmark all
                    msk[idx] = False
                    # mark only bface at surface
                    msk[idx[imx]] = True
            bfaces_marked = ibfaces[msk]
        if len(bfaces_marked) > 0:
            LOG.info(f"Creating Group " + group_name + str(count))
            fgroup = mesh.CreateGroup(SMESH.FACE, group_name + str(count))
            ii = list(np.unique(bfacesId[bfaces_marked]))
            indexes = [int(i) for i in ii]
            fgroup.Add(indexes)
            count += 1
            fgroup.SetColorNumber(count)
            fgroup.SetColor(SALOMEDS.Color(col[3*(count-1)], col[3*(count-1)+1], col[3*(count-1)+2]))


# ------------------------------------------------------------------------------
def LoadFlowMeshNumpy(fname, min_thickness=5.0, auto_save=True):
    """
    Load IMEX flow model, based on coordinate and connections files, smoothing
    all faults grid and removing pinchouts in the mesh adding a minimal
    thickness. Returns a tuple (a ndarray coordinate, ndarray connectivities)
    """

    # %% procedures
    """
    1) collect grid info (nr of cells, nodes)
    2) align grid (by rotation) to cartesian coordinate system
    3) compute cells centroids and volume
    """

    tic = time.time()
    # load data
    LOG.debug("Loading files: %s {.coords, .lnods}", fname)
    d_nodes = np.loadtxt(fname + ".coords")
    d_cells = np.loadtxt(fname + ".lnods", dtype=int)

    if auto_save:
        utils.write_unv(fname + "_original.unv", d_nodes, d_cells)

    # extract basic info
    n_n, n_d = np.shape(d_nodes)
    n_c, n_conn = np.shape(d_cells)

    # minimum x and y (base vector)
    minx = np.argmin(d_nodes[:, 0])
    miny = np.argmin(d_nodes[:, 1])
    node = d_nodes[minx, 0:n_d-1]
    vbase = d_nodes[miny, 0:n_d-1] - d_nodes[minx, 0:n_d-1]

    # translate to origin (minimum x)
    d_nodes[:, 0:n_d-1] = d_nodes[:, 0:n_d-1] - node

    v = [1, 0]
    theta = np.arccos(vbase.dot(v)/np.sqrt(vbase.dot(vbase)))

    # rotate model (align to cartisian system)
    nodes = np.zeros_like(d_nodes)
    nodes[:, 0] = d_nodes[:, 0] * np.cos(theta) - d_nodes[:, 1] * np.sin(theta)
    nodes[:, 1] = d_nodes[:, 0] * np.sin(theta) + d_nodes[:, 1] * np.cos(theta)
    nodes[:, 2] = d_nodes[:, 2]

    if auto_save:
        utils.write_unv(fname + "_output.unv", nodes, d_cells)

    # compute cell centers and volume
    LOG.debug("Compute cell center and volume")
    cells_centroids = np.zeros((n_c, n_d))
    vol = np.zeros((n_c,))
    for c in range(n_c):
        cells_centroids[c, :] = np.mean(d_nodes[d_cells[c, :]-1, :], axis=0)
        vol[c] = utils.volume_hexahedron(d_nodes[d_cells[c, :]-1, :])

    L_x = np.max(nodes[:, 0]) - np.min(nodes[:, 0])
    L_y = np.max(nodes[:, 1]) - np.min(nodes[:, 1])

    idx = utils.find_indexes(vol > 0)
    cnodes = d_cells[idx[0]] - 1
    dx = np.abs(nodes[cnodes[0], 0] - nodes[cnodes[1], 0])
    dy = np.abs(nodes[cnodes[0], 1] - nodes[cnodes[2], 1])

    n_x = np.floor(L_x / dx)
    n_y = np.floor(L_y / dy)

    toc = time.time()

    print('-- Imported')
    print('   nodes: {}'.format(n_n))
    print('   cells: {}'.format(n_c))
    print('   azimuth: {}'.format(np.rad2deg(theta)+90))
    print('   number of cells on x-dir: {}'.format(n_x))
    print('   number of cells on y-dir: {}'.format(n_y))
    print('-- Elapsed in {} seconds'.format(toc-tic))

    # %%
    """
    grid flow settings:

    1) collect pillar nr and nodes in pillars
    2) mark top and bottom cells in pillars
    3) collecting nodes on top and bottom
    """
    tic = time.time()
    # -------------------------------------
    LOG.info('Counting pillars')
    # counting pillars
    idx = np.arange(0, n_n)
    n_pillar_nodes = []
    pillars_nodes = []
    layer_n = np.zeros((n_n,))
    pnodes = np.zeros((n_n,), dtype=bool)
    for n in idx:
        if pnodes[n]:
            continue
        pnodes[n] = True

        # diff of nodes (same pillar has dx=dy=0)
        dx = np.abs(nodes[n, :] - nodes[:, ])[:, 0:n_d-1]

        # check for pillar
        p = utils.find_indexes((dx[:, 0] < 1e-9) & (dx[:, 1] < 1e-9))
        # print(dx)

        if len(p) > 0:
            pillars_nodes.append(p)
            n_pillar_nodes.append(len(p))

            zmin = np.argmin(nodes[p, -1])
            zmax = np.argmax(nodes[p, -1])

            layer_n[p[zmin]] = -1
            layer_n[p[zmax]] = +1

            pnodes[p] = True

    toc = time.time()
    LOG.info(' number of pillars: %d', len(pillars_nodes))
    LOG.info('Elapsed in %f seconds', toc-tic)

    # -------------------------------------
    # mark top and bottom cells in pillars
    LOG.info('Collecting pillars info')
    tic = time.time()
    n_pillar = []
    pillars = []
    idx = np.arange(0, n_c)
    cells = np.zeros((n_c,), dtype=bool)
    dxyz = np.zeros((n_c, n_d))
    for n in idx:
        if cells[n]:
            continue

        cells[n] = True

        # diff of nodes (same pillar has dx=dy=0)
        dx = np.abs(cells_centroids[n, :] - cells_centroids[:, ])[:, 0:n_d-1]

        dxyz[n, 0] = np.abs(nodes[d_cells[n, 0], 0] - nodes[d_cells[n, 1], 0])
        dxyz[n, 1] = np.abs(nodes[d_cells[n, 0], 1] - nodes[d_cells[n, 2], 1])
        dxyz[n, 2] = np.abs(nodes[d_cells[n, 0], 2] - nodes[d_cells[n, 3], 2])

        # check for pillar
        p = utils.find_indexes((dx[:, 0] < 1e-9) & (dx[:, 1] < 1e-9))
        # print(dx)
        if len(p) > 0:
            pillars.append(p)
            n_pillar.append(len(p))
            cells[p] = True

    # mark cells on top and bot
    cells_pillar = np.zeros((n_c,))
    nr_pillar = np.zeros((n_c,))
    layer = np.zeros_like(nr_pillar)
    i = 0
    top, bot = 1, -1
    for p in pillars:
        i += 1
        n = len(p)
        cells_pillar[p] = n
        nr_pillar[p] = i
        zmin = np.argmin(cells_centroids[p, -1])
        zmax = np.argmax(cells_centroids[p, -1])
        layer[p[zmin]] = bot
        layer[p[zmax]] = top

    # -------------------------------------
    # nodes on top and bot
    tnodes = np.zeros((len(pillars_nodes), n_d))
    bnodes = np.zeros_like(tnodes)
    for n in range(len(pillars_nodes)):
        nodes_on_pillar = pillars_nodes[n]

        if len(nodes_on_pillar) > 1:
            # get nodes marked on top
            idx = utils.find_indexes(layer_n[nodes_on_pillar] == top)
            if len(idx) > 1:
                tnodes[n, :] = np.mean(nodes[idx, :], axis=0)
            else:
                zmax = np.argmax(nodes[nodes_on_pillar, -1])
                tnodes[n, :] = nodes[nodes_on_pillar[zmax], :]

            # get nodes marked on bottom
            idx = utils.find_indexes(layer_n[nodes_on_pillar] == bot)
            if len(idx) > 1:
                bnodes[n, :] = np.mean(nodes[idx, :], axis=0)
            else:
                zmin = np.argmin(nodes[nodes_on_pillar, -1])
                bnodes[n, :] = nodes[nodes_on_pillar[zmin], :]
        else:
            LOG.warning('Pillar #%d with one node!!', n)
            # get nodes marked on top
            tnodes[n, :] = nodes[layer_n[nodes_on_pillar], :]

            # get nodes marked on bottom
            bnodes[n, :] = nodes[layer_n[nodes_on_pillar], :]
    toc = time.time()
    LOG.info('Elapsed in %f seconds', toc-tic)

    # # plot fitted points
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.scatter(tnodes[:, 0], tnodes[:, 1], tnodes[:, 2], marker='o')
    # ax.scatter(bnodes[:, 0], bnodes[:, 1], bnodes[:, 2], marker='.')
    # plt.show()

    # %%
    """
    create the grid
    """
    LOG.info('Generating grid: Vertices and Elements')
    tic = time.time()
    # construct grid
    x = np.linspace(0, L_x, np.int64(n_x) + 1)
    y = np.linspace(0, L_y, np.int64(n_y) + 1)
    n_z = np.int64(np.floor(np.mean(cells_pillar))) - 1
    z = np.linspace(0, n_z, np.int64(n_z)+1)

    vertices = np.array([[i, j, k] for k in z for j in y for i in x])
    # mark top and bottom vertices
    mrk = np.zeros((vertices.shape[0]))
    mrk[utils.find_indexes(vertices[:, -1] == 0)] = -1
    mrk[utils.find_indexes(vertices[:, -1] == n_z)] = +1
    toc = time.time()
    LOG.info(' vertices creation elapsed in %f seconds', toc-tic)

    # --------------------------------------
    # interpolation process
    tic = time.time()
    ztop = inter.Rbf(tnodes[:, 0], tnodes[:, 1], tnodes[:, 2],
                     function='linear', smooth=100)
    vertices[mrk > 0, -1] = ztop(vertices[mrk > 0, 0], vertices[mrk > 0, 1])
    zbot = inter.Rbf(bnodes[:, 0], bnodes[:, 1], bnodes[:, 2],
                     function='linear', smooth=100)
    vertices[mrk < 0, -1] = zbot(vertices[mrk < 0, 0], vertices[mrk < 0, 1])

    # # plot fitted points
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.scatter(vertices[mrk > 0, 0], vertices[mrk > 0, 1],
    #            vertices[mrk > 0, 2], marker='o')
    # ax.scatter(vertices[mrk < 0, 0], vertices[mrk < 0, 1],
    #            vertices[mrk < 0, 2], marker='.')
    # plt.show()

    # remove pinch-outs (pillar with same nodes coordinate)
    ncheck = np.zeros((vertices.shape[0],), dtype=bool)
    dz = np.mean(dxyz[dxyz[:, -1] > 0], axis=0)[-1]
    if min_thickness < 1e-9:
        min_thickness = dz
    for i in range(vertices.shape[0]):
        if ncheck[i]:
            continue
        ncheck[i] = True

        # diff of nodes (same pillar has dx=dy=0)
        dx = np.abs(vertices[i, :] - vertices[:, ])[:, 0:n_d-1]

        # check for pillar (nodes in same x and y-coordinates)
        p = np.array(utils.find_indexes((dx[:, 0] < 1e-9) & (dx[:, 1] < 1e-9)))
        # print(dx)
        if len(p) > 0:
            marked = mrk[p]
            # split internal and top/bot (marked) pillar nodes
            unmarked = p[utils.find_indexes(marked == 0)]
            marked = p[utils.find_indexes(marked != 0)]

            # horizons
            zmax = np.max(vertices[marked, -1])
            zmin = np.min(vertices[marked, -1])

            # sorted index (unmarked)
            if np.abs(zmax-zmin) > dz:
                # z = vertices[unmarked, -1]
                # ind = np.unravel_index(np.argsort(z, axis=None), z.shape)[0]
                z_linspace = np.linspace(zmin, zmax, len(p))
                z_linspace = z_linspace[1:len(p)-1:1]
                # for v in range(len(unmarked)):
                #     z[ind[v]] = z_linspace[v]
                # vertices[unmarked, -1] = z
                vertices[unmarked, -1] = z_linspace
            else:
                marked = mrk[p]
                # split internal and top (marked) pillar nodes
                unmarked = p[utils.find_indexes(marked < 1)]
                marked = p[utils.find_indexes(marked > 0)]

                # boundary horizon
                zmax = np.max(vertices[marked, -1])
                # z = vertices[unmarked, -1]
                # ind = np.unravel_index(np.argsort(z, axis=None), z.shape)[0]
                z_linspace = np.linspace(zmax - len(p) * min_thickness, zmax,
                                         len(p))
                # z_linspace = z_linspace[1:]
                # for v in range(len(unmarked)):
                #     z[ind[v]] = z_linspace[v]
                # vertices[unmarked, -1] = z
                vertices[p, -1] = z_linspace

        ncheck[p] = True

    toc = time.time()
    LOG.info(' Vertices interp. elapsed in %f seconds', toc-tic)

    # # plot fitted points
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.scatter(vertices[mrk > 0, 0], vertices[mrk > 0, 1],
    #            vertices[mrk > 0, 2], marker='o')
    # # ax.scatter(vertices[mrk < 0, 0], vertices[mrk < 0, 1],
    # #            vertices[mrk < 0, 2], marker='o')
    # ax.scatter(vertices[mrk == 0, 0], vertices[mrk == 0, 1],
    #            vertices[mrk == 0, 2], marker='.')
    # plt.show()

    # create cell nodes --------------------------------------------------
    tic = time.time()
    nx = np.int64(n_x)
    ny = np.int64(n_y)
    nz = np.int64(n_z)

    i, j, k = np.mgrid[0:nx, 0:ny, 0:nz]
    ijk = np.ravel_multi_index(
        [list(i.ravel()), list(j.ravel()), list(
            k.ravel())], (nx + 1, ny + 1, nz + 1),
        order='F')
    conn = np.array([[i, i+1, i+1+(nx+1), i+(nx+1),
                      i+(nx+1)*(ny+1), i+1+(nx+1) *
                      (ny+1), i+1+(nx+1)+(nx+1)*(ny+1),
                      i+(nx+1)+(nx+1)*(ny+1)]
                     for i in ijk], dtype='uint64')
    toc = time.time()
    LOG.info(' Connections build elapsed in %f seconds', toc-tic)

    # compute cells volume
    LOG.info('Evaluating grid')
    volumes = np.zeros(nx*ny*nz)
    for c in range(nx*ny*nz):
        volumes[c] = utils.volume_hexahedron(vertices[conn[c]])

    if any(volumes < 1e-9):
        LOG.warning('** Negative volume found!')
    LOG.info('Done')

    # create unv
    if auto_save:
        utils.write_unv(fname + "_smoothed.unv", vertices, conn + 1)
        np.savetxt(fname + '_smoothed.coords', vertices)
        np.savetxt(fname + '_smoothed.lnods', conn + 1, fmt='%10d')

    return (vertices, conn)


# ------------------------------------------------------------------------------
def SmeshFromNodesAndCellNodes(nodes, cells, make_groups=True):
    """
    Returns an instance of SMESH (Mesh class) from vertices and connections
    """

    # salome imports
    from salome.smesh import smeshBuilder

    # initialize smesh
    LOG.debug('Initializing SMESH')
    smesh = smeshBuilder.New()

    # instaciate mesh
    mesh = smesh.Mesh(0,"Grid")

    LOG.debug("Adding nodes")
    for i in range(nodes.shape[0]):
        mesh.AddNode(nodes[i, 0], nodes[i, 1], nodes[i, 2])

    LOG.debug("Adding elements (hexahedron)")
    if np.min(cells.ravel()) < 0:
        conn = [int(ind + 1) for kxx in cells for ind in kxx]
    else:
        conn = [int(ind) for kxx in cells for ind in kxx]
    for i in range(0, len(conn), 8):
        mesh.AddFace([conn[i+0], conn[i+1], conn[i+2], conn[i+3]])
        mesh.AddFace([conn[i+1], conn[i+0], conn[i+4], conn[i+5]])
        mesh.AddFace([conn[i+2], conn[i+1], conn[i+5], conn[i+6]])
        mesh.AddFace([conn[i+3], conn[i+2], conn[i+6], conn[i+7]])
        mesh.AddFace([conn[i+0], conn[i+3], conn[i+7], conn[i+4]])
        mesh.AddFace([conn[i+7], conn[i+6], conn[i+5], conn[i+4]])

        mesh.AddVolume([conn[i+0], conn[i+1], conn[i+2], conn[i+3],
                        conn[i+4], conn[i+5], conn[i+6], conn[i+7]])

    if make_groups:
        M = CreateBorderGroups(mesh)
    else:
        import SMESH
        dim = SMESH.BND_2DFROM3D

        # boundary group in this mesh
        LOG.info("Setting boundary faces in Grid")
        groupName = "Boundary_Faces"
        nbfaces, M, new_group = mesh.MakeBoundaryElements(dim, groupName)

    return M


# ------------------------------------------------------------------------------
def CreateExtendedMesh(mesh, direction_key, length, division):
    """
    Create an extended grid from a given direction with dimensions and
    divisions provided.
    """

    # Get direction code
    direction = DIRECTION[direction_key.lower()]

    # get vertices sideburden
    # get side to extend
    LOG.debug("Checking side direction to extend")
    side = SIDE[direction]
    gFace = mesh.GetGroupByName(side + '_Faces')
    if len(gFace) > 0:
        gFace = gFace[0]
    else:
        LOG.critical('Group %s not found', side + '_Faces')

    # list of faces on side
    facesId = gFace.GetListOfID()
    faceNodesId = np.array([mesh.GetElemNodes(f) for f in facesId])
    nodesId = np.unique(faceNodesId.ravel())
    # vertices of side
    vertices = np.array([mesh.GetNodeXYZ(int(i)) for i in nodesId])
    xmean = np.mean(vertices, axis=0)

    # For Eastside and Westside
    if direction < 2:

        # collecting nodes for generate extended mesh
        x_offset = np.linspace(xmean[0] - (1 - direction) * length,
                               xmean[0] + direction * length, division + 1)
        y_offset = np.unique(vertices[:, 1])

        diff = np.abs(vertices[0, :] - vertices)
        idz = utils.find_indexes((diff[:, 0] < 1e-9) & (diff[:, 1] < 1e-9))
        z_offset = np.unique(vertices[idz, -1])

        axis = 1
        pillars = y_offset
    # For Northside and Southside
    elif direction < 4:

        # collecting nodes for generate extended mesh
        x_offset = np.unique(vertices[:, 0])
        y_offset = np.linspace(xmean[1] - (direction - 2) * length,
                               xmean[1] + (3 - direction) * length,
                               division + 1)

        diff = np.abs(vertices[0, :] - vertices)
        idz = utils.find_indexes((diff[:, 0] < 1e-9) & (diff[:, 1] < 1e-9))
        z_offset = np.unique(vertices[idz, -1])

        axis = 0
        pillars = x_offset

    # For Topside and Bottomside
    else:

        # collecting nodes for generate extended mesh
        x_offset = np.unique(vertices[:, 0])
        y_offset = np.unique(vertices[:, 1])

        diff = np.abs(vertices[0, :] - vertices)
        idz = utils.find_indexes((diff[:, 0] < 1e-9) & (diff[:, 1] < 1e-9))
        z_offset = np.linspace(xmean[2] - (direction - 4) * length,
                               xmean[2] + (5 - direction) * length,
                               division + 1)

        axis = [0, 1]
        pillars = [x_offset, y_offset]
        z_ref = (direction - 4) * z_offset[0] + (5 - direction) * z_offset[-1]

    # Generate side mesh
    LOG.debug("Creating grid extended")
    (nodes, cells) = utils.CartGrid(x_offset, y_offset, z_offset)

    # for irregular sides (z extend)
    LOG.debug("Aligning nodes")
    if direction > 3:
        # align/fit coordinates
        for p0 in pillars[0]:
            for p1 in pillars[1]:
                # pillar in grid
                i = utils.find_indexes((vertices[:, axis[0]] == p0) &
                                       (vertices[:, axis[1]] == p1))
                z = vertices[i][0]

                # adjust z coords
                j = np.array(utils.find_indexes((nodes[:, axis[0]] == p0)
                                                & (nodes[:, axis[1]] == p1)))
                dist = nodes[j, -1] - z[-1]
                ind = np.argsort(dist)
                nodes[j[ind], 2] = np.linspace(
                    (direction - 4) * z_ref + (5 - direction) * z[-1],
                    (direction - 4) * z[-1] + (5 - direction) * z_ref,
                    division + 1)

    else:
        # align/fit coordinates
        for p in pillars:
            # pillar in grid
            i = utils.find_indexes(vertices[:, axis] == p)
            z_pillar = np.sort(vertices[i, -1])

            # adjust z coords
            z = np.unique(nodes[nodes[:, axis] == p, -1])
            for k in range(z.size):
                j = utils.find_indexes((nodes[:, axis] == p)
                                       & (nodes[:, 2] == z[k]))
                nodes[j, 2] = z_pillar[k]

    # create SMESH
    return (nodes, cells)


# ------------------------------------------------------------------------------
def CreateMeshFromTopBase(vert, cells, fun_top, fun_base):
    """
    Create grid from a given top and base function interpolated.
    """
    top = vert[:, -1] == np.max(vert[:, -1])
    base = vert[:, -1] == np.min(vert[:, -1])

    # interpolate vertices top and base
    vert[top, -1] = fun_top(vert[top, 0], vert[top, 1])
    vert[base, -1] = fun_base(vert[base, 0], vert[base, 1])

    vmsk = np.zeros((vert.shape[0],), dtype=bool)

    # mark horizons (top and base)
    horz = np.zeros((vert.shape[0],))
    horz[top] = 1
    horz[base] = -1
    for i in range(vert.shape[0]):
        if vmsk[i]:
            continue
        vmsk[i] = True

        # diff of nodes (same pillar has dx=dy=0)
        dx = np.abs(vert[i, :] - vert[:, ])[:, 0:2]

        # check for pillar
        msk = np.array(utils.find_indexes((dx[:, 0] < 1e-9) & (dx[:, 1] < 1e-9)))
        hh = horz[msk]
        top = np.argmax(hh)
        base = np.argmin(hh)

        if np.abs(vert[msk[0], -1] - vert[msk[-1], -1]) > 1e-9:
            # sort
            z_linspace = np.linspace(vert[msk[0], -1], vert[msk[-1], -1], len(msk))
            vert[msk, -1] = z_linspace
        else:
            # sort
            z_linspace = np.linspace(
                vert[msk[0], -1] - 10, vert[msk[-1], -1] + 10, len(msk))
            vert[msk, -1] = z_linspace
        
        # fix wrong data provided
        if vert[msk[top],-1] < vert[msk[base],-1]:
            vert[msk] = np.flipud(vert[msk])

        vmsk[msk] = True

    # create SMESH
    return SmeshFromNodesAndCellNodes(vert, cells + 1, False)


# ------------------------------------------------------------------------------
def CreatePolylinesFromShapefile(shape_file: str, closed: bool=True) -> None:
    """
    Create polylines from shapefile. If shape has more than one shape this create
    several polylines. 
    If shapes aren't closed, set closed=False
    """
    import shapefile
    import GEOM
    from salome.geom import geomBuilder
    import xalome
    geompy = geomBuilder.New()

    sf = shapefile.Reader(shape_file)

    pline = 0
    for s in sf.shapes():
        p = np.asarray(s.points)
        pl = geompy.Polyline2D()
        pl.addSection('zone'+str(pline), GEOM.Polyline, True, p.reshape(-1,1).ravel().tolist())
        pp = pl.result()
        xalome.displayShape(xalome.addToStudy(pp,'polyline'+str(pline)))
        pline += 1


# ------------------------------------------------------------------------------
def ScaleAlongAxes(mesh, factor_x=1.0, factor_y=1.0, factor_z=1.0):
    """
    Scale the given mesh object by different factors along coordinate axes, creating
    its copy before the scaling.
    """
    nnodes = mesh.NbNodes()
    nquads = mesh.NbQuadrangles()
    nhexas = mesh.NbHexas()

    if nhexas == 0:
        cells = []
        for e in range(mesh.NbElements()):
            cnodes = mesh.GetElemNodes(e+1)
            if len(cnodes) == 4:
                cells.append(mesh.GetElemNodes(e+1))
        cells = np.asarray(cells)
    else:
        cells = []
        for e in range(mesh.NbElements()):
            cnodes = mesh.GetElemNodes(e+1)
            if len(cnodes) == 8:
                cells.append(mesh.GetElemNodes(e+1))
        cells = np.asarray(cells)
    
    nodes = np.asarray([mesh.GetNodeXYZ(i+1) for i in range(mesh.NbNodes())])
    nodes[:,0] *= factor_x
    nodes[:,1] *= factor_y
    nodes[:,2] *= factor_z

    return SmeshFromNodesAndCellNodes(nodes, cells, False)