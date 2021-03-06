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
import threading
import subprocess
import time
import os
import plugins
import config


class MonitordDriver(object):

    def __init__(self, params):
        self.params = params
        self.monitor_thread = MonitoringThread(params)
        self.monitor_thread.setDaemon(True)
        logging.info("Monitord driver initialized.")

    def start_monitoring(self):
        self.monitor_thread.start()


class MonitoringThread(threading.Thread):

    def __init__(self, params):
        threading.Thread.__init__(self)
        self.params = params
        # load configuration values

        # configure monitord binary
        if config.DATA["monitord"]["directory"].startswith("/"):
            # configuration is abs. path
            self.command = config.DATA["monitord"]["directory"]
            self.cwd = config.DATA["monitord"]["directory"]
        else:
            # is relative path
            self.command = params.path + config.DATA["monitord"]["directory"]
            self.cwd = params.path + config.DATA["monitord"]["directory"]
        self.command += config.DATA["monitord"]["executable"]
        # configure alarm script folder
        if config.DATA["plugins"]["alarm_script_dir"].startswith("/"):
            self.alarm_script_dir = config.DATA["plugins"]["alarm_script_dir"]
        else:
            self.alarm_script_dir = params.path \
                + config.DATA["plugins"]["alarm_script_dir"]
        # first part of ZVEI codes
        self.zvei_filter = config.DATA["options"]["zvei_filter"]
        # time between two alarm runs of one ZVEI code
        self.cooldown = config.DATA["options"]["alarm_cooldown"]
        # dict to store the last alarm of a ZVEI code:
        self.last_alarms = {}

    def run(self):
        # run monitord as a subprocess and parse outputs
        try:
            logging.debug("Trying to start monitord: %s" % self.command)
            process = subprocess.Popen(
                [self.command],
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
                )
            logging.info("Monitord process started.")
        except:
            logging.exception("Could not start monitord process. Exit.")
            exit(1)

        # infinite loop to monitor ZVEI decoding
        while True:
            try:
                data = process.stdout.readline()
                # logging.debug("Monitord output: %s" % str(data))
                zvei = self.parse_zvei_code(data)
                if zvei is not None:
                    if zvei in self.last_alarms:
                        if abs(time.time()
                                - self.last_alarms[zvei]) < self.cooldown:
                            continue  # skip execution (cooldown)
                    self.last_alarms[zvei] = time.time()
                    logging.info("Received ZVEI Code: %s" % zvei)
                    plugins.execute_plugins(self.alarm_script_dir, arg=zvei)
            except:
                logging.exception("Error in ZVEI decoding loop.")

    def parse_zvei_code(self, data):
        try:
            if data is not None:
                if "zvei = " in data:
                    zvei = data.split()[2].replace('"', '')
                    if len(zvei) != 5:
                        logging.warning("Bad ZVEI code: %s" % zvei)
                        return None
                    if self.zvei_filter is not None:
                        if not zvei.startswith(self.zvei_filter):
                            return None
                    return int(zvei)
        except:
            return logging.warning("Parsing exception.")
        return None
