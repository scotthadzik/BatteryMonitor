import LCD1602
import PCF8591 as ADC
import time
import datetime
import os
import sys
from twilio.rest import Client
import env as env
from ReportTime import ReportTime
import RPi.GPIO as GPIO

#Twilio Credentials
auth_token = env.TW_TOKEN
account_sid = env.TW_SID
#numbers = [env.TestSMS_Number,env.PrimarySMS_Number,env.SecondarySMS_Number]
numbers = [env.TestSMS_Number]

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
engineTurnedOver = False # state of the pump
engineOnTimeInSeconds = time.time()
engineOffTimeInSeconds = time.time()
engineTimeRunningSeconds = time.time()

dateNow = datetime.datetime.now()
currentHour = dateNow.hour
testhour = 8 #TODO this is for testing time
beginningOfTheDay = True

reports = [
ReportTime(6,' 6:00 a.m. '),
ReportTime(18,' 6:00 p.m. '),
]

index = 0 # report time index tracking


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
	LCD1602.write(0, 0, 'Battery Monitor')
	reportTemperature()
	# sendMessage('The monitor has started') TODO remove comment

def button_callback(channel):
    print("Button was pushed!")
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
	global engineTurnedOver
	global engineOnTimeInSeconds
	global engineOffTimeInSeconds
	global engineTimeRunningSeconds
	readAIN0 = ADC.read(0)
	engineStartTimeOfDay = datetime.datetime.now()

	voltage = readAIN0 # More accurate near 12 V
	if voltage > 50 and engineTurnedOver == False: #Increase the count --> use the motorTurnedOver state to verify that the On time is not counted
		engineOnTimeInSeconds = time.time()
		engineStartTimeOfDay = datetime.datetime.now() # set the time that the engine started
		engineTurnedOver = True
	if voltage < 50 and engineTurnedOver == True: # The motor turned over, but now it is not turning over
		engineTurnedOver = False
		engineOffTimeInSeconds = time.time()
		engineTimeRunningSeconds = (engineOffTimeInSeconds - engineOnTimeInSeconds) / 60
		formattedMotorRunTime = round(engineTimeRunningSeconds,2)
		engineStartTimeOfDayString = ('Engine on at ' + engineStartTimeOfDay.strftime("%c") + '\n')
		motorRunTime = (' Engine ran for ' + str(formattedMotorRunTime) + ' minutes')
		motorRunMessage = (engineStartTimeOfDayString + motorRunTime)
		print (motorRunMessage)
		# sendMessage(motorRunMessage) TODO remove comment
	return count

def sendMessage(messageBody):
	for number in numbers:
		message = client.messages \
                .create(
                     body=messageBody,
                     from_=env.PI_Number,
                     to=number
                 )
	print(message.sid)

def reportTemperature():
	global dayHighTemp
	global dayLowTemp
	currentTemp = readTemperature()
	formatedTemp = "{:.2f} F".format(currentTemp)
	formatedLowTemp = "{:.2f} F".format(dayLowTemp)
	
	LCD1602.write(0, 0, 'Temp = : ' + formatedTemp)
	print ("Current temperature : " + formatedTemp)
	print ("Low temperature today: " + formatedLowTemp)
	return formatedTemp

def loop():
	global startingTime
	global dayHighTemp
	global dayLowTemp
	global index
	global testhour 
	while True:
		countIfOn()
		currentTemperature = readTemperature()
		# print (currentHour)
		for report in reports:
			
			if (currentHour >= report.time and report.reported == False):
				message = createMessageBody(report, currentTemperature, dayHighTemp, dayLowTemp)
				# sendMessage(message) #TODO uncomment for production
				print (message)
				report.reported = True
		
		if currentHour == 0:
			startNewDay(reports)

def createMessageBody(report, temp, hightemp, lowtemp):
	formatedTemp = "{:.2f} F".format(temp)
	formatedLowTemp = "{:.2f} F".format(dayLowTemp)
	formatedHighTemp = "{:.2f} F".format(hightemp)
	# Output to the LCD
	currentTempString = 'The current temperature is ' + formatedTemp + '\n'
	lowTempString = 'The low temp was ' + str(formatedLowTemp) + '\n'
	highTempString = 'The high temp was ' + formatedHighTemp + '\n'

	message = 	(report.meridian + ' Report ' + '\n' + currentTempString + lowTempString + highTempString)

	return message

def startNewDay(reports):
	global dayLowTemp
	global dayHighTemp
	for report in reports:
		report.reported = False
		dayLowTemp = 200
		dayHighTemp = -50	



def destroy():
	ADC.write(0)

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()


