import RPi.GPIO as GPIO
import os
import sys

def setup():
	IPAddress = '10.0.0.9'

def destroy():
	print('end')

if __name__ == "__main__":
	try:
		setup()
		print("sms sent")
		os.system("python send_sms.py") #Using this line in any python program you can send sms. This call the send_sms.py program and runs
	except KeyboardInterrupt:
		destroy()