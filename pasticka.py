#!/usr/bin/python
# coding=utf-8
import RPi.GPIO as GPIO
from pb.pushbullet_client import PushbulletClient
from gmail.gmail_client import GmailClient
from blink.blinker import Blinker
import logging
import sys, getopt
import json
import time

GPIO.setmode(GPIO.BCM)

LED_PIN = 18
SWITCH_PIN = 17

GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # vs GPIO.PUD_UP
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)

last_check = 0
lastState = GPIO.input(SWITCH_PIN)
CHECK_DELAY_SECS = 0.5  # delay in secs

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

blink = Blinker(LED_PIN)

def load_config():
	config_file_path = "/home/pi/projects/pasticka/config.json"
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hc:", ["configfile="])
	except getopt.GetoptError:
		print 'pasticka.py -c <configfile>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'pasticka.py -c <configfile>'
			sys.exit()
		elif opt in ("-c", "--configfile"):
			config_file_path = arg
	logger.debug("Config file path: {}".format(config_file_path))

	with open(config_file_path) as json_data_file:
		data = json.load(json_data_file)
	return data


config = load_config()


def check_switch(pin):
	stav = GPIO.input(pin)

	global lastState

	if stav == lastState:
		return

	refreshSignalization(stav)

	logger.debug('PIN: {} state: {}'.format(pin, stav))

	if (config["pushbullet"]["active"] == 1):
		pb.send("Pasticka", 'Stav: {}'.format(translateStav(stav)))

	if (config["gmail"]["active"] == 1):
		gm = GmailClient(config["gmail"]["sender"], config["gmail"]["username"], config["gmail"]["password"])
		gm.send([config["gmail"]["to"]], "Pasticka", "Stav: {}".format(translateStav(stav)))
	lastState = stav

def translateStav(stav):
	return "Nastrazena" if stav==1 else "Zaklapnuta"

def refreshSignalization(stav):
	# GPIO.output(LED_PIN, 1 if stav == 0 else 0)
	if stav == 0:
		blink.start(Blinker.QUICK)
	else:
		blink.start(Blinker.HEARTBEAT)


pb = PushbulletClient(config["pushbullet"]["apiKey"])

# GPIO.add_event_detect(SWITCH_PIN, GPIO.BOTH, callback=switch_pin_callback, bouncetime=10)

if __name__ == "__main__":
	logger.debug('Started')

	refreshSignalization(GPIO.input(SWITCH_PIN))

	try:
		while True:
			now = time.time()

			time.sleep(0.1)

			duration = now - last_check
			if duration > CHECK_DELAY_SECS:
				# logger.debug('checking now: {} last: {}'.format(now, last_check))
				last_check = now
				check_switch(SWITCH_PIN)
	except (KeyboardInterrupt, SystemExit):
		logger.debug('Finished')
		raise
	finally:
		blink.stop()
		GPIO.cleanup()

	logger.debug('Finished')
