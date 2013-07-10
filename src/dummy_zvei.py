"""
    Pi FirePager - Software fire pager for German ZVEI alarm codes

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
Simple dummy script to generate random output which looks like the
output of the 'multimon' tool.
This is used to do off-line tests without de-coding real ZVEI radio codes.
"""

import time
import random


sleeptime = 0.3
alert_probability = 0.2


def generate_alert():
    r = random.randint(0, 99)
    if r < alert_probability * 100:
        return True
    return False


def create_random_alert():
    zvei_code = []
    for i in range(5):
        zvei_code.append(random.randint(0, 9))
        if i > 0 and zvei_code[i] == zvei_code[i - 1]:
            zvei_code[i] = 'e'
    return zvei_code


def run():
    while True:
        if generate_alert():
            zvei_code = create_random_alert()
            for e in zvei_code:
                print "ZVEI: %s" % e
                time.sleep(sleeptime)
        else:
            print "ZVEI: f"
        time.sleep(sleeptime)


if __name__ == '__main__':
    run()
