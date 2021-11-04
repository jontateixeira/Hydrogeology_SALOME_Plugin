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


class EmptyDialog(QtWGui.QDialog):
    """
    This class defines the design of a Qt dialog box dedicated to the
    salome plugin. It presents a UI empty form, with purpose to produce 
    one from the scratch.  
    """
    def __init__(self, parent=None) -> None:
        QtWGui.QDialog.__init__(self, parent)
        self.setupUi()
    
    def setupUi(self):
        self.setObjectName("EmptyDialog")
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

        # set input boxes

        # set policy of window
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

        self.setWindowTitle("Empty UI")
        

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