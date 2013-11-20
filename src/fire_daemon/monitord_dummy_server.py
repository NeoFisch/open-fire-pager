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

"""
    This script builds a simple TCP server that emulates the behavior of the
    'monitord' radio monitor.

    It sends randomly generated alarm messages to the connected client.
    This script is used to test the monitord client of OpenFirePager.
"""

import socket
import time
import random
import os
import binascii


def random_string(length=24):
    """
    Returns a random string with given length.
    """
    return binascii.b2a_hex(os.urandom(length / 2))


def build_zvei_message(zvei_id):
    """
    Build a dummy ZVEI code alarm message in monitord format.
    """
    # Format: 300:timestamp:channelnumber(char):zvei_id(text5):alarm_kind(char):text
    return "300:%s:1:%s:0:%s" % (time.time(), str(zvei_id), random_string(32))


def build_bad_message():
    """
    Builds a random message to simulate errors.
    """
    return random_string(64)


def fetch_random_message(wait_intervall=(0.01, 0.4), test_zvei=51372, test_zvei_rate=0.4, bad_message_rate=0.1):
    """
    Return a tuple (wait_time, message).
    Probability of different message types can be configured.
    """
    # set random wait time for next message
    wait_time = random.uniform(wait_intervall[0], wait_intervall[1])
    # select random message type to send
    r = random.uniform(0.0, 1.0)
    if r < bad_message_rate:
        message = build_bad_message()
    elif r < test_zvei_rate:
        message = build_zvei_message(test_zvei)
    else:
        message = build_zvei_message(random.randint(10000, 99999))
    return (wait_time, message)


def run_typ_server():
    """
    Runs a very simple TCP server, sending random alarm messages.
    Stop it with: CTRL+C in your terminal.
    """
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 9333

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((SERVER_IP, SERVER_PORT))
    while 1:
        print "Waiting for connection ..."
        s.listen(1)
        c, addr = s.accept()
        print "Client connected: %s" % str(addr)
        while 1:
            try:
                wait, message = fetch_random_message()
                print "Sending message: %s" % message
                c.send(message)
                print "Waiting for %f seconds" % wait
                time.sleep(wait)
            except Exception as e:
                print "Error: " + str(e)
                c.close()
                print "Connection closed"
                break
        try:
            c.close()
        except:
            pass


def main():
    print "Started monitord dummy server"
    run_typ_server()
    print "Stopped monitord dummy server"


if __name__ == '__main__':
    main()
