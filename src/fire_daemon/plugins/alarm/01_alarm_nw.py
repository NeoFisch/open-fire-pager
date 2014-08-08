#!/usr/bin/python
"""
Alarm script to trigger SMS alarm: FF Nieder-Werbe.
"""
import sys
import requests


ZVEI_CODES = ["51372"]


def main():
    print "01_alarm_nw.py"
    # load alarm url
    f = open("data_alarmurl.txt", "r")
    aurl = f.read()
    f.close()
    aurl = aurl.strip()
    print "Alarm URL: %s" % aurl
    print "Sending request..."
    r = requests.get(aurl)
    print "... done."
    print "Result: Code: %s Body: %s" % (r.status_code, r.text)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ZVEI_CODES:
            main()
