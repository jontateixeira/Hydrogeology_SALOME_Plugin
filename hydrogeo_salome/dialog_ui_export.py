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

# python imports
from PyQt5 import QtWidgets as QtWGui
from PyQt5 import QtGui
from PyQt5 import QtCore

# salome imports
from salome.smesh import smeshBuilder
import SMESH

# plugins import
from . import utilities as utils

class ExportDialog(QtWGui.QDialog):
    """
    This class defines the design of a Qt dialog box dedicated to the
    salome plugin. It presents a UI form that contains parameters 
    for the export mesh format of a grid object selected.
    """

    output_formats = ['legacy vtk', 'MFEM mesh', 'p3matpac (coords and lnods) datablock']

    def __init__(self, parent=None) -> None:
        QtWGui.QDialog.__init__(self, parent)
        self.setupUi()
        self._outputFormatsCombo.currentIndexChanged.connect(self._meshFormatComboChanged)
        self._enableMeshGroups.stateChanged.connect(self._enableGroups)
        self._addGroup.clicked.connect(self._add_groups)
        self._removeGroup.clicked.connect(self._remove_groups)
        self._selectPath.clicked.connect(self._setOutFile)
        self.handleAcceptWith(self.accept)
        self.handleRejectWith(self.reject)
        self._mesh = None
        self._groups = None
        self._groups_dict = {}
        self._enable_mesh_groups = False
        self._mesh_format = self.output_formats[0]

    def setupUi(self):
        self.setObjectName("exportDialog")
        self.resize(800, 400)
        self.setSizeGripEnabled(True)
    
        # principal/main layout
        self._grid_layout = QtWGui.QGridLayout(self)
        self._grid_layout.setObjectName("mainLayout")
    
        # mesh selection layout
        self._mesh_obj_layout = QtWGui.QGridLayout(self)
        self._mesh_obj_layout.setObjectName("meshObjLayout")

        # mesh info
        self._meshLabel = QtWGui.QLabel(self)
        self._meshLabel.setObjectName("meshLabel")
        self._selectMeshButton = QtWGui.QPushButton(self)
        self._selectMeshButton.setObjectName("selectMesh")
        self._selectMeshButton.setCheckable(True)
        self._meshObj = QtWGui.QLineEdit(self)
        self._meshObj.setObjectName("meshObj")
        self._meshObj.setReadOnly(True) # don't edit oe insert nothing!
        self._mesh_obj_layout.addWidget(self._meshLabel, 0, 0)
        self._mesh_obj_layout.addWidget(self._selectMeshButton, 0, 2)
        self._mesh_obj_layout.addWidget(self._meshObj, 0, 1)

        #add layout
        self._grid_layout.addLayout(self._mesh_obj_layout, 0, 0)

        # groups in mesh to export
        self._group_layout = QtWGui.QGridLayout(self)
        self._group_layout.setObjectName("groupLayout")

        # enable check (in order to collect groups in selected mesh)
        self._enableMeshGroups = QtWGui.QCheckBox(self)
        self._enableMeshGroups.setObjectName("enableMeshGroups")
        self._group_layout.addWidget(self._enableMeshGroups, 0, 0, 2, 1)
        #add to layout
        self._grid_layout.addLayout(self._group_layout, 1, 0)

        # groups_selection
        self._group_selection_layout= QtWGui.QGridLayout(self)
        self._group_selection_layout.setObjectName("groupSelectionLayout")
        # table of groups available
        self._groupTable = QtWGui.QTableWidget(self)
        self._groupTable.setObjectName("groupTable")
        self._groupTable.setColumnCount(1)
        self._tableHeader = QtWGui.QTableWidgetItem()
        self._groupTable.setHorizontalHeaderItem(0, self._tableHeader)
        self._groupTable.horizontalHeader().setSectionResizeMode(0, QtWGui.QHeaderView.Stretch)
        self._group_selection_layout.addWidget(self._groupTable, 0, 0, 4, 1)
        # table of groups to export
        self._group2Export = QtWGui.QTableWidget(self)
        self._group2Export.setObjectName("groupToExport")
        self._group2Export.setColumnCount(3)
        self._group2Export.setHorizontalHeaderItem(0,QtWGui.QTableWidgetItem("Groups to export"))
        self._group2Export.setHorizontalHeaderItem(1,QtWGui.QTableWidgetItem("Name"))
        self._group2Export.setHorizontalHeaderItem(2,QtWGui.QTableWidgetItem("Groups type"))
        self._group_selection_layout.addWidget(self._group2Export, 0, 2, 4,1)
        # add/remove group buttons
        self._addGroup = QtWGui.QPushButton(self)
        self._addGroup.setObjectName("addGroup")
        self._addGroup.setText("+")
        self._removeGroup = QtWGui.QPushButton(self)
        self._removeGroup.setObjectName("removeGroup")
        self._removeGroup.setText("-")
        self._group_selection_layout.addWidget(self._addGroup, 1, 1, 1, 1)
        self._group_selection_layout.addWidget(self._removeGroup, 2, 1, 1, 1)
        #add groupSelectionLayout to layout
        self._grid_layout.addLayout(self._group_selection_layout, 2, 0)
        
        #output format
        self._output_format = QtWGui.QGridLayout(self)
        self._output_format.setObjectName("outputFormat")
        self._outputLabel = QtWGui.QLabel(self)
        self._outputLabel.setObjectName("outputLabel")
        self._output_format.addWidget(self._outputLabel, 0, 0)
        self._outputFormatsCombo = QtWGui.QComboBox(self)
        self._outputFormatsCombo.setObjectName("outputFormatsCombo")
        for output in self.output_formats:
            self._outputFormatsCombo.addItem(output)
        self._output_format.addWidget(self._outputFormatsCombo, 0, 1)
        self._grid_layout.addLayout(self._output_format, 3, 0)

        #output
        self._output_file = QtWGui.QGridLayout(self)
        self._output_file.setObjectName("outputFile")
        self._outputFileLabel = QtWGui.QLabel(self)
        self._outputFileLabel.setObjectName("outputFileLabel")
        self._selectPath = QtWGui.QPushButton(self)
        self._selectPath.setObjectName("selectPath")
        self._outFilePath = QtWGui.QLineEdit(self)
        self._outFilePath.setObjectName("outFileLabel")
        self._output_file.addWidget(self._outputFileLabel, 0, 0)
        self._output_file.addWidget(self._outFilePath, 0, 1)
        self._output_file.addWidget(self._selectPath, 0, 2)
        self._grid_layout.addLayout(self._output_file, 4, 0)
        
        # ok and cancel button        
        self.buttonBox = QtWGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWGui.QDialogButtonBox.Cancel|
                                          QtWGui.QDialogButtonBox.NoButton|
                                          QtWGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self._grid_layout.addWidget(self.buttonBox, 5, 0)
    
        self.setWindowTitle("Export meshes")
        # mesh selection
        self._meshLabel.setText("Mesh to export:")
        self._selectMeshButton.setText("Select")
        # groups to export
        self._enableMeshGroups.setText("Export groups as boundary regions")
        self._tableHeader.setText("Available groups")
        # output formats
        self._outputLabel.setText("Output format:")
        # output file 
        self._selectPath.setText("Select")
        self._outputFileLabel.setText("Destination folder:")


        self._meshObj.setToolTip('SMESH obj to export')
        self._enableMeshGroups.setToolTip('Check to export some groups in SMESH obj as boundary regions')
        self._outputLabel.setToolTip('Mesh format to export the SMESH obj.')
        self._outFilePath.setToolTip('full path to export the SMESH obj.')

        # Keep the dialog on top of the windows
        self.setWindowFlags(self.windowFlags() | 
                            QtCore.Qt.WindowStaysOnTopHint)


    def _meshFormatComboChanged(self, select):
        """This set the mesh format selected"""
        self._mesh_format = self._outputFormatsCombo.itemText(select)


    def _enableGroups(self, state):
        """Check box was checked or not and collect groups if mesh was selected"""
        if state == QtCore.Qt.Checked:
            self._enable_mesh_groups = True
            if self._mesh:
                # collect groups and display in the table
                self._groups = []
                for g in self._mesh.GetGroups():
                    if not g.GetTypes():
                        continue
                    if (g.GetTypes()[0] == SMESH.VOLUME or g.GetTypes()[0] == SMESH.FACE):
                        self._groups.append(g)
                self._groupTable.setRowCount(len(self._groups))
                for i,g in enumerate(self._groups):
                    self._groupTable.setItem(i,0, QtWGui.QTableWidgetItem(g.GetName()))
                    self._groups_dict[g.GetName()] = g
        else:
            self._enable_mesh_groups = False
            if self._mesh:
                # erase all groups in table
                self._groups = None
                self._groups_dict = {}
                self._groupTable.setRowCount(0)
                self._group2Export.setRowCount(0)


    def _add_groups(self):
        self.__exchangeTableItens(self._groupTable, self._group2Export)


    def _remove_groups(self):
        self.__exchangeTableItens(self._group2Export, self._groupTable)

      
    def __exchangeTableItens(self, From, To):
        itens_selected = From.selectedItems()
        itens_selected_idx = From.selectedIndexes()
        n = To.rowCount()
        To.setRowCount(n + len(itens_selected))
        for i,g in enumerate(itens_selected):
            group = self._groups_dict[g.text()]
            To.setItem(n+i,0, QtWGui.QTableWidgetItem(group.GetName()))
            To.setItem(n+i,1, QtWGui.QTableWidgetItem(group.GetName()))
            if group.GetTypes()[0] == SMESH.VOLUME:
                To.setItem(n+i,2, QtWGui.QTableWidgetItem('VOLUME'))
            elif group.GetTypes()[0] == SMESH.FACE:
                To.setItem(n+i,2, QtWGui.QTableWidgetItem('FACE'))
            else:
                pass
        for i in itens_selected_idx:
            From.removeRow(i.row())


    def _setOutFile(self):
        selection = ''
        if self._mesh_format.endswith('vtk'):
            out_str = 'vtk legacy File (*.vtk)'
            ext = 'vtk'
        if self._mesh_format.endswith('mesh'):
            out_str = 'MFEM mesh File (*.mesh)'
            ext = 'mesh'
        if self._mesh_format.endswith('datablock'):
            out_str = 'p3matpac nodes datablock File (*.coords);; p3matpac cells datablock File (*.lnods)'
            ext = 'coords'
        all_files_str = 'All Files (*)'        
        selection = out_str + ";;" + all_files_str
        file_dialog = QtWGui.QFileDialog(self, 
                                        "Select an output file", 
                                        self._outFilePath.text(), selection)
        if file_dialog.exec_():
            txt = file_dialog.selectedFiles()[0]
            if txt.split('.')[-1] != ext:
                txt = txt + '.' + ext
            self._outFilePath.setText(txt)


    def handleAcceptWith(self,callbackFunction):
        """This defines the function to be connected to the signal 'accepted()' (click on Ok)"""
        self.buttonBox.accepted.connect(callbackFunction)

    def handleRejectWith(self,callbackFunction):
        """This defines the function to be connected to the signal 'rejected()' (click on Cancel)"""
        self.buttonBox.rejected.connect(callbackFunction)

    def handleCheckedGroups(self,callbackFunction):
        """This defines the function to be connected to the signal 'Groups CheckBox()'"""
        self._enableMeshGroups.clicked.connect(callbackFunction)

    def handleSelectMesh(self,callbackFunction):
        """This defines the function to be connected to the signal 'Mesh select'"""
        self._selectMeshButton.clicked.connect(callbackFunction)

    def accept(self):
        '''Callback function when dialog is accepted (click Ok)'''
        self._wasOk = True
        # We should test here the validity of values
        QtWGui.QDialog.accept(self)

    def reject(self):
        '''Callback function when dialog is rejected (click Cancel)'''
        self._wasOk = False
        QtWGui.QDialog.reject(self)


    def getMeshWriter(self):
        '''get mesh format writer'''
        self._mesh_format = self._outputFormatsCombo.currentText()
        if self._mesh_format.endswith('vtk'):
            return utils.write_vtk
        if self._mesh_format.endswith('mesh'):
            return utils.write_mesh
        if self._mesh_format.endswith('datablock'):
            return utils.write_coords_lnods

    def getOutputFileName(self) -> str:
        '''get full path of output file name'''
        p = self._outFilePath.text()
        if len(p) < 1:
            return None
        else:
            return p

    def getMesh(self):
        '''get mesh name selected'''
        return self._mesh

    def getMeshGroups(self):
        '''get groups selected to export'''
        if self._enable_mesh_groups: 
            groups_out = []
            groups = self._mesh.GetGroups()
            for r in range(self._group2Export.rowCount()):
                g_id = self._group2Export.item(r,0).text()
                if self._group2Export.item(r,2).text() == 'VOLUME':
                    g_type = SMESH.VOLUME
                elif self._group2Export.item(r,2).text() == 'FACE':
                    g_type = SMESH.FACE
                count = 0
                for g in groups:
                    if g.GetName() == g_id:
                        count += 1
                        g2add = g
                # warning / error message / multiples names
                if count != 1:
                    QtWGui.QMessageBox.about(f'Two or more groups have the same name ({g_id})!. Please assign unique group names and retry')
                    return
                    
                groups_out.append(g2add)
            return groups_out
        else:
            return None

    def setMeshObj(self, obj) -> None:
        '''set mesh obj selected and collect groups if enable checkbox was checked'''
        if isinstance(obj, smeshBuilder.meshProxy):
            self._mesh = obj.GetMesh()
            name = smeshBuilder.GetName(obj)
        else:
            self._mesh  = obj
            name = obj.GetName()
        self._meshObj.setText(name)
        if self._enable_mesh_groups:
            # collect groups and display in the table (availables)
            self._group2Export.setRowCount(0)
            self._groups = []
            for g in self._mesh.GetGroups():
                if not g.GetTypes():
                    continue
                if (g.GetTypes()[0] == SMESH.VOLUME or g.GetTypes()[0] == SMESH.FACE):
                    self._groups.append(g)
            self._groupTable.setRowCount(len(self._groups))
            for i,g in enumerate(self._groups):
                self._groupTable.setItem(i,0, QtWGui.QTableWidgetItem(g.GetName()))
                self._groups_dict[g.GetName()] = g