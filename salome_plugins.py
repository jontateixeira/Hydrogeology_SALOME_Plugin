# Copyright (c) 2021 JCT
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
# Main authors: JCT ~ Jonathan Teixeira (https://github.com/jontateixeira; 
#                                        jonathan.teixeira@ufpe.br)
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