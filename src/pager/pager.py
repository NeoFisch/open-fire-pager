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
import multimon


class Pager(object):

    def __init__(self, params):
        self.params = params
        logging.info("Pager init.")

    def run(self):
        self.setup()
        while True:
            self.wakeup()
            time.sleep(60 * 60)

    def setup(self):
        mm_zvei = multimon.MultimonZveiDriver(self.params)
        mm_zvei.start_monitoring()

    def wakeup(self):
        logging.info("Wakeup...")


