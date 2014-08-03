#!/usr/bin/python
"""
Alarm script to record alarm messages and load them to a server.
"""
import sys
import subprocess
import time

ZVEI_CODES = ["51372"]


def main(zvei):
    print "02_recorder_nw.py"
    # configurations
    RECORD_DURATION = 30  # record duration in seconds
    RECORD_FILE = "/tmp/current_alarm_%s" % zvei  # record file (tmp)
    SERVER_DIR = "/var/www/a/"
    ARCHIVE_DIR = "/tmp/archive/"

    # commands
    CMD_RECORD = "arecord -D dsnoop -f S32_LE -c2 -r48000 \
    -t wav -N -d %d %s.wav" % (RECORD_DURATION, RECORD_FILE)

    CMD_ENCODE = "lame -b 64 -B 64 %s.wav" % RECORD_FILE

    CMD_UPLOAD = "scp %s.mp3 peu-srv-upload:%s" % (RECORD_FILE, SERVER_DIR)

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
    print "Archiving..."
    subprocess.call(CMD_ARCHIVE, shell=True)
    print "Cleanup..."
    subprocess.call(CMD_CLEAN, shell=True)
    print "Finished."


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ZVEI_CODES:
            main(sys.argv[1])
            exit(0)
    print "No ZVEI in argument."
    exit(1)
