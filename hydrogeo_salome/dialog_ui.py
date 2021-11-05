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