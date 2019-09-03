import LCD1602
import PCF8591 as ADC
import time
import datetime
import os
import sys
from twilio.rest import Client
import env as env
from ReportTime import ReportTime


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
dayLowTemp = 200
dayHighTemp = -50

motorTestFreq = 15 # Change this to the number of seconds that the pump voltage is checked
motorTurnedOver = False # state of the pump
motorStarterONAtTime = time.time()
motorStarterOffAtTime = time.time()
motorStarterRunTime = time.time()
shortestCrank = 500
longestCrank = 0

dateNow = datetime.datetime.now()
currentHour = dateNow.hour
beginningOfTheDay = True

reports = [
ReportTime(8,' 8:00 a.m. '),
ReportTime(12,' 12:00 p.m. '),
ReportTime(16,' 4:00 p.m. '),
ReportTime(20,' 8:00 p.m. '),
]


index = 0 # report time index tracking

sentReport = False


def setup():
	# sendMessage("Pi has started") TODO: Remove this comment
	global index
	global beginningOfTheDay
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
	reportTemperature()

def readTemperature():
#	global ds18b20
	global dayHighTemp
	global dayLowTemp
	location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'
	tfile = open(location)
	text = tfile.read()
	tfile.close()
	secondline = text.split("\n")[1]
	temperaturedata = secondline.split(" ")[9]
	temperature = float(temperaturedata[2:])
	temperature = temperature / 1000
	temperature = (temperature* 9/5) + 32
	if (temperature < dayLowTemp):
		dayLowTemp = temperature
	if (temperature > dayHighTemp):
		dayHighTemp = temperature
	return temperature

def countIfOn():
	global count
	global motorTurnedOver
	global motorStarterONAtTime
	global motorStarterOffAtTime
	global motorStarterRunTime
	global dayHighTemp
	global dayLowTemp
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

def reportTemperature():
	global dayHighTemp
	global dayLowTemp
	currentTemp = readTemperature()
	formatedTemp = "{:.2f} F".format(currentTemp)
	formatedLowTemp = "{:.2f} F".format(dayLowTemp)
	formatedHighTemp = "{:.2f} F".format(dayHighTemp)
	# Output to the LCD
	LCD1602.write(0, 0, 'Temp = : ' + formatedTemp)
	print ("Current temperature : " + formatedTemp)
	print ("High temperature today: " + formatedHighTemp)
	print ("Low temperature today: " + formatedLowTemp)
	return formatedTemp

def loop():
	global startingTime
	global sentReport
	global dayHighTemp
	global dayLowTemp
	global index
	while True:
		count = countIfOn()
		currentTemperature = readTemperature()
		for report in reports:
			if (currentHour > report,time and report.reported == False):
				message = createMessageBody(report, currentTemperature, count, dayHighTemp, dayLowTemp)
				sendMessage(message)
				report.reported = (True)


def createMessageBody(report, temp, starts, hightemp, lowtemp):
	message = 	(report.meridian + ' Report \n' +
				'The current temperature is ' + temp + '\n' +
				'The low temp was ' + lowtemp + '\n' +
				'The high temp was ' + hightemp + '\n' +
				'The engine was turned over ' + str(starts) + ' times ')
	return message
		
def destroy():
	ADC.write(0)

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()


