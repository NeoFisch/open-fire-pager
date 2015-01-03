OpenFirePager
=============

## ALSA USB Sound Setup

1. Plugin USB Sound card

2. Install packages
	´sudo apt-get install alsa-utils libasound2-dev

3. Checks
	* sudo lsusb: List USB
	*  aplay -l: List Audio devices to find USB (eg. card 1 / subdevice #0)

3. Edit configuration
	Edit ´etc/asound.conf´
	(see aspund.conf in repo)

4. reboot


## Sound checks:

* Record: arecord -D dsnooper -f S16_LE -c1 -r48000 -t wav -N -d 30 test.wav





