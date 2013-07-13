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

import sys
import os
import time
import atexit
import logging
import argparse
from signal import SIGTERM
from pager.pager import Pager


class DaemonBase(object):
    '''
    Base class for creating an UNIX daemon process.
    '''

    def __init__(self, pidfile, stdin=os.devnull, stdout=os.devnull, stderr=os.devnull):
        '''
        Init input values
        '''
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.pid = None

    def fork_process(self):
        """
        Fork two times to create a real UNIX daemon with IO to /dev/null
        """
        try:
            pid = os.fork()  # first fork
            if pid > 0:
                sys.exit(0)  # exit parent
        except OSError, e:
            sys.stderr.write("fork failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        # set base environment
        base_path = os.path.split(sys.argv[0])[0] + "/"
        os.chdir(base_path)
        os.setsid()
        os.umask(0)
        try:
            pid = os.fork()  # second fork
            if pid > 0:
                sys.exit(0)  # exit parent
        except OSError, e:
            sys.stderr.write("fork failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        #redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        #create pidfile
        atexit.register(self.delpid)
        atexit.register(self.shutdownlogger)
        pid = str(os.getpid())
        self.pid = pid
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        '''
        Deletes the pid file.
        '''
        os.remove(self.pidfile)

    def shutdownlogger(self):
        '''
        Shuts the logger down.
        '''
        logging.shutdown()

    def start(self, params=None, daemonize=True):
        """
        Start the daemon
        """
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if pid:
            sys.stderr.write("Start failed. Daemon is already running?\n")
            sys.exit(1)
        # Start the daemon
        print "Starting daemon..."
        if daemonize:
            self.fork_process()
        self.run(params)

    def stop(self):
        """
        Stop the daemon
        """
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if not pid:
            sys.stderr.write("Stop failed. Daemon not running?\n")
            return
        #kill daemon process
        print "Stopping daemon..."
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self, params=None, daemonize=True):
        """
        Restart the daemon
        """
        self.stop()
        self.start(params, daemonize)

    def getPID(self):
        """
        Return the daemon's process id (it's pid or -1)
        """
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            return -1
        return pid

    def run(self, params=None):
        """
        Override this method
        """
        pass


class PagerDaemon(DaemonBase):  # inherits from DaemonBase to build a Unix daemon

    def __init__(self):
        '''
        Constructor
        '''
        super(PagerDaemon, self).__init__("/tmp/firepagerd.pid")

    def setupLogging(self, params):
        '''
        Logging setup.
        '''
        if params is None:
            raise Exception("Missing arguments for logging setup.")
            return
        if params.loglevel == "debug" or params.verbose:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO
        if params.verbose:
            logfile = None
        else:
            logfile = "/tmp/firepagerd.log"
        # setup logging
        logging.basicConfig(filename=logfile, filemode="w", level=loglevel,
                            format="%(asctime)s [%(levelname)-8s] %(message)s")
        logging.debug("OpenFirePager logging enabled with loglevel: DEBUG")

    def start(self, params, daemonize=True):
        '''
        Runs the server.
        '''
        self.setupLogging(params)
        super(PagerDaemon, self).start(params, daemonize)

    def run(self, params=None):
        '''
        Sets up the pager and go into infinity serving loop.
        '''
        logging.info('OpenFirePager daemon running with PID: %s' % str(self.pid))
        p = Pager(params)
        p.run()


def parse_arguments():
    '''
    Initializes command line argument parser.
    Sets up logging environment.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", dest="verbose",
                        action="store_true",
                        help="Runs the daemon directly in the shell. Logs are printed to screen. Loglevel is always: DEBUG.")
    parser.add_argument("-d", "--dummy", dest="dummy",
                        action="store_true",
                        help="Triggers dummy mode. In this mode a dummy script (producing random output) \
                        instead of the multimon ZVEI decoder tool is used.")
    parser.add_argument("-l", "--loglevel", dest="loglevel",
                        choices=['debug', 'info'], help="Defines the used logging level.")
    parser.add_argument("-a", "--action", dest="action",
                        choices=['start', 'stop', 'restart', 'status'],
                        help="Action which should be performed on daemon.")
    params = parser.parse_args()
    return params


if __name__ == '__main__':
    # parse command line parameters
    params = parse_arguments()
    # create daemon instance
    s = PagerDaemon()
    # process command
    if params.action == 'start':
        s.start(params, daemonize=not params.verbose)
    elif params.action == 'stop':
        s.stop()
    elif params.action == 'restart':
        s.restart(params, daemonize=not params.verbose)
    elif params.action == 'status':
        pid = s.getPID()
        if pid > 0:
            print "Daemon is running with PID: %d." % pid
        else:
            print "Daemon is not running."
