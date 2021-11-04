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

"""
This is the file that is detected by salome in order to load the plugin
Do not rename or move this file!
Check "salome_pluginsmanager.py" for more information
"""

# python imports
import sys
import os

# salome imports
from salome_pluginsmanager import AddFunction

#import plugin component
from hydrogeo_salome import *
from hydrogeo_salome import hydrogeo_interface as interface

# %% setup
plugin_path = ""
# add SALOME_PLUGIN_PATH to Python environment for easier module import
if (os.environ.get("SALOME_PLUGINS_PATH") is not None):
    plugin_path = os.environ.get("SALOME_PLUGINS_PATH") +\
                  os.sep + "hydrogeo_salome"
if not (os.path.exists(plugin_path + os.sep + "hydrogeo_salome_handler.py")):
    import inspect
    plugin_path = os.path.dirname(inspect.getfile(inspect.currentframe())) +\
                  os.sep + "hydrogeo_salome"

sys.path.append(plugin_path)

if not (os.path.exists(plugin_path + os.sep + "__init__.py")):
    sys.exit("No hydrogeology module found")

# ========================================================================
# CARTESIAN GRID MODEL
AddFunction('Hydrogeology Modelling/Cartesian Grid Model',
          'Load and preprocess a cartesian Grid Model',
          interface.init_grid_model)


# ========================================================================
# REALISTC GRID MODEL
AddFunction('Hydrogeology Modelling/Grid Model with constraints',
          'Load and preprocess a Grid Model with constraints',
          interface.constraint_grid_model)


# ========================================================================
# set boundary condition
AddFunction('Hydrogeology Modelling/Boundary Condition',
          'add boundary condition (Head/Recharge constraints)',
          interface.bdr_constraint)


# ========================================================================
# export tools
AddFunction('Hydrogeology Modelling/Export mesh',
          'Export mesh and groups to SOLVER readable format',
          interface.export_mesh)