#!/usr/bin/python
"""
Info script, which sends a pushover notification for special ZVEIs.
"""
import sys
import httplib
import urllib


ZVEI_CODES = ["51366", "51367", "51368", "51369", "51370", "51371", "51372", "51373",
              "51374", "51375", "51376", "51377", "51378", "51379", "51399"]


def main(zvei):
    print "10_pushover.py"
    # load secret data
    f = open("pushover_app_token.txt", "r")
    APP_API_KEY = f.read()
    APP_API_KEY.strip()
    f.close()
    f = open("pushover_user_token.txt", "r")
    USER_API_KEY = f.read()
    USER_API_KEY.strip()
    f.close()
    f = open("alarm_url.txt", "r")
    ALARM_URL = f.read()
    ALARM_URL.strip()
    f.close()

    # build push notification
    MESSAGE = "Einsatz fuer Florian Waldeck! Schleife: %s." % zvei
    # if ZVEI 372, use higher priority
    PRIORITY = 0
    if zvei == "51372":
        PRIORITY = 1
        MESSAGE = "EINSATZ! Florian Nieder-Werbe!"

    # send request to pushover service
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
                 urllib.urlencode({
                                  "token": APP_API_KEY,
                                  "user": USER_API_KEY,
                                  "message": MESSAGE,
                                  "url": ALARM_URL,
                                  "url_title": "Alarm Aufzeichnung",
                                  "priority": PRIORITY,
                                  }),
                 {"Content-type": "application/x-www-form-urlencoded"})
    resp = conn.getresponse()
    print "Pushover request delivered: %s" % str(resp)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ZVEI_CODES:
            main(sys.argv[1])
    else:
        print "Missing argument: ZVEI code. Exitting."
    exit(0)
