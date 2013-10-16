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
import time
import subprocess


class MultimonZveiDriver(object):

    def __init__(self, params):
        self.params = params
        self.cmd_multimon = ['/home/manuel/multimonNG/build/multimon-ng', '-a', 'ZVEI1']
        self.cmd_dummy = ['python', '/home/manuel/open-fire-pager/pager/dummy_zvei.py']

        self.command = self.cmd_multimon
        if params.dummy:
            self.command = self.cmd_dummy

        self.monitor_thread = MonitoringThread(self.command)
        self.monitor_thread.setDaemon(True)

       

    def start_monitoring(self):
        self.monitor_thread.start()



class MonitoringThread(threading.Thread):

    def __init__(self, command):
        threading.Thread.__init__(self)
        self.command = command
        
    def run(self):
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=open('/dev/null'))
        out_buffer = ""

        # analyze outputs of multimon
        while True:
            out = process.stdout.readline()
            out = self.cleanup_output(out)
            if not out is None:
                if not out == 'F':
                    out_buffer += out
                else:
                    out_buffer = ""
            if len(out_buffer) > 4:
                output_list = self.build_output_list(out_buffer)
                out_buffer = ""
                if not output_list is None:
                    logging.info("ZVEI code detected: %s" % str(output_list))
                else:
                    logging.info("None detected.")
            time.sleep(0.1)

    def cleanup_output(self, output):
        """
        Removes un-needed information from input string.
        """
        if output is None:
            return None
        if "Enabled" in output:
            return None
        output = str(output)
        output = output.replace("ZVEI: ", "")
        output = output.replace("ZVEI1: ", "")
        output = output.replace("ZVEI2: ", "")
        output = output.replace("ZVEI3: ", "")
        output = output.replace("DZVEI: ", "")
        output = output.strip()
        output = output.replace("f", "F")
        output = output.replace("e", "E")
        if len(output) > 0:
            return output
        return None


    def build_output_list(self, output):
        """
        Cleans up the code and returns a 5 element list of integer or None.
        """
        # ensure that only int < 9 and E is in the string and build a list
        allowed_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'E']
        output_list = []
        for c in output:
            if c in allowed_chars:
                output_list.append(c)
            else:
                if c != 'F':
                    logging.error("Bad character detected: %s", str(c))
        if len(output_list) <= 0:
            return None
        # remove double value indicators and cast to integers
        for i in range(1, len(output_list)):
            if output_list[i] == 'E':
                output_list[i] = output_list[i - 1]
        # cast to integer
        for i in range(0, len(output_list)):
            output_list[i] = int(output_list[i])
        # work on codes which is to long (try to find local pattern, e.g. 51 for Gemany/WA-FKB)
        if len(output_list) > 5:
            logging.debug("Detected ZVEI code too long: '%s'. Trying local code detection." % str(output_list))
            for i in range(0, len(output_list) - 1):
                if output_list[i] == 5 and output_list[i + 1] == 1:
                    break
                else:
                    output_list[i] = -1
            # remove all elements before local code starts 
            output_list = [x for x in output_list if x > 0]
            # early skip
            if len(output_list) <= 1:
                return None
            # trim list to 5 elements
            output_list = output_list[0:5]
        # error if code is malformed at this point
        if len(output_list) != 5:
            logging.error("Detected ZVEI code has wrong length: '%s'" % str(output_list))
            return None
        return output_list
