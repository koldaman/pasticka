#!/usr/bin/python
import RPi.GPIO as GPIO
from pb.pushbullet_client import PushbulletClient
from gmail.gmail_client import GmailClient
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

	logger.debug('PIN: {} state: {}'.format(pin, stav))
	GPIO.output(LED_PIN, stav)

	if (config["pushbullet"]["active"] == 1):
		pb.send("Pasticka", 'Stav: {}'.format(stav))

	if (config["gmail"]["active"] == 1):
		gm = GmailClient(config["gmail"]["sender"], config["gmail"]["username"], config["gmail"]["password"])
		gm.send([config["gmail"]["to"]], "Pasticka", "Stav: {}".format(stav))
	lastState = stav


pb = PushbulletClient(config["pushbullet"]["apiKey"])

# GPIO.add_event_detect(SWITCH_PIN, GPIO.BOTH, callback=switch_pin_callback, bouncetime=10)

if __name__ == "__main__":
	logger.debug('Started')

	try:
		while True:
			now = time.time()

			time.sleep(0.1)

			duration = now - last_check
			if duration > CHECK_DELAY_SECS:
				# logger.debug('checking now: {} last: {}'.format(now, last_check))
				last_check = now
				check_switch(SWITCH_PIN)
	except KeyboardInterrupt:
		GPIO.cleanup()

	logger.debug('Finished')
