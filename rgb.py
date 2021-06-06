#!/usr/bin/env python3
from gpiozero import LED
from time import sleep

R = LED(32)
G = LED(33)
B = LED(31)

while True:
    R.on()
    sleep(1)
    R.off()
    sleep(1)
