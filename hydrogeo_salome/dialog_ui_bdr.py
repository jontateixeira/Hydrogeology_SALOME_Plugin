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

try:
    from PyQt4 import QtGui as QtWGui
    from PyQt4 import QtCore
except ImportError:
    from PyQt5 import QtWidgets as QtWGui
    from PyQt5 import QtGui
    from PyQt5 import QtCore

import os
import shapefile # pyshp
import numpy as np

import logging
LOG = logging.getLogger(__name__)

class BoundaryConditionDialog(QtWGui.QDialog):
    """
    This class defines the design of a Qt dialog box dedicated to the
    salome plugin. It presents a UI form that contains parameters 
    for the boundary condition of a grid object.
    """
    def __init__(self, parent=None) -> None:
        QtWGui.QDialog.__init__(self, parent)
        self.setupUi()
        self.meshObjCombo.currentIndexChanged.connect(self._meshObjComboChanged)
        self._checkAtSurf.stateChanged.connect(self.assignAtSurface)
        self.handleAcceptWith(self.accept)
        self.handleRejectWith(self.reject)
        self.setData(1e3,1e3)
    
    def setupUi(self):
        self.setObjectName("BdrDialog")
        self.resize(400, 300)
        self._hbox = QtWGui.QHBoxLayout(self)
        self._hbox.setContentsMargins(9,9,9,9)
        self._hbox.setSpacing(6)
        self._hbox.setObjectName("_hbox")

        self._hbox1 = QtWGui.QHBoxLayout()
        self._hbox1.setContentsMargins(0,0,0,0)
        self._hbox1.setSpacing(6)
        self._hbox1.setObjectName("_hbox1")
        
        self._vbox = QtWGui.QVBoxLayout()
        self._vbox.setContentsMargins(0,0,0,0)
        self._vbox.setSpacing(6)
        self._vbox.setObjectName("_vbox")
        
        self._vbox1 = QtWGui.QVBoxLayout()
        self._vbox1.setContentsMargins(0,0,0,0)
        self._vbox1.setSpacing(6)
        self._vbox1.setObjectName("_vbox1")
        
        # create fields names        
        self._shaperegion = QtWGui.QLabel(self)
        self._shaperegion.setObjectName("regions")
        self._vbox1.addWidget(self._shaperegion)

        self._dxLabel = QtWGui.QLabel(self)
        self._dxLabel.setObjectName("criterionX")
        self._vbox1.addWidget(self._dxLabel)
        
        self._dyLabel = QtWGui.QLabel(self)
        self._dyLabel.setObjectName("criterionY")
        self._vbox1.addWidget(self._dyLabel)

        self._bdrNameLabel = QtWGui.QLabel(self)
        self._bdrNameLabel.setObjectName("prefix")
        self._vbox1.addWidget(self._bdrNameLabel)

        self._meshObjLabel = QtWGui.QLabel(self)
        self._meshObjLabel.setObjectName("meshobj")
        self._vbox1.addWidget(self._meshObjLabel)

        self._checkAtSurfLabel = QtWGui.QLabel(self)
        self._checkAtSurfLabel.setObjectName("checkAtSurfLabel")
        self._vbox1.addWidget(self._checkAtSurfLabel)

        self._hbox1.addLayout(self._vbox1)

        # set input boxes
        self._vbox2 = QtWGui.QVBoxLayout()
        self._vbox2.setContentsMargins(0,0,0,0)
        self._vbox2.setSpacing(6)
        self._vbox2.setObjectName("_vbox2")

        self._regions = QtWGui.QLineEdit(self)
        self._regions.setObjectName("str_regions")
        self._vbox2.addWidget(self._regions)

        self._dx = QtWGui.QLineEdit(self)
        self._dx.setObjectName("str_dx")
        self._vbox2.addWidget(self._dx)

        self._dy = QtWGui.QLineEdit(self)
        self._dy.setObjectName("str_dy")
        self._vbox2.addWidget(self._dy)

        self._bdrName = QtWGui.QLineEdit(self)
        self._bdrName.setObjectName("bdrName")
        self._vbox2.addWidget(self._bdrName)

        # public to populate combobox at runtime
        self.meshObjCombo = QtWGui.QComboBox(self)
        self.meshObjCombo.setObjectName("mObjCombo")
        self._vbox2.addWidget(self.meshObjCombo)

        self._checkAtSurf = QtWGui.QCheckBox("Only one Surface", self)
        self._checkAtSurf.setObjectName("checkAtSurf")
        self._vbox2.addWidget(self._checkAtSurf)

        self._hbox1.addLayout(self._vbox2)
        self._vbox.addLayout(self._hbox1)
        
        spacerItem = QtWGui.QSpacerItem(20, 40, QtWGui.QSizePolicy.Minimum, 
            QtWGui.QSizePolicy.Expanding)
        self._vbox.addItem(spacerItem)
        
        self.buttonBox = QtWGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWGui.QDialogButtonBox.Cancel|
                                          QtWGui.QDialogButtonBox.Apply|
                                          QtWGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self._vbox.addWidget(self.buttonBox)
        self._hbox.addLayout(self._vbox)

        self.setWindowTitle("Setup boundary condition on model")
        self._shaperegion.setText("Regions")
        self._dxLabel.setText("dx criteria")
        self._dyLabel.setText("dy criteria")
        self._bdrNameLabel.setText("Group Name")
        self._meshObjLabel.setText("Mesh Obj")

        self._dx.setToolTip('Maximum distance in x-direction to assign region')
        self._dy.setToolTip('Maximum distance in y-direction to assign region')
        self._bdrName.setToolTip('Prefix group name')
        self._regions.setToolTip('Full path of shapefile, or xyz, marking region to attribute boundary condition')
        self.meshObjCombo.setToolTip('SMESH obj to create new groups')
        self._checkAtSurf.setToolTip('Assign on faces at surface (maximum z-coordinate)')

        # Keep the dialog on top of the windows
        self.setWindowFlags(self.windowFlags() | 
                            QtCore.Qt.WindowStaysOnTopHint)

    def _meshObjComboChanged(self, select):
        """This set the mesh obj selected"""
        self._meshObj = self.meshObjCombo.itemText(select)

    def assignAtSurface(self, state):
        """Check if boundary condition is assign at surface (or on faces inside regions)"""
        if state == QtCore.Qt.Checked:
            self._atSurface = True
        else:
            self._atSurface = False

    def handleAcceptWith(self,callbackFunction):
        """This defines the function to be connected to the signal 'accepted()' (click on Ok)"""
        self.buttonBox.accepted.connect(callbackFunction)

    def handleRejectWith(self,callbackFunction):
        """This defines the function to be connected to the signal 'rejected()' (click on Cancel)"""
        self.buttonBox.rejected.connect(callbackFunction)

    def handleApplyWith(self,callbackFunction):
        """This defines the function to be connected to the signal 'apply()' (click on Apply)"""
        button = self.buttonBox.button(QtWGui.QDialogButtonBox.Apply)
        button.clicked.connect(callbackFunction)

    def accept(self):
        '''Callback function when dialog is accepted (click Ok)'''
        self._wasOk = True
        # We should test here the validity of values
        QtWGui.QDialog.accept(self)

    def reject(self):
        '''Callback function when dialog is rejected (click Cancel)'''
        self._wasOk = False
        QtWGui.QDialog.reject(self)

    def wasOk(self):
        return self._wasOk

    def setData(self, dx, dy, prefix = "zone"):
        self._dx.setText(str(dx))
        self._dy.setText(str(dy))
        self._bdrName.setText(prefix)
        self._regions.setText("None")
        self._meshObj = None
        self._atSurface = False

    def getCriteria(self):
        try:
            dx=eval(str(self._dx.text()))
            dy=eval(str(self._dy.text()))
        except:
            return None

        return dx, dy

    def getGroupName(self):
        try:
            name=self._bdrName.text()
        except:
            name = "Group"
        return name

    def getMesh(self):
        if len(self._meshObj) > 0:
            return self._meshObj
        else:
            return None

    def getAssignAtSurface(self):
        return self._atSurface

    def getBdrRegion(self):
        fullpath = self._regions.text()
        if not (os.path.exists(fullpath)):
            return None
        else:
            try:
                if fullpath[-4:].lower() == '.txt':
                    # Get region limits (xy data)
                    d = [np.loadtxt(fullpath.strip(), skiprows=1, usecols=[1, 2])]
                elif fullpath[-4:].lower() == '.shp':
                    # Get region limits (xy data)
                    sf = shapefile.Reader(fullpath)
                    # collect all regions
                    shp = sf.shapes()
                    d = []
                    for s in shp:
                        d.append(np.asarray(s.points))
                elif fullpath[-4:].lower() == '.csv':
                    # Get region limits (xy data)
                    d = [np.loadtxt(fullpath.strip(), skiprows=1, delimiter=',', usecols=[1, 2])]
                return d
            except:
                return None