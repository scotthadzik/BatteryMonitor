# from guizero import App, Text

# app = App(title="Battery Monitor", layout="grid" )
# batteryMessage      = Text(app, text="Battery Voltage", grid=[0,0])
# temperatureMessage  = Text(app, text="Temperature", grid=[1,0], align="right")

# app.display()

# print("Connected to Pi") # Added to Github

import PCF8591 as ADC
import time

def setup():
	ADC.setup(0x48)

def loop():
	while True:
		print (ADC.read(0))
		time.sleep(5)

def destroy():
	ADC.write(0)

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()