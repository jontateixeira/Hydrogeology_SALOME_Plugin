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
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
#
# Author : Jonathan Teixeira (jonathan.teixeira@ufpe.br)
#
"""
This file contains all dialog used as interface to Salome
"""

# python imports
try:
    from PyQt4 import QtGui
    from PyQt4 import QtCore
except ImportError:
    from PyQt5 import QtWidgets as QtGui
    from PyQt5 import QtCore
import numpy as np
from matplotlib import path
import logging

# salome imports
import salome

#import plugin component
from hydrogeo_salome import *
from . import dialog_ui_grid as dialog_grid
from . import dialog_ui_bdr as dialog_bdr
from . import dialog_ui_export as dialog_export
from hydrogeo_salome import utilities as utils
from hydrogeo_salome import macros

global plugin_initialized
plugin_initialized = False
preview_mesh_obj = None


def deletePreviewMesh(preview_mesh):
    """This delete the smesh currently being displayed as a preview"""
    salome.sg.Erase(preview_mesh['ID'])
    meshSO = salome.ObjectToSObject(preview_mesh['Obj'].GetMesh())
    salome.myStudy.NewBuilder().RemoveObjectWithChildren( meshSO )
    preview_mesh['Obj'].GetMesh().Clear() # just in case
    salome.sg.updateObjBrowser()
    preview_mesh = None
    return preview_mesh


def deletePreviewGroupMesh(preview_mesh_obj):
    """This delete the Group added in a smesh currently being displayed as a preview"""
    global salome
    
    mesh = preview_mesh_obj['Obj'].GetMesh()
    prefix = preview_mesh_obj['GroupName']
    groups = mesh.GetGroups()
    for g in groups:
        if g.GetName().startswith(prefix):
            mesh.RemoveGroup(g)
    # Update Object Browser
    if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser()
    preview_mesh_obj = None
    return preview_mesh_obj


# ========================================================================
# CARTESIAN GRID MODEL: build a grid model (cartesian grid) and recycled 
# for every call.
def init_grid_model(context):
    """Generate a simple grid model (cartesian) this functionality is used
    as a model to create/extend new task and function from scratch. see also
    hydrogeo_salome.dialog_ui.py to create the ui interface.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    global plugin_initialized

    def acceptCallback():
        """Action to be done when click on Ok"""
        global preview_mesh_obj

        sgrid_dialog.accept()

        # We first have to destroy the currently displayed preview smesh.
        if isinstance(preview_mesh_obj, dict):
            preview_mesh_obj = deletePreviewMesh(preview_mesh_obj)
            
        nx, ny, nz = sgrid_dialog.getNumberOfBlock()
        lx, ly, lz = sgrid_dialog.getDataLength()
        x = np.linspace(0, lx, nx +1)
        y = np.linspace(0, ly, ny + 1)
        z = np.linspace(0, lz, nz + 1)
        nodes, cells = utils.CartGrid(x,y,z)
        mesh = macros.SmeshFromNodesAndCellNodes(nodes, cells + 1)

        # Update Object Browser
        if salome.sg.hasDesktop():
            id = salome.myStudy.FindObjectByPath("/Mesh/Grid").GetID()
            # display obj
            salome.sg.Display(id)
            salome.sg.FitAll()
            salome.sg.updateObjBrowser()


    def rejectCallback():
        """Action to be done when click on Cancel"""
        global preview_mesh_obj
        sgrid_dialog.reject()

        # We first have to destroy the currently displayed preview smesh.
        if isinstance(preview_mesh_obj, dict):
            preview_mesh_obj = deletePreviewMesh(preview_mesh_obj)


    def applyCallback():
        """Action to be done when click on Apply"""
        global preview_mesh_obj
        # We first have to destroy the currently displayed preview smesh.
        if isinstance(preview_mesh_obj, dict):
            preview_mesh_obj = deletePreviewMesh(preview_mesh_obj)
        
        nx, ny, nz = sgrid_dialog.getNumberOfBlock()
        lx, ly, lz = sgrid_dialog.getDataLength()
        x = np.linspace(0, lx, nx +1)
        y = np.linspace(0, ly, ny + 1)
        z = np.linspace(0, lz, nz + 1)
        nodes, cells = utils.CartGrid(x,y,z)
        mesh = macros.SmeshFromNodesAndCellNodes(nodes, cells + 1)

        # Update Object Browser
        if salome.sg.hasDesktop():
            salome.sg.updateObjBrowser()
            # get mesh obj ID
            id = salome.myStudy.FindObjectByPath("/Mesh/Grid").GetID()
            obj = salome.myStudy.FindObjectByPath("/Mesh/Grid").GetObject()
            preview_mesh_obj = {'Obj': obj, 'ID': id}
            # display obj
            salome.sg.Display(id)
            salome.sg.FitAll()
            salome.sg.UpdateView() # update view
    
    # ===========================================================================
    # get active module and check if SMESH
    # ===========================================================================
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    # ===========================================================================
    # initialize dialog
    # ===========================================================================
    sgrid_dialog = dialog_grid.GridModelDialog()  
    
    # set default input parameters and others settings
    sgrid_dialog.setData(10,10,5)
    # Connection of callback functions to the dialog butoon click signals
    sgrid_dialog.handleAcceptWith(acceptCallback)
    sgrid_dialog.handleRejectWith(rejectCallback)
    sgrid_dialog.handleApplyWith(applyCallback)

    if not plugin_initialized:
        import hydrogeo_salome
        plugin_initialized = True
    sgrid_dialog.open()

# ========================================================================
# REALISTC GRID MODEL: Grid model with constraints
def constraint_grid_model(context):
    """Generate a constrainted grid model (cartesian).

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    global plugin_initialized

    def rejectCallbackWithConstraint():
        """Action to be done when click on Cancel"""
        global preview_mesh_obj
        gdialog_w_constraint.reject()

        # We first have to destroy the currently displayed preview smesh.
        if isinstance(preview_mesh_obj, dict):
            preview_mesh_obj = deletePreviewMesh(preview_mesh_obj)

    def acceptCallbackWithConstraint():
        """Action to be done when click on Ok"""
        global preview_mesh_obj

        LOG = logging.getLogger(__name__)

        gdialog_w_constraint.accept()

        # We first have to destroy the currently displayed preview smesh.
        if isinstance(preview_mesh_obj, dict):
            preview_mesh_obj = deletePreviewMesh(preview_mesh_obj)

        
        nx, ny, nz = gdialog_w_constraint.getNumberOfBlock()
        limits = gdialog_w_constraint.getConstraintArea()
        if limits is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Something wrong with the model area limits, Check it!')
            LOG.critical('Something wrong with the model area limits, Check it!')
            return
        x = np.linspace(np.min(limits[:,0]), np.max(limits[:,0]), nx +1)
        y = np.linspace(np.min(limits[:,1]), np.max(limits[:,1]), ny + 1)
        z = np.linspace(0, 1, nz + 1)
        LOG.info("generating cartesian grid")
        (nodes, cells) = utils.CartGrid(x,y,z)

        # compute cells centers
        cell_center = np.zeros((cells.shape[0], 3))
        for c in range(cells.shape[0]):
            cell_center[c, :] = np.mean(nodes[cells[c, :], :], axis=0)

        # remove cells out of limtis
        LOG.info("remove cells out of limtis")
        p = path.Path(limits)
        msk = p.contains_points(cell_center[:, [0, 1]])
        # select cells and vertices inside constrant area
        cnodes = cells[msk]
        vnodes = np.unique(cnodes.reshape(cnodes.size))
        # rearrange the cells and nodes
        idx = np.zeros((int(vnodes.max()+1),))
        idx[vnodes] = np.arange(0, vnodes.size)
        vert = nodes[vnodes]
        hexa = np.int64(np.reshape(idx[cnodes].ravel(), (cnodes.shape[0], 8)))

        # create a smesh
        LOG.info("Creating SMESH")
        top = gdialog_w_constraint.getTopHorizon()
        base = gdialog_w_constraint.getBottomHorizon()
        if top is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Something wrong with the model top horizon, Check it!')
            LOG.critical('Something wrong with the model top horizon, Check it!')
            return
        if base is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Something wrong with the model top horizon, Check it!')
            LOG.critical('Something wrong with the model top horizon, Check it!')
            return
        mesh = macros.CreateMeshFromTopBase(vert, hexa, top, base)

        # Update Object Browser
        if salome.sg.hasDesktop():
            salome.sg.updateObjBrowser()
            # get mesh obj ID
            id = salome.myStudy.FindObjectByPath("/Mesh/Grid").GetID()
            # display obj
            salome.sg.Display(id)
            salome.sg.FitAll()
            salome.sg.UpdateView() # update view


    def applyCallbackWithConstraint():
        """Action to be done when click on Apply"""
        global preview_mesh_obj
        
        LOG = logging.getLogger(__name__)

        # We first have to destroy the currently displayed preview smesh.
        if isinstance(preview_mesh_obj, dict):
            preview_mesh_obj = deletePreviewMesh(preview_mesh_obj)

        nx, ny, nz = gdialog_w_constraint.getNumberOfBlock()
        limits = gdialog_w_constraint.getConstraintArea()
        if limits is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Something wrong with the model area limits, Check it!')
            LOG.critical('Something wrong with the model area limits, Check it!')
            return
        x = np.linspace(np.min(limits[:,0]), np.max(limits[:,0]), nx +1)
        y = np.linspace(np.min(limits[:,1]), np.max(limits[:,1]), ny + 1)
        z = np.linspace(0, 1, nz + 1)
        LOG.info("generating cartesian grid")
        (nodes, cells) = utils.CartGrid(x,y,z)

        # compute cells centers
        cell_center = np.zeros((cells.shape[0], 3))
        for c in range(cells.shape[0]):
            cell_center[c, :] = np.mean(nodes[cells[c, :], :], axis=0)

        # remove cells out of limtis
        p = path.Path(limits)
        msk = p.contains_points(cell_center[:, [0, 1]])
        # select cells and vertices inside constrant area
        cnodes = cells[msk]
        vnodes = np.unique(cnodes.reshape(cnodes.size))
        # rearrange the cells and nodes
        idx = np.zeros((int(vnodes.max()+1),))
        idx[vnodes] = np.arange(0, vnodes.size)
        vert = nodes[vnodes]
        hexa = np.int64(np.reshape(idx[cnodes].ravel(), (cnodes.shape[0], 8)))

        # create a smesh
        LOG.info("Creating SMESH")
        top = gdialog_w_constraint.getTopHorizon()
        base = gdialog_w_constraint.getBottomHorizon()
        if top is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Something wrong with the model top horizon, Check it!')
            LOG.critical('Something wrong with the model top horizon, Check it!')
            return
        if base is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Something wrong with the model top horizon, Check it!')
            LOG.critical('Something wrong with the model top horizon, Check it!')
            return
        mesh = macros.CreateMeshFromTopBase(vert, hexa, top, base)


        # Update Object Browser
        if salome.sg.hasDesktop():
            salome.sg.updateObjBrowser()
            # get mesh obj ID
            id = salome.myStudy.FindObjectByPath("/Mesh/Grid").GetID()
            obj = salome.myStudy.FindObjectByPath("/Mesh/Grid").GetObject()
            preview_mesh_obj = {'Obj': obj, 'ID': id}
            # display obj
            salome.sg.Display(id)
            salome.sg.FitAll()
            salome.sg.UpdateView() # update view


    # ===========================================================================
    # get active module and check if SMESH
    # ===========================================================================
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    if not plugin_initialized:
        import hydrogeo_salome
        plugin_initialized = True

    # ===========================================================================
    # initialize dialog
    # ===========================================================================
    gdialog_w_constraint = dialog_grid.GridModelWithConstraintDialog()
    
    # set default parameters values
    gdialog_w_constraint.setData(10,10,5) 
    # Connection of callback functions to the dialog butoon click signals
    gdialog_w_constraint.handleAcceptWith(acceptCallbackWithConstraint)
    gdialog_w_constraint.handleRejectWith(rejectCallbackWithConstraint)
    gdialog_w_constraint.handleApplyWith(applyCallbackWithConstraint)

    # start dialog
    gdialog_w_constraint.open()



# ========================================================================
# SET BOUNDARY CONDITION
def bdr_constraint(context):
    """Add boundary condition constraints on grid model.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    LOG = logging.getLogger(__name__)

    def rejectCallBack():
        """Action to be done when click on Cancel"""
        global preview_mesh_obj
        bdr_dialog.reject()

        # We first have to destroy the currently displayed preview smesh.
        if isinstance(preview_mesh_obj, dict):
           preview_mesh_obj = deletePreviewGroupMesh(preview_mesh_obj)
        # Update Object Browser
        if salome.sg.hasDesktop():
            salome.sg.updateObjBrowser()

    def acceptCallBack():
        """Action to be done when click on Ok"""
        global preview_mesh_obj

        # active accept
        bdr_dialog.accept()

        # We first have to destroy the currently displayed preview smesh.
        if isinstance(preview_mesh_obj, dict):
            preview_mesh_obj = deletePreviewGroupMesh(preview_mesh_obj)
        
        # collect parameters
        zones = bdr_dialog.getBdrRegion()
        mesh_name = bdr_dialog.getMesh()
        dx = bdr_dialog.getCriteria()
        groupName = bdr_dialog.getGroupName()
        at_surface = bdr_dialog.getAssignAtSurface()

        # sanity check
        if zones is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Something wrong with Regions file, Check it!')
            LOG.critical('Something wrong with Regions file, Check it!')
            return
        if dx is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Something wrong with dx or dy criteria, Check it!')
            LOG.critical('Something wrong with dx or dy criteria, Check it!')
            return
        if mesh_name is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Select one mesh')
            LOG.critical('Select one mesh')
            return

        # create new group and update smesh
        m_obj = salome.myStudy.FindObjectByPath("/Mesh/" + mesh_name).GetObject()
        mesh = macros.CreateBorderGroupsFromRegions(m_obj.GetMesh(), zones, dx, 
                                                    groupName, at_surface)

        # Update Object Browser
        if salome.sg.hasDesktop():
            salome.sg.updateObjBrowser()

    def applyCallBack():
        """Action to be done when click on Apply"""
        global preview_mesh_obj

        # We first have to destroy the currently displayed preview smesh.
        if isinstance(preview_mesh_obj, dict):
            preview_mesh_obj = deletePreviewGroupMesh(preview_mesh_obj)
        
        # collect parameters
        zones = bdr_dialog.getBdrRegion()
        mesh_name = bdr_dialog.getMesh()
        dx = bdr_dialog.getCriteria()
        groupName = bdr_dialog.getGroupName()
        at_surface = bdr_dialog.getAssignAtSurface()

        # sanity check
        if mesh_name is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Select one mesh')
            LOG.critical('Select one mesh')
            return
        if zones is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Something wrong with Regions file, Check it!')
            LOG.critical('Something wrong with Regions file, Check it!')
            return
        if dx is None:
            QtGui.QMessageBox.critical(None, 'Grid Model' ,
                                    'Something wrong with dx or dy criteria, Check it!')
            LOG.critical('Something wrong with dx or dy criteria, Check it!')
            return

        # create new group and update smesh
        m_obj = salome.myStudy.FindObjectByPath("/Mesh/" + mesh_name).GetObject()
        mesh = macros.CreateBorderGroupsFromRegions(m_obj.GetMesh(), zones, dx, 
                                                    groupName, at_surface)

        # Update Object Browser
        if salome.sg.hasDesktop():
            salome.sg.updateObjBrowser()
            # get mesh obj ID
            id = salome.myStudy.FindObjectByPath("/Mesh/" + mesh_name).GetID()
            obj = salome.myStudy.FindObjectByPath("/Mesh/" + mesh_name).GetObject()
            preview_mesh_obj = {'Obj': obj, 'GroupName': groupName}
    
    # ===========================================================================
    # get active module and check if SMESH
    # ===========================================================================
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    # ===========================================================================
    # initialize dialog
    # ===========================================================================
    bdr_dialog = dialog_bdr.BoundaryConditionDialog()
    # set default parameters value
    bdr_dialog.setData(5000, 5000)
    # Connection of callback functions to the dialog butoon click signals
    bdr_dialog.handleAcceptWith(acceptCallBack)
    bdr_dialog.handleRejectWith(rejectCallBack)
    bdr_dialog.handleApplyWith(applyCallBack)

    # populate combobox
    bdr_dialog.meshObjCombo.addItem("","Empty")
    # collect all SMESH in the context
    meshes = salome.myStudy.FindComponent("SMESH")
    if meshes:
        iterator = salome.myStudy.NewChildIterator( meshes )
        while iterator.More():
            mobj = iterator.Value()
            if len(mobj.GetName()) > 1:
                bdr_dialog.meshObjCombo.addItem(mobj.GetName(), mobj.GetName())
            iterator.Next()

    bdr_dialog.open()



# ========================================================================
# SET BOUNDARY CONDITION
def export_mesh(context):
    """export smesh and groups to SOLVER readable format.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    LOG = logging.getLogger(__name__)

    def rejectCallBack():
        """Action to be done when click on Cancel"""
        # active accept
        export_dialog.reject()

    def acceptCallBack():
        """Action to be done when click on Ok"""        
        # collect parameters
        writer = export_dialog.getMeshWriter()
        file_name = export_dialog.getOutputFileName().split('.')[0]
        msh = export_dialog.getMesh()
        groups = export_dialog.getMeshGroups()

        # sanity check
        if msh is None:
            QtGui.QMessageBox.critical(None, 'Boundary condtition' ,
                                    'Select a valid smesh!')
            LOG.critical('Select a valid smesh!')
            return
        if file_name is None:
            QtGui.QMessageBox.critical(None, 'Boundary condtition' ,
                                    'Select a valid file_name')
            LOG.critical('Select a valid file_name')
            return

        # TODO: split volume and face groups 
        writer(file_name, msh, groups)

        # active accept
        export_dialog.accept()


    def selectMeshObj():
        """Action to be done when click on Select for Mesh obj. attr."""
        global preview_mesh_obj
        selCount = salome.sg.SelectedCount() # the number of selected items
        if selCount > 1:
            QtGui.QMessageBox.about(None, "HYDROGEO_SALOME",
                                "Functionality is only for one mesh obj selected.")
            return
        elif selCount == 0:
            QtGui.QMessageBox.about(None, "HYDROGEO_SALOME",
                                "Select one valid mesh obj.")
            return
        obj_id = salome.sg.getSelected(0)
        obj_id = salome.myStudy.FindObjectID(obj_id).GetObject()
        export_dialog.setMeshObj(obj_id)


    # ===========================================================================
    # get active module and check if SMESH
    # ===========================================================================
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    # ===========================================================================
    # initialize dialog
    # ===========================================================================
    export_dialog = dialog_export.ExportDialog()
    # Connection of callback functions to the dialog button click signals
    export_dialog.handleAcceptWith(acceptCallBack)
    export_dialog.handleRejectWith(rejectCallBack)
    export_dialog.handleSelectMesh(selectMeshObj)

    export_dialog.open()