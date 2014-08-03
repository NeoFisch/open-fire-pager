#!/usr/bin/python
"""
Alarm script to trigger SMS alarm: FF Nieder-Werbe.
"""
import sys

ZVEI_CODES = ["51372"]


def main():
    print "01_alarm_nw.py"


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ZVEI_CODES:
            main()
