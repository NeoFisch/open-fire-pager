#!/usr/bin/python
"""
Awake script to trigger SMS alarm alive monitor: FF Nieder-Werbe.
"""
import sys
import requests


def main():
    print "01_allivemessage.py"
    # load alarm url
    f = open("data_awakeurl.txt", "r")
    aurl = f.read()
    f.close()
    aurl = aurl.strip()
    print "Awake URL: %s" % aurl
    print "Sending request..."
    r = requests.get(aurl)
    print "... done."
    print "Result: Code: %s Body: %s" % (r.status_code, r.text)


if __name__ == '__main__':
    main()
