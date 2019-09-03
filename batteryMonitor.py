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
startingTime = time.time()
temperatureMeasureFreq = 5 # Change this to the number of seconds that the temperature is measured
motorTestFreq = 15 # Change this to the number of seconds that the pump voltage is checked
motorTurnedOver = False # state of the pump
motorStarterONAtTime = time.time()
motorStarterOffAtTime = time.time()
motorStarterRunTime = time.time()

reportTime1= datetime.time(8,00,00)
reportTime2= datetime.time(12,00,00)
reportTime3= datetime.time(16,00,00)
reportTime4= datetime.time(18,00,00)
reportTimeTest = datetime.time(18,50,00)

sentReport = false


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
	global motorTurnedOver
	global motorStarterONAtTime
	global motorStarterOffAtTime
	global motorStarterRunTime
	readAIN0 = ADC.read(0)
	voltage = readAIN0 # More accurate near 12 V
	if voltage > 50 and motorTurnedOver == False: #Increase the count --> use the motorTurnedOver state to verify that the On time is not counted
		count +=1
		motorStarterONAtTime = time.time()
		motorTurnedOver = True
	if voltage < 50 and motorTurnedOver == True: # The motor turned over, but now it is not turning over
		motorTurnedOver = False
		motorStarterOffAtTime = time.time()
		motorStarterRunTime = motorStarterOffAtTime - motorStarterONAtTime
		print(' Starter ran for ' + str(motorStarterRunTime) + ' seconds')
	return count

def sendMessage(messageBody):
	message = client.messages \
                .create(
                     body=messageBody,
                     from_=env.PI_Number,
                     to=env.SMS_Number
                 )
	print(message.sid)

def loop():
	global startingTime
	while True:
		count = countIfOn()
		currentTime = time.time()
		timeDifference = currentTime - startingTime
		if (timeDifference > 20):
			LCD1602.clear
			currentTemp = readTemperature()
			formatedTemp = "{:.2f} F".format(currentTemp)
			#Output to the LCD
			LCD1602.write(0, 0, 'Temp = : ' + formatedTemp)
			LCD1602.write(1, 1, 'Count = : ' + str(count))
			#print to console
			print ("Number of Times Started : " + str(count))
			print ("Current temperature : " + formatedTemp)
			#reset the starting time
			startingTime = time.time()
		if(currentTime > reportTimeTest and sentReport == False):
			print('sendSMS')
			sendMessage('This is a voltage message')
		time.sleep(timeBetweenMeasurements)
		
def destroy():
	ADC.write(0)

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()


