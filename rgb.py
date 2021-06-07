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

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(12, GPIO.OUT)
while True:
	GPIO.output(12, GPIO.HIGH)
	time.sleep(1)
	print('off')

	GPIO.output(12, GPIO.LOW)
	time.sleep(1)
	print('on')
