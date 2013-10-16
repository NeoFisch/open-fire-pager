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
import socket
import time
import urllib2
import time


class MonitordTcpDriver(object):

    def __init__(self, params):
        self.params = params
        self.monitor_thread = MonitoringThread()
        self.monitor_thread.setDaemon(True)

        logging.info("Monitord TCP driver initialized.")

    def start_monitoring(self):
        self.monitor_thread.start()


class MonitoringThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.last_alarm = 0

    def connect(self):
        connected = False
        while not connected:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", 9333))
                #s.settimeout(2)
                connected = True
                logging.info("Connected to: 127.0.0.1:9333")
            except:
                logging.info("Connection refused. Retry ...")
                time.sleep(0.5)
        return s

    def run(self):
        logging.info("Monitoring started ...")
        s = self.connect()

        while True:
            try:
                data = s.recv(4096)
            except socket.timeout, e:
                err = e.args[0]
                # if timeout occurs: sleep a second
                if err == 'timed out':
                    print "Socket timeout"
                    time.sleep(1)
                    continue
            except socket.error, e:
                logging.exception("TCP exception:")
            else:
                if len(data):
                    logging.debug("Message received from monitord: %s" % data)
                    message_parts = data.split(":")
                    for p in message_parts:
                        if p == "51372":  # Pager id FF Nieder- Werbe
                            self.alert()
                else:
                    try:
                        s.close()
                    except:
                        logging.exception("TCP Close exception:")
                    s = self.connect()

    def alert(self):
        if (time.time() - self.last_alarm) > 300:  # 5 minute cool down
            self.last_alarm = time.time()
            data = '0'
            tries = 0
            res = None
            while data != '1' and tries < 5:
                try:
                    res = urllib2.urlopen("http://alarm-url.com/alarm")
                except:
                    logging.exception("Exception in URL alarm request.")
                if res is not None:
                    data = res.read()
                tries += 1
            logging.info(" *** ALARM for ZVEI: 51372 ***")
