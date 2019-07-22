# from guizero import App, Text

# app = App(title="Battery Monitor", layout="grid" )
# batteryMessage      = Text(app, text="Battery Voltage", grid=[0,0])
# temperatureMessage  = Text(app, text="Temperature", grid=[1,0], align="right")

# app.display()

# print("Connected to Pi") # Added to Github

import LCD1602
import PCF8591 as ADC
import time
import os
import sys

timeBetweenMeasurements = 1
voltage = 0
ds18b20 = ''

def setup():
	ADC.setup(0x48)
	# global ds18b20
	# for i in os.listdir('/sys/bus/w1/devices'):
	# 	if i != 'w1_bus_master1':
	# 		ds18b20 = i
	# LCD1602.init(0x27, 1)	# init(slave address, background light)
	# LCD1602.clear
	# LCD1602.write(0, 0, 'Electrical')
	# LCD1602.write(1, 1, 'Trainer')
	# time.sleep(2)

def readTemperature():
#	global ds18b20
	location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'
	tfile = open(location)
	text = tfile.read()
	tfile.close()
	secondline = text.split("\n")[1]
	temperaturedata = secondline.split(" ")[9]
	temperature = float(temperaturedata[2:])
	temperature = temperature / 1000
	temperature = (temperature* 9/5) + 32
	return temperature


def loop():
	while True:
		readAIN0 = ADC.read(0)
		voltage = readAIN0 # More accurate near 12 V
		print ("Current Battery Voltage: %0.3f" % float(voltage))
		# if readTemperature() != None:
		# 	print ("Current temperature : %0.3f F" % readTemperature())
		# 	LCD1602.write(0, 0, 'Temp =')
		# 	LCD1602.write(1, 1, 'On time =')
		time.sleep(timeBetweenMeasurements)
		
def destroy():
	ADC.write(0)

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()
