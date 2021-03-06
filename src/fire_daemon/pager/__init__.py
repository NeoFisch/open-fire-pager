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

import logging
import time
import monitord
import plugins
import config


class Pager(object):

    def __init__(self, params):
        self.params = params
        # load configuration
        config.load_config(params.config, basepath=params.path)
        # get configuration values
        self.wakeupinterval = config.DATA["options"]["wakeupinterval"]
        if config.DATA["plugins"]["wakeup_script_dir"].startswith("/"):
            self.wakeup_script_dir = \
                config.DATA["plugins"]["wakeup_script_dir"]
        else:
            self.wakeup_script_dir = params.path \
                + config.DATA["plugins"]["wakeup_script_dir"]

    def run(self):
        self.setup()
        while True:
            self.wakeup()
            time.sleep(self.wakeupinterval)

    def setup(self):
        monitor = monitord.MonitordDriver(self.params)
        monitor.start_monitoring()

    def wakeup(self):
        logging.info("Wakeup!")
        plugins.execute_plugins(self.wakeup_script_dir)
