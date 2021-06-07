# #!/usr/bin/env python3
# from gpiozero import LED
import time

# R = LED(12)
# G = LED(13)
# B = LED(6)

# R.blink()
# # G.off()
# # B.on()



# while True:
    
# 	B.blink()
rpin = 6

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(rpin, GPIO.OUT)
while True:
	GPIO.output(rpin, GPIO.HIGH)
	time.sleep(1)
	print('off')	

	GPIO.output(rpin, GPIO.LOW)
	time.sleep(1)
	print('on')
