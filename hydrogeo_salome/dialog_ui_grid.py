# Copyright (C) 2018-2020 JCT
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
import scipy.interpolate as inter

import logging
LOG = logging.getLogger(__name__)

class GridModelDialog(QtWGui.QDialog):
    """
    This class defines the design of a Qt dialog box dedicated to the
    salome plugin. It presents a UI form that contains parameters 
    for the spatial dimensions of grid object.
    """
    def __init__(self, parent=None) -> None:
        QtWGui.QDialog.__init__(self, parent)
        self.setupUi()
        self.handleAcceptWith(self.accept)
        self.handleRejectWith(self.reject)
    
    def setupUi(self):
        self.setObjectName("GridDialog")
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
        self._nx = QtWGui.QLabel(self)
        self._nx.setObjectName("numberOfBlocksInXDirection")
        self._vbox1.addWidget(self._nx)
        
        self._ny = QtWGui.QLabel(self)
        self._ny.setObjectName("numberOfBlocksInYDirection")
        self._vbox1.addWidget(self._ny)

        self._nz = QtWGui.QLabel(self)
        self._nz.setObjectName("numberOfBlocksInZDirection")
        self._vbox1.addWidget(self._nz)

        self._Lx = QtWGui.QLabel(self)
        self._Lx.setObjectName("LengthInXDirection")
        self._vbox1.addWidget(self._Lx)
        
        self._Ly = QtWGui.QLabel(self)
        self._Ly.setObjectName("LengthInYsDirection")
        self._vbox1.addWidget(self._Ly)

        self._Lz = QtWGui.QLabel(self)
        self._Lz.setObjectName("LengthInZDirection")
        self._vbox1.addWidget(self._Lz)

        self._hbox1.addLayout(self._vbox1)

        # set input boxes
        self._vbox2 = QtWGui.QVBoxLayout()
        self._vbox2.setContentsMargins(0,0,0,0)
        self._vbox2.setSpacing(6)
        self._vbox2.setObjectName("_vbox2")

        self._txtNx = QtWGui.QLineEdit(self)
        self._txtNx.setObjectName("txtNx")
        self._vbox2.addWidget(self._txtNx)

        self._txtNy = QtWGui.QLineEdit(self)
        self._txtNy.setObjectName("txtNy")
        self._vbox2.addWidget(self._txtNy)

        self._txtNz = QtWGui.QLineEdit(self)
        self._txtNz.setObjectName("txtNz")
        self._vbox2.addWidget(self._txtNz)

        self._txtLx = QtWGui.QLineEdit(self)
        self._txtLx.setObjectName("txtLx")
        self._vbox2.addWidget(self._txtLx)

        self._txtLy = QtWGui.QLineEdit(self)
        self._txtLy.setObjectName("txtLy")
        self._vbox2.addWidget(self._txtLy)

        self._txtLz = QtWGui.QLineEdit(self)
        self._txtLz.setObjectName("txtLz")
        self._vbox2.addWidget(self._txtLz)

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

        self.setWindowTitle("Setup grid model")
        self._nx.setText("Nx")
        self._ny.setText("Ny")
        self._nz.setText("Nz")
        self._Lx.setText("Lx")
        self._Ly.setText("Ly")
        self._Lz.setText("Lz")

        self._txtNx.setToolTip('Number of cell blocks in x-direction')
        self._txtNy.setToolTip('Number of cell blocks in y-direction')
        self._txtNz.setToolTip('Number of cell blocks in z-direction')
        self._txtLx.setToolTip('Length in x-direction')
        self._txtLy.setToolTip('Length in y-direction')
        self._txtLz.setToolTip('Length in z-direction')

        # Keep the dialog on top of the windows
        self.setWindowFlags(self.windowFlags() | 
                            QtCore.Qt.WindowStaysOnTopHint)

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

    def setData(self, nx, ny, nz, Lx = 1.0, Ly = 1.0, Lz = 1.0):
        self._txtNx.setText(str(nx))
        self._txtNy.setText(str(ny))
        self._txtNz.setText(str(nz))
        self._txtLx.setText(str(Lx))
        self._txtLy.setText(str(Ly))
        self._txtLz.setText(str(Lz))

    def getNumberOfBlock(self):
        try:
            nx=eval(str(self._txtNx.text()))
            ny=eval(str(self._txtNy.text()))
            nz=eval(str(self._txtNz.text()))
        except:
            print("")

        return nx, ny, nz

    def getDataLength(self):
        try:
            Lx=eval(str(self._txtLx.text()))
            Ly=eval(str(self._txtLy.text()))
            Lz=eval(str(self._txtLz.text()))
        except:
            print("")

        return Lx, Ly, Lz



class GridModelWithConstraintDialog(GridModelDialog):
    
    def setupUi(self):
        self.setObjectName("GridDialog")
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
        self._nx = QtWGui.QLabel(self)
        self._nx.setObjectName("numberOfBlocksInXDirection")
        self._vbox1.addWidget(self._nx)
        
        self._ny = QtWGui.QLabel(self)
        self._ny.setObjectName("numberOfBlocksInYDirection")
        self._vbox1.addWidget(self._ny)

        self._nz = QtWGui.QLabel(self)
        self._nz.setObjectName("numberOfBlocksInZDirection")
        self._vbox1.addWidget(self._nz)
        
        self._constraints = QtWGui.QLabel(self)
        self._constraints.setObjectName("constraintSapefile")
        self._vbox1.addWidget(self._constraints)
        
        self._topHoriz = QtWGui.QLabel(self)
        self._topHoriz.setObjectName("topHorizon")
        self._vbox1.addWidget(self._topHoriz)
        
        self._botHoriz = QtWGui.QLabel(self)
        self._botHoriz.setObjectName("botHorizon")
        self._vbox1.addWidget(self._botHoriz)
        
        self._interpFun = QtWGui.QLabel(self)
        self._interpFun.setObjectName("interpolation")
        self._vbox1.addWidget(self._interpFun)

        self._hbox1.addLayout(self._vbox1)
        self._hbox1.addLayout(self._vbox1)

        # set input boxes
        self._vbox2 = QtWGui.QVBoxLayout()
        self._vbox2.setContentsMargins(0,0,0,0)
        self._vbox2.setSpacing(6)
        self._vbox2.setObjectName("_vbox2")

        self._txtNx = QtWGui.QLineEdit(self)
        self._txtNx.setObjectName("txtNx")
        self._vbox2.addWidget(self._txtNx)

        self._txtNy = QtWGui.QLineEdit(self)
        self._txtNy.setObjectName("txtNy")
        self._vbox2.addWidget(self._txtNy)

        self._txtNz = QtWGui.QLineEdit(self)
        self._txtNz.setObjectName("txtNz")
        self._vbox2.addWidget(self._txtNz)
        
        self._txtconstraints = QtWGui.QLineEdit(self)
        self._txtconstraints.setObjectName("txtConstshapefile")
        self._vbox2.addWidget(self._txtconstraints)
        
        self._txtTopHorizon = QtWGui.QLineEdit(self)
        self._txtTopHorizon.setObjectName("txtTophorizon")
        self._vbox2.addWidget(self._txtTopHorizon)
        
        self._txtBotHorizon = QtWGui.QLineEdit(self)
        self._txtBotHorizon.setObjectName("txtBottomhorizon")
        self._vbox2.addWidget(self._txtBotHorizon)
        
        self._txtInterp = QtWGui.QLineEdit(self)
        self._txtInterp.setObjectName("txtInterpolation")
        self._vbox2.addWidget(self._txtInterp)

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

        self.setWindowTitle("Setup grid model")
        self._nx.setText("Nx")
        self._ny.setText("Ny")
        self._nz.setText("Nz")
        self._constraints.setText("model area limits")
        self._topHoriz.setText("top horizon")
        self._botHoriz.setText("bottom horizon")
        self._interpFun.setText("Interpolation method")
        
        self._txtNx.setToolTip('Number of cell blocks in x-direction')
        self._txtNy.setToolTip('Number of cell blocks in y-direction')
        self._txtNz.setToolTip('Number of cell blocks in z-direction')
        self._txtconstraints.setToolTip('Full path of model constraints/limits (shapefile format)')
        self._txtTopHorizon.setToolTip('Full path of top horizon file (ID xyz format)')
        self._txtBotHorizon.setToolTip('Full path of Bottom horizon file (ID xyz format)')
        self._txtInterp.setToolTip('Interpolation method: multiquadric, inverse, gaussian,[linear], cubic, quintic')

        self.handleAcceptWith(self.accept)
        self.handleRejectWith(self.reject)

        # Keep the dialog on top of the windows
        self.setWindowFlags(self.windowFlags() | 
                            QtCore.Qt.WindowStaysOnTopHint)

    def setData(self, nx, ny, nz):
        self._txtNx.setText(str(nx))
        self._txtNy.setText(str(ny))
        self._txtNz.setText(str(nz))
        self._txtconstraints.setText("shapefile format")
        self._txtBotHorizon.setText("ID+xyz delimited format")
        self._txtTopHorizon.setText("ID+xyz delimited format")
        self._txtInterp.setText("linear")
    

    def getConstraintArea(self):
        fullpath = self._txtconstraints.text()
        ext = fullpath[-4:]
        if ext.lower() != '.shp':
            LOG.critical('File name provided is not a shapefile')

        if not (os.path.exists(fullpath)):
            return None
        else:
            try:
                # Open shapefile
                sf = shapefile.Reader(fullpath)

                # Get points ~ has only one shape!!
                shp = sf.shapes()[0]

                # # Collect points
                pts = np.asarray(shp.points)
                return pts
            except:
                return None
    

    def getTopHorizon(self):
        fullpath = self._txtTopHorizon.text()
        if not (os.path.exists(fullpath)):
            return None
        else:
            try:
                # Get top horizon data
                d = np.loadtxt(fullpath, skiprows=1, usecols=[1, 2, 3])

                # Get points ~ has only one shape!!
                xt = d[:, 0]
                xx = [np.min(xt), np.max(xt)]
                yt = d[:, 1]
                yy = [np.min(yt), np.max(yt)]
                zt = d[:, 2]

                # interpolate verticies
                return inter.Rbf(xt, yt, zt, function=self._txtInterp.text(), smooth=100)
            except:
                return None
    

    def getBottomHorizon(self):
        fullpath = self._txtBotHorizon.text()
        if not (os.path.exists(fullpath)):
            return None
        else:
            try:
                # Get bottom horizon data
                d = np.loadtxt(fullpath, skiprows=1, usecols=[1, 2, 3])

                # Get points ~ has only one shape!!
                xb = d[:, 0]
                xx = [np.min(xb), np.max(xb)]
                yb = d[:, 1]
                yy = [np.min(yb), np.max(yb)]
                zb = d[:, 2]

                # interpolate verticies
                return inter.Rbf(xb, yb, zb, function=self._txtInterp.text(), smooth=100)
            except:
                return None