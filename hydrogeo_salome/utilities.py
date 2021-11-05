# Copyright (C) 2017-2020 JCT
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
# Author : Jonathan Teixeira (jonathan.teixeira@ufpe.br)
#
#

"""
This file contains utility functions
NOTE: This file must NOT have dependencies on other files in the macro
"""

# python imports
import os
import numpy as np

# ------------------------------------------------------------------------------


def CartGrid(x, y, z=None):
    """Build a cartesian grid data (nodes and connections). Returns a tuple with:
    (ndarray nodes coordinate, ndarray cells connectivities)"""

    if z is None:
        nodes = np.array([[i, j, 0.] for j in y for i in x])

        nx = x.size
        ny = y.size
        i, j = np.mgrid[0:nx, 0:ny]
        ij = np.ravel_multi_index(
            [list(i.ravel()), list(j.ravel())], (nx+1, ny+1), order='F')

        cells = np.array([[i, i+1, i+1+nx+1, i+nx+1]
                          for i in ij], dtype='uint64')

    else:
        nodes = np.array([[i, j, k] for k in z for j in y for i in x])

        nx = x.size - 1
        ny = y.size - 1
        nz = z.size - 1

        i, j, k = np.mgrid[0:nx, 0:ny, 0:nz]
        ijk = np.ravel_multi_index(
            [list(i.ravel()), list(j.ravel()), list(
                k.ravel())], (nx + 1, ny + 1, nz + 1),
            order='F')
        cells = np.array([[i, i+1, i+1+(nx+1), i+(nx+1),
                           i+(nx+1)*(ny+1), i+1+(nx+1) *
                           (ny+1), i+1+(nx+1)+(nx+1)*(ny+1),
                           i+(nx+1)+(nx+1)*(ny+1)]
                          for i in ijk], dtype='uint64')

    return (nodes, cells)


# ------------------------------------------------------------------------------
def find_indexes(b):
    """This function is similar to the 'find' a MATLAB function"""
    return [i for (i, vals) in enumerate(b) if vals]


# ------------------------------------------------------------------------------
def write_unv(fname, nodes, cells, mat=None):
    """
    Write the UNV (Universal) file dataset format
    reference in: https://docs.plm.automation.siemens.com/tdoc/nx/12/nx_help#uid:xid1128419:index_advanced:xid1404601:xid1404604
    """

    # consts
    sep = "    -1"
    si, coordsys, vertices, elements = 164, 2420, 2411, 2412

    # settings
    if mat is None:
        mat = np.zeros((cells.shape[0],), dtype=np.int64) + 1

    # write unv file
    # print("-- writing file: {}".format(fname))
    with open(fname, "w") as unv:
        # unit system (164)
        unv.write('{}\n'.format(sep))
        unv.write('{:6g}\n'.format(si))  # unv code
        unv.write('{:10d}{:20s}{:10d}\n'.format(1, "SI: Meters (newton)", 2))
        unv.write('{:25.17E}{:25.17E}{:25.17E}\n{:25.17E}\n'.format(
            1, 1, 1, 273.15))
        unv.write('{}\n'.format(sep))

        # coordinate system (2420)
        unv.write('{}\n'.format(sep))
        unv.write('{:6g}\n'.format(coordsys))  # unv code
        unv.write('{:10d}\n'.format(1))  # coordsys label (uid)
        unv.write('{:40s}\n'.format("SMESH_Mesh from Salome Geomechanics"))
        # coordsys label, coordsys type (0: cartesian), coordsys color
        unv.write('{:10d}{:10d}{:10d}\n'.format(1, 0, 0))
        unv.write('{:40s}\n'.format("Global cartesian coord. system"))
        unv.write('{:25.16E}{:25.16E}{:25.16E}\n'.format(1, 0, 0))
        unv.write('{:25.16E}{:25.16E}{:25.16E}\n'.format(0, 1, 0))
        unv.write('{:25.16E}{:25.16E}{:25.16E}\n'.format(0, 0, 1))
        unv.write('{:25.16E}{:25.16E}{:25.16E}\n'.format(0, 0, 0))
        unv.write('{}\n'.format(sep))

        # write nodes coordinates
        unv.write('{}\n'.format(sep))
        unv.write('{:6g}\n'.format(vertices))  # unv code
        for n in range(nodes.shape[0]):
            # node-id, coordinate system label, displ. coord. system, color(11)
            unv.write('{:10d}{:10d}{:10d}{:10d}\n'.format(n + 1, 1, 1, 11))
            unv.write('{:25.16E}{:25.16E}{:25.16E}'.format(
                nodes[n, 0], nodes[n, 1], nodes[n, 2]))
            unv.write('\n')
        unv.write('{}\n'.format(sep))

        # write cells connectivities
        unv.write('{}\n'.format(sep))
        unv.write('{:6g}\n'.format(elements))  # unv code
        for c in range(cells.shape[0]):
            # node-id, coordinate system label, displ. coord. system, color(11)
            unv.write('{:10d}{:10d}{:10d}{:10d}{:10d}{:10d}\n'.format(
                c + 1, 115, mat[c], mat[c], mat[c], 8))
            unv.write('{:10d}{:10d}{:10d}{:10d}{:10d}{:10d}{:10d}{:10d}'.format(
                cells[c, 0], cells[c, 1], cells[c, 2], cells[c, 3],
                cells[c, 4], cells[c, 5], cells[c, 6], cells[c, 7]))
            unv.write('\n')
        unv.write('{}\n'.format(sep))

        # write cells regions
        unv.write('{}\n'.format(sep))
        unv.write('{:6g}\n'.format(2467))  # unv code
        regions = np.unique(mat)
        for region in regions:
            ind = find_indexes(mat == region)
            unv.write('{:10d}{:10d}{:10d}{:10d}{:10d}{:10d}{:10d}{:10d}\n'.format(
                region, 0, 0, 0, 0, 0, 0, len(ind)))       
            unv.write('Region_{}\n'.format(region))
            i = 0
            for c in range(len(ind)):
                unv.write('{:10d}{:10d}{:10d}{:10d}'.format( 8, ind[c] + 1, 0, 0))
                i += 1
                if i == 2:
                    i = 0
                    unv.write('\n')
            if i == 1:
                unv.write('\n')
        unv.write('{}\n'.format(sep))


# ------------------------------------------------------------------------------
def write_mesh(fname, smesh, boundaries=None, mat=None):
    """
    Write the mesh file format (mfem). Only works for hexahedron (cube)

    TODO: impl. other finite elements
    """
    import SMESH
    # consts
    header = """# automatically generated by hydrogeo_salome plugin
MFEM mesh v1.0

#
# MFEM Geometry Types (see mesh/geom.hpp):
#
# POINT       = 0
# SEGMENT     = 1
# TRIANGLE    = 2
# SQUARE      = 3
# TETRAHEDRON = 4
# CUBE        = 5
#
"""
    
    # settings
    ncells = smesh.NbHexas()
    nnodes = smesh.NbNodes()
    dim = 3
    if mat is None:
        mat = np.ones((ncells,), dtype=np.int64)
    else:
        assert mat.shape[0] == ncells, "mismatch length between mat and cells"

    cells = smesh.GetElementsByType(SMESH.VOLUME)
    # write mesh file
    with open(fname + '.mesh', "w") as mesh:
        # header
        mesh.write('{}'.format(header))

        # dimension
        mesh.write('dimension\n{}\n\n'.format(dim))

        # elements connectivities
        mesh.write('elements\n{}\n'.format(ncells))
        for i in range(ncells):
            # region-id, element-type, connectivities
            mesh.write('{} {}'.format(mat[i], 5))
            for n in smesh.GetElemNodes(cells[i]):
                mesh.write(' {}'.format(n))
            mesh.write('\n')
        mesh.write('\n')

        # boundaries
        if boundaries is not None:
            count = 0
            for b in boundaries:
                count += len(b.GetIDs())
            mesh.write('boundary\n{}\n'.format(count))
            count = 1
            for bdr in boundaries:
                for b in bdr.GetIDs():
                    # region-id, element-type, connectivities
                    mesh.write('{} {}'.format(count, 3))
                    for n in smesh.GetElemNodes(b):
                        mesh.write(' {}'.format(n))
                    mesh.write('\n')
                count += 1
            mesh.write('\n')

        # vertices
        mesh.write('vertices\n{}\n{}\n'.format(nnodes, dim))
        for n in smesh.GetNodesId():
            # x y z
            for x in smesh.GetNodeXYZ(n):
                mesh.write(' {}'.format(x))
            mesh.write('\n')
        mesh.write('\n')


# ------------------------------------------------------------------------------
def write_coords_lnods(fname, smesh, boundaries=None, mat=None):
    """
    Write the datablock mesh file format (coords and lnodes). Only works for hexahedron (cube)

    TODO: impl. other finite elements
    """
    import SMESH
    # consts
    header1 = "# node-ID x y z bdr-ID\n"
    header2 = "# elem-ID mat elem-type conn... \n"
    
    # settings
    ncells = smesh.NbHexas()
    nnodes = smesh.NbNodes()
    dim = 3
    if mat is None:
        mat = np.ones((ncells,), dtype=np.int64)
    else:
        assert mat.shape[0] == ncells, "mismatch length between mat and cells"

    cells = smesh.GetElementsByType(SMESH.VOLUME)
    # write mesh file
    with open(fname + '.coords', "w") as coords:
        coords.write(header1)
        # boundaries
        bdr = np.zeros((nnodes,), dtype=np.int64)
        count = 1
        if boundaries is not None:
            for b in boundaries:
                for id in b.GetIDs():
                    bdr[np.asarray(smesh.GetElemNodes(id)) - 1] = count
                count += 1
        count = 0
        for n in smesh.GetNodesId():
            coords.write('{}'.format(count + 1))
            # x y z
            for x in smesh.GetNodeXYZ(n):
                coords.write(' {}'.format(x))
            coords.write(' {}\n'.format(bdr[count]))
            count += 1

    with open(fname + '.lnods', "w") as lnods:
        lnods.write(header2)
        # elements connectivities
        for i in range(ncells):
            # region-id, element-type, connectivities
            lnods.write('{} {} hex'.format(i + 1, mat[i]))
            for n in smesh.GetElemNodes(cells[i]):
                lnods.write(' {}'.format(n))
            lnods.write('\n')
        lnods.write('\n')


# ------------------------------------------------------------------------------
def write_vtk(fname, smesh, boundaries=None, mat=None):
    """
    Write the vtk legacy format (vtk). Only works for hexahedron (cube)

    TODO: impl. other finite elements
    """
    import SMESH
    # consts
    header = """# vtk DataFile Version 2.0
meshfile created by hydrogeo_salome plugins
ASCII
DATASET UNSTRUCTURED_GRID
FIELD FieldData 2
TIME 1 1 float
0
CYCLE 1 1 int
0
"""
    
    # settings
    ncells = smesh.NbHexas()
    nnodes = smesh.NbNodes()
    dim = 3
    if mat is None:
        mat = np.ones((ncells,), dtype=np.int64)
    else:
        assert mat.shape[0] == ncells, "mismatch length between mat and cells"

    cells = smesh.GetElementsByType(SMESH.VOLUME)
    # write mesh file
    with open(fname + '.vtk', "w") as mesh:
        # header
        mesh.write('{}'.format(header))

        # vertices
        mesh.write('POINTS {} float\n'.format(nnodes))
        for n in smesh.GetNodesId():
            # x y z
            for x in smesh.GetNodeXYZ(n):
                mesh.write(' {}'.format(x))
            mesh.write('\n')
        mesh.write('\n')

        # elements connectivities
        mesh.write('CELLS  {} {}\n'.format(ncells, ncells + 8*ncells))
        for i in range(ncells):
            # region-id, element-type, connectivities
            mesh.write('8 ')
            for n in smesh.GetElemNodes(cells[i]):
                mesh.write(' {}'.format(n - 1))
            mesh.write('\n')
        mesh.write('\n')

        # elements type
        mesh.write('CELL_TYPES  {}\n'.format(ncells))
        for i in range(ncells):
            # region-id, element-type, connectivities
            mesh.write('12\n')
        mesh.write('\n')

        # boundaries and materials
        if boundaries is not None:
            bdr = np.zeros((nnodes,), dtype=np.int64)
            count = 1
            for b in boundaries:
                for id in b.GetIDs():
                    bdr[np.asarray(smesh.GetElemNodes(id)) - 1] = count
                count += 1

            mesh.write('POINT_DATA  {}\n'.format(nnodes))
            mesh.write('SCALARS bdr float\n')
            mesh.write('LOOKUP_TABLE default\n')
            for i in range(nnodes):
                mesh.write('{}\n'.format(bdr[i]))
            mesh.write('\n')

        mesh.write('CELL_DATA  {}\n'.format(ncells))
        mesh.write('SCALARS materials float\n')
        mesh.write('LOOKUP_TABLE default\n')
        for i in range(ncells):
            mesh.write('{}\n'.format(mat[i]))
        mesh.write('\n')


# ------------------------------------------------------------------------------
def volume_hexahedron(nodes):
    """This function compute hexahedron volume"""

    volelm = 0
    x1 = nodes[0, 0]
    y1 = nodes[0, 1]
    z1 = nodes[0, 2]

    x2 = nodes[1, 0]
    y2 = nodes[1, 1]
    z2 = nodes[1, 2]

    x3 = nodes[2, 0]
    y3 = nodes[2, 1]
    z3 = nodes[2, 2]

    x4 = nodes[3, 0]
    y4 = nodes[3, 1]
    z4 = nodes[3, 2]

    x5 = nodes[4, 0]
    y5 = nodes[4, 1]
    z5 = nodes[4, 2]

    x6 = nodes[5, 0]
    y6 = nodes[5, 1]
    z6 = nodes[5, 2]

    x7 = nodes[6, 0]
    y7 = nodes[6, 1]
    z7 = nodes[6, 2]

    x8 = nodes[7, 0]
    y8 = nodes[7, 1]
    z8 = nodes[7, 2]

    chi1 = -1.0
    eta1 = -1.0
    tet1 = -1.0

    chi2 = +1.0
    eta2 = -1.0
    tet2 = -1.0

    chi3 = +1.0
    eta3 = +1.0
    tet3 = -1.0

    chi4 = -1.0
    eta4 = +1.0
    tet4 = -1.0

    chi5 = -1.0
    eta5 = -1.0
    tet5 = +1.0

    chi6 = +1.0
    eta6 = -1.0
    tet6 = +1.0

    chi7 = +1.0
    eta7 = +1.0
    tet7 = +1.0

    chi8 = -1.0
    eta8 = +1.0
    tet8 = +1.0

    # 8 integration points
    chi01 = -.577350269189626
    eta01 = -.577350269189626
    tet01 = -.577350269189626

    chi02 = +.577350269189626
    eta02 = -.577350269189626
    tet02 = -.577350269189626

    chi03 = +.577350269189626
    eta03 = +.577350269189626
    tet03 = -.577350269189626

    chi04 = -.577350269189626
    eta04 = +.577350269189626
    tet04 = -.577350269189626

    chi05 = -.577350269189626
    eta05 = -.577350269189626
    tet05 = +.577350269189626

    chi06 = +.577350269189626
    eta06 = -.577350269189626
    tet06 = +.577350269189626

    chi07 = +.577350269189626
    eta07 = +.577350269189626
    tet07 = +.577350269189626

    chi08 = -.577350269189626
    eta08 = +.577350269189626
    tet08 = +.577350269189626

    nval = 8
    weight = 1.0

    for ival in range(0, nval):
        if ival == 0:
            chi = chi01
            eta = eta01
            tet = tet01
        elif ival == 1:
            chi = chi02
            eta = eta02
            tet = tet02
        elif ival == 2:
            chi = chi03
            eta = eta03
            tet = tet03
        elif ival == 3:
            chi = chi04
            eta = eta04
            tet = tet04
        elif ival == 4:
            chi = chi05
            eta = eta05
            tet = tet05
        elif ival == 5:
            chi = chi06
            eta = eta06
            tet = tet06
        elif ival == 6:
            chi = chi07
            eta = eta07
            tet = tet07
        elif ival == 7:
            chi = chi08
            eta = eta08
            tet = tet08

        dn1dchi = chi1*(1.0+eta*eta1)*(1.0+tet*tet1)/8.
        dn1deta = eta1*(1.0+chi*chi1)*(1.0+tet*tet1)/8.
        dn1dtet = tet1*(1.0+chi*chi1)*(1.0+eta*eta1)/8.

        dn2dchi = chi2*(1.0+eta*eta2)*(1.0+tet*tet2)/8.
        dn2deta = eta2*(1.0+chi*chi2)*(1.0+tet*tet2)/8.
        dn2dtet = tet2*(1.0+chi*chi2)*(1.0+eta*eta2)/8.

        dn3dchi = chi3*(1.0+eta*eta3)*(1.0+tet*tet3)/8.
        dn3deta = eta3*(1.0+chi*chi3)*(1.0+tet*tet3)/8.
        dn3dtet = tet3*(1.0+chi*chi3)*(1.0+eta*eta3)/8.

        dn4dchi = chi4*(1.0+eta*eta4)*(1.0+tet*tet4)/8.
        dn4deta = eta4*(1.0+chi*chi4)*(1.0+tet*tet4)/8.
        dn4dtet = tet4*(1.0+chi*chi4)*(1.0+eta*eta4)/8.

        dn5dchi = chi5*(1.0+eta*eta5)*(1.0+tet*tet5)/8.
        dn5deta = eta5*(1.0+chi*chi5)*(1.0+tet*tet5)/8.
        dn5dtet = tet5*(1.0+chi*chi5)*(1.0+eta*eta5)/8.

        dn6dchi = chi6*(1.0+eta*eta6)*(1.0+tet*tet6)/8.
        dn6deta = eta6*(1.0+chi*chi6)*(1.0+tet*tet6)/8.
        dn6dtet = tet6*(1.0+chi*chi6)*(1.0+eta*eta6)/8.

        dn7dchi = chi7*(1.0+eta*eta7)*(1.0+tet*tet7)/8.
        dn7deta = eta7*(1.0+chi*chi7)*(1.0+tet*tet7)/8.
        dn7dtet = tet7*(1.0+chi*chi7)*(1.0+eta*eta7)/8.

        dn8dchi = chi8*(1.0+eta*eta8)*(1.0+tet*tet8)/8.
        dn8deta = eta8*(1.0+chi*chi8)*(1.0+tet*tet8)/8.
        dn8dtet = tet8*(1.0+chi*chi8)*(1.0+eta*eta8)/8.

        a11 = x1*dn1dchi+x2*dn2dchi+x3*dn3dchi+x4*dn4dchi + \
            x5*dn5dchi+x6*dn6dchi+x7*dn7dchi+x8*dn8dchi
        a12 = y1*dn1dchi+y2*dn2dchi+y3*dn3dchi+y4*dn4dchi + \
            y5*dn5dchi+y6*dn6dchi+y7*dn7dchi+y8*dn8dchi
        a13 = z1*dn1dchi+z2*dn2dchi+z3*dn3dchi+z4*dn4dchi + \
            z5*dn5dchi+z6*dn6dchi+z7*dn7dchi+z8*dn8dchi
        a21 = x1*dn1deta+x2*dn2deta+x3*dn3deta+x4*dn4deta + \
            x5*dn5deta+x6*dn6deta+x7*dn7deta+x8*dn8deta
        a22 = y1*dn1deta+y2*dn2deta+y3*dn3deta+y4*dn4deta + \
            y5*dn5deta+y6*dn6deta+y7*dn7deta+y8*dn8deta
        a23 = z1*dn1deta+z2*dn2deta+z3*dn3deta+z4*dn4deta + \
            z5*dn5deta+z6*dn6deta+z7*dn7deta+z8*dn8deta
        a31 = x1*dn1dtet+x2*dn2dtet+x3*dn3dtet+x4*dn4dtet + \
            x5*dn5dtet+x6*dn6dtet+x7*dn7dtet+x8*dn8dtet
        a32 = y1*dn1dtet+y2*dn2dtet+y3*dn3dtet+y4*dn4dtet + \
            y5*dn5dtet+y6*dn6dtet+y7*dn7dtet+y8*dn8dtet
        a33 = z1*dn1dtet+z2*dn2dtet+z3*dn3dtet+z4*dn4dtet + \
            z5*dn5dtet+z6*dn6dtet+z7*dn7dtet+z8*dn8dtet

        det = a11*a22*a33+a12*a23*a31+a21*a32*a13-a13*a22*a31 - \
            a12*a21*a33-a23*a32*a11

        volelm = volelm+det*weight
    return volelm


# ------------------------------------------------------------------------------
def GetModulePath():
    """This function returns the absolute path to the module"""
    return os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


# ------------------------------------------------------------------------------

def GetAbsPathInModule(*paths):
    """This function prepends the path to the module to a path given in the input"""
    return os.path.join(GetModulePath(), *paths)
