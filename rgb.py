#!/usr/bin/env python3
from gpiozero import LED
from time import sleep

R = LED(12)
G = LED(13)
B = LED(6)

while True:
    # R.on()
    # sleep(1)
    # R.off()
    # sleep(1)
    G.on()
    sleep(1)
    G.off()
    sleep(1)
    B.on()
    sleep(1)
    B.off()
    sleep(1)
