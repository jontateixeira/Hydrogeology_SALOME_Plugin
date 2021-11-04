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
# Main authors: Jonathan Teixeira (https://github.com/jontateixeira)
#
"""
This file contains initialization procedures.
NOTE: This file have just the logging init.
"""

def IsExecutedInSalome():
    """Function to check if the script is being executed inside Salome."""
    # python imports
    import os
    return "SALOME_ROOT_DIR" in os.environ


def __CheckSalomeIsInitialized():
    """Function to check if salome was initialized before.
    Salome must be initialized before importing the plugin,
    because the plugin uses it already during importing!
    If it is not initialized some strange errors can happen.
    It is a "private" function to not pollute the global namespace.
    """
    if IsExecutedInSalome():
        import salome
        # make sure that salome is initialized properly
        # see "__init__.py" of the salome python kernel => "salome_init"
        if salome.salome_initial:
            raise Exception('Trying to use salome but "salome.salome_init()" was not called!')


def __InitializeLogging():
    """Initialize the logging of the plugin.
    It is a "private" function to not pollute the global namespace.
    """
    # python imports
    import sys
    import logging

    # salome_hydrogeology imports
    from . import plugin_logging as gsLOG
    
    gsLOG.InitializeLogging()

    logger = logging.getLogger("HYDROGEOLOGY SALOME")
    logger.debug('Python version: {}'.format(".".join(map(str, sys.version_info[:3]))))
    if sys.version_info[1] < 6:
        logger.warning('It is recommended to use at least Python version 3.6, support for older versions will be dropped in the future!')
    logger.debug('Operating system: {}'.format(sys.platform))


__CheckSalomeIsInitialized()
__InitializeLogging()