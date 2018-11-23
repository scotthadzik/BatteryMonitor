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

def convertToVoltage(valueInBytes):
	# byteValue = int.from_bytes(b'\x00\x10', byteorder='little')
	byteValue = 0
	for byte in valueInBytes:
		byteValue = byteValue + int(byte)
	return byteValue

def loop():
	while True:
		readAIN0 = ADC.read(0)
		print('reading is', readAIN0)
		voltage = readAIN0/12.8
		print (voltage)
		time.sleep(5)
		# 154 is 12 V ~ 12.24
		# 63  is 05 V ~ 23.27
		# 36  is 3.3V ~ 26.55
		# 0   is 0.0V ~ 31.00


def destroy():
	ADC.write(0)

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()