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


class MonitordDriver(object):

    def __init__(self, params):
        self.params = params
        self.monitor_thread = MonitoringThread()
        self.monitor_thread.setDaemon(True)
        logging.info("Monitord driver initialized.")

    def start_monitoring(self):
        self.monitor_thread.start()


class MonitoringThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.command = ["/home/manuel/monitor/trunk/monitord/monitord"]
        self.cwd = "/home/manuel/monitor/trunk/monitord/"
        self.alarm_script_dir = "plugins/alarm"
        # dict to store the last alarm of a ZVEI code:
        self.last_alarms = {}
        # time between two alarm runs of one ZVEI code
        self.cooldown = 60


    def run(self):
        logging.info("Monitoring started ...")
        process = subprocess.Popen(self.command, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # analyze outputs of monitord, and execute alarm scripts:
        while True:
            zvei = self.parse_zvei_code(process.stdout.readline())
            if zvei is not None:
                logging.info("Received ZVEI Code: %s" % zvei)
                if zvei in self.last_alarms:
                    if abs(time.time() - self.last_alarms[zvei]) < self.cooldown:
                        continue # skip execution (cooldown)
                self.last_alarms[zvei] = time.time()
                self.execute_alarm_scripts(zvei)

    def parse_zvei_code(self, data):
        try:
            if data is not None:
                if "zvei = " in data:
                    zvei = data.split()[2].replace('"', '')
                    if len(zvei) != 5:
                        logging.warning("Bad ZVEI code: %s" % zvei)
                        return None
                    return int(zvei)
        except:
            return logging.warning("Parsing exception.")
        return None

    def execute_alarm_scripts(self, zvei):
        script_list = [os.path.join(self.alarm_script_dir, f) for f in os.listdir(self.alarm_script_dir) if os.path.isfile(os.path.join(self.alarm_script_dir,f)) ]
        script_list.sort()
        for f in script_list:
            try:
                subprocess.Popen([f, str(zvei)])
            except:
                logging.error("Script execution error: %s" % str(f))



