# from guizero import App, Text

# app = App(title="Battery Monitor", layout="grid" )
# batteryMessage      = Text(app, text="Battery Voltage", grid=[0,0])
# temperatureMessage  = Text(app, text="Temperature", grid=[1,0], align="right")

# app.display()

# print("Connected to Pi") # Added to Github

import PCF8591 as ADC
import time
voltage = 0

def setup():
	ADC.setup(0x48)

def convertToVoltage(i2CData):
	byteValue = int.from_bytes(b'\x00\x10', byteorder='little')
	return byteValue

def loop():
	while True:
		readAIN0 = ADC.read(0)
		voltage = convertToVoltage(readAIN0)
		print (voltage)
		time.sleep(5)

def destroy():
	ADC.write(0)

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()