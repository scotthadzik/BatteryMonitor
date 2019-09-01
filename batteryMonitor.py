import LCD1602
import PCF8591 as ADC
import time
import datetime
import os
import sys
from twilio.rest import Client
import env as env


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure

#Twilio Credentials
auth_token = env.TW_TOKEN
account_sid = env.TW_SID

client = Client(account_sid, auth_token)

timeBetweenMeasurements = 1
voltage = 0
ds18b20 = ''
timeOn = 0
count = 0
pushButton = 36 # BCM16 physical pin 36
startingTime = datetime.datetime.now()

def setup():
	sendMessage("Pi has started")
	ADC.setup(0x48)
	global ds18b20
	for i in os.listdir('/sys/bus/w1/devices'):
		if i != 'w1_bus_master1':
			ds18b20 = i
	LCD1602.init(0x27, 1)	# init(slave address, background light)
	LCD1602.clear
	LCD1602.write(0, 0, 'Electrical')
	LCD1602.write(1, 1, 'Trainer')
	time.sleep(2)
	
	
	

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

def countIfOn():
	global count
	readAIN0 = ADC.read(0)
	voltage = readAIN0 # More accurate near 12 V
	print ("Current Battery Voltage: %0.3f" % float(voltage))
	if voltage > 50:
		count+=1
	print ("Number of times tured on" + str(count))
	return count

def sendMessage(messageBody):
	message = client.messages \
                .create(
                     body=messageBody,
                     from_='+18019489202',
                     to='+14358502964'
                 )
	print(message.sid)

def loop():
	while True:
		# readAIN0 = ADC.read(0)
		# voltage = readAIN0 # More accurate near 12 V
		count = countIfOn()
		LCD1602.clear
		currentTime = datetime.datetime.now()
		timeDifference = currentTime - startingTime
		timeDifferenceSec = timeDifference.seconds
		print (timeDifferenceSec)
		if (timeDifference > 20.0):
			print ('inside loop')
			currentTemp = readTemperature()
			formatedTemp = "{:.2f} F".format(currentTemp)
			print ("Current temperature : " + formatedTemp)
			LCD1602.write(0, 0, 'Temp = : ' + formatedTemp)
			LCD1602.write(1, 1, 'On time = ' + str(count))
		
		time.sleep(timeBetweenMeasurements)
		
def destroy():
	ADC.write(0)



if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()


