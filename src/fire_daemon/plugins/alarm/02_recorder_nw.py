#!/usr/bin/python
"""
Alarm script to record alarm messages and load them to a server.
"""
import sys
import subprocess
import time
import os

ZVEI_CODES = ["51366", "51367", "51368", "51369", "51370", "51371", "51372", "51373",
              "51374", "51375", "51376", "51377", "51378", "51379", "51399"]


def main(zvei):
    print "02_recorder_nw.py"
    # check lock
    if os.path.exists('/tmp/record.lock'):
        print "Lock is set. Abort."
        exit(0)
    # create lock
    f = open('/tmp/record.lock', 'w')
    f.close()
    print "Created lock."
    # wait
    time.sleep(2)
    # configurations
    RECORD_DURATION = 45  # record duration in seconds
    RECORD_FILE = "/tmp/current_alarm_%s" % "51372"  # record file (tmp)
    SERVER_DIR = "/var/www/a/"
    SERVER_ARCHIVE = "/var/www/alarms/"
    ARCHIVE_DIR = "/home/pi/alarmarchive/"

    # commands
    CMD_RECORD = "arecord -D dsnooper -f S16_LE -c1 -r48000 \
    -t wav -N -d %d %s.wav" % (RECORD_DURATION, RECORD_FILE)

    CMD_ENCODE = "lame -b 64 -B 64 %s.wav" % RECORD_FILE

    CMD_UPLOAD = "scp %s.mp3 peu-srv-upload:%s" % (RECORD_FILE, SERVER_DIR)

    CMD_UPLOAD2 = "scp %s.mp3 peu-srv-upload:%salarm_%s.mp3" % (RECORD_FILE, SERVER_ARCHIVE, str(time.time()))

    CMD_ARCHIVE = "cp %s.mp3 %salarm_%s.mp3" % \
        (RECORD_FILE, ARCHIVE_DIR, str(time.time()))

    CMD_CLEAN = "rm %s.*" % RECORD_FILE

    # execution
    print "Recording..."
    subprocess.call(CMD_RECORD, shell=True)
    print "Encoding..."
    subprocess.call(CMD_ENCODE, shell=True)
    print "Uploading..."
    subprocess.call(CMD_UPLOAD, shell=True)
    print "Wait for 120s"
    time.sleep(120) # wait two minutes, for archive upload
    print "Uploading... 2"
    subprocess.call(CMD_UPLOAD2, shell=True)
    print "Archiving..."
    subprocess.call(CMD_ARCHIVE, shell=True)
    print "Cleanup..."
    subprocess.call(CMD_CLEAN, shell=True)
    print "Finished."

    # release lock
    os.remove('/tmp/record.lock')
    print "Lock released."

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ZVEI_CODES:
            main(sys.argv[1])
    else:
        print "Missing argument: ZVEI code. Exitting."
    exit(0)

