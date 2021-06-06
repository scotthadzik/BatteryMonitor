#!/usr/bin/env python3
from gpiozero import LED
from time import sleep

R = LED(12)
G = LED(13)
B = LED(6)

R.off()
G.off()
B.on()



while True:
    
	B.blink()
