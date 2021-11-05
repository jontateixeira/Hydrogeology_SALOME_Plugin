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
# Main authors: JCT ~ Jonathan Teixeira (https://github.com/jontateixeira)
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