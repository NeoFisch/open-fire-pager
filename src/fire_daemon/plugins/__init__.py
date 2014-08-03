"""
    OpenFirePager - Software fire pager for German ZVEI alarm codes

    Copyright (C) 2013 Manuel Peuster <manuel@peuster.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import logging
import subprocess


def execute_plugins(script_dir, arg=None):
    """
    Execute all scripts within the given folder.
    Add arg as first command line argument.
    """
    script_list = [os.path.join(script_dir, f) for f
                   in os.listdir(script_dir) if
                   os.path.isfile(os.path.join(script_dir, f))]
    script_list.sort()
    for f in script_list:
        try:
            subprocess.Popen([f, str(arg) if arg is not None else ""])
            logging.info("Executing: %s %s"
                         % (f, str(arg) if arg is not None else ""))
        except:
            logging.exception("Script execution error: %s" % str(f))
