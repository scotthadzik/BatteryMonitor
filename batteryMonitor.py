from functools import singledispatch
import LCD1602
import PCF8591 as ADC
import time
import serial
import datetime
import os
import sys
from twilio.rest import Client
import env as env
from ReportTime import ReportTime
import RPi.GPIO as GPIO
import re
from gpiozero import LED, Button

#Twilio Credentials
auth_token = env.TW_TOKEN
account_sid = env.TW_SID
#numbers = [env.TestSMS_Number,env.PrimarySMS_Number,env.SecondarySMS_Number] #TODO uncomment for production
numbers = [env.TestSMS_Number] #TODO COMMENT FOR PRODUCTION	
client = Client(account_sid, auth_token)

#Temperature Sense
ds18b20 = ''
dayLowTemp = 200 # set the initial temperatures to a higher and lower than normal
dayHighTemp = -50

#Voltage Sense
voltage = 0 #set the initial voltage to zero. voltage is used to report when the motor power is turned on
engineTurnedOver = False # initial state of the engine
engineOnTimeInSeconds = time.time()
engineOffTimeInSeconds = time.time()
engineTimeRunningSeconds = time.time()
engineOnMessage = False

#pushbutton -- Currently not used
signal_status_button = Button(5) # BCM16 physical pin 36
red_led = LED(12)
green_led = LED(13)
blue_led = LED(6)
red_led.on()
green_led.on()
blue_led.on()
pressed = False

#date and time
dateNow = datetime.datetime.now()
currentHour = dateNow.hour
dateNow = datetime.datetime.now()
currentHour = dateNow.hour
beginningOfTheDay = True

reports = [
ReportTime(6,' 6:00 a.m. '),
ReportTime(18,' 6:00 p.m. ')
]

def setup():
	global beginningOfTheDay
	ADC.setup(0x48)
	global ds18b20

	for i in os.listdir('/sys/bus/w1/devices'):
		if i != 'w1_bus_master1':
			ds18b20 = i
	# LCD1602.init(0x27, 1)	# init(slave address, background light)
	# LCD1602.clear
	# LCD1602.write(0, 0, 'Battery Monitor')
	# sendMessage('The monitor has started') #TODO Remove for production
	print ('The monitor has started')

def networkStatus():
	phone = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=2.0) # Connect with the serial port
	phone.write(str.encode('AT+CSQ\r\n')) #send AT+CSQ message to queary signal quality
	result=phone.read(100).decode() # read the first 100 char from serial data
	reg_ex_result = re.compile(r'\d+,\d+') # setup regex
	numbers = reg_ex_result.findall(result) # search for the first occurance of numbers
	
	if numbers: # check for a valid number return
		first_num= numbers[0].split(',') # split the return list based on coma
		signal_value = int(first_num[0]) # convert the first set of numbers to integer
	else:
		signal_value = 99
		return ('offline')
	if signal_value == 99:
		reportSignal("offline")
		return ('offline')
	elif signal_value < 10:	# evaluate quality of the signal
		reportSignal("marginal")
		return ('marginal')
	else: 
		reportSignal("good")
		return('good')
	
def reportSignal(signal):
	# for i in os.listdir('/sys/bus/w1/devices'):
	# 	if i != 'w1_bus_master1':
	# 		ds18b20 = i
	# LCD1602.init(0x27, 1)	# init(slave address, background light)
	# LCD1602.clear
	if signal == "offline":
		print('offline')
		red_led.off()
		green_led.on()
		blue_led.on()
	if signal == "marginal":
		print('marginal')
		red_led.off()
		green_led.off()
		blue_led.on()
	if signal == "good":
		print('good')
		red_led.on()
		green_led.off()
		blue_led.on()

def readTemperature():
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
	temperature = (temperature* 1.8) + 32 - 6
	if (temperature < dayLowTemp):
		dayLowTemp = temperature
	if (temperature > dayHighTemp):
		dayHighTemp = temperature
	return temperature

def countIfOn():
	global engineTurnedOver
	global engineOnMessage
	
	readAIN0 = ADC.read(0)

	voltage = readAIN0 # More accurate near 12 V

	if voltage > 50 and engineTurnedOver == False: #Voltage is on engine hasn't started yet
		readTemperature() #check the temperature
		engineTurnedOver = True
		sendMessage(createEngineMessage ("ON"))	
	if voltage < 50 and engineTurnedOver == True: # The engine turned off
		readTemperature() #check the temperature
		engineTurnedOver = False
		sendMessage(createEngineMessage ("OFF"))

		
def createEngineMessage(status):
	tempString = createTempString() # Get the current temp string
	engineTimeOfDay = datetime.datetime.now()
	engineTimeOfDayString = ('\nEngine ' + status + ' at ' + engineTimeOfDay.strftime("%I:%M:%S %p") + '\n')
	engineRunMessage = (engineTimeOfDayString + tempString)
	print (engineRunMessage)
	return engineRunMessage
		


def sendMessage(messageBody):
	for number in numbers:
		message = client.messages \
                .create(
                     body=messageBody,
                     from_=env.PI_Number,
                     to=number
                 )
	print(message.sid)

def loop():
	global dayHighTemp
	global dayLowTemp
	global currentHour
	global beginningOfTheDay
	global pressed
	while True:
		countIfOn() # check if engine has turned on
		dateNow = datetime.datetime.now() #determine the current data and time
		currentHour = dateNow.hour #Get the hour to determine need for report
		for report in reports:		
			if (currentHour >= report.time and report.reported == False): #If it's the hour to report and it has not been reported yet
				report.reported = True
				currentTemperature = readTemperature() #check the temperature
				message = createMessageBody(report, currentTemperature, dayHighTemp, dayLowTemp)
				# sendMessage(message) #TODO uncomment for production
				print (message)
				
		if (currentHour == 0 and beginningOfTheDay == True):
			beginningOfTheDay = False
			startNewDay(reports)
		if (currentHour == 1):
			beginningOfTheDay = True
		
		signal_status_button.when_pressed = networkStatus
		
		# if GPIO.input(signal_status_button):
		# 	if not pressed:
		# 		print ("Button Pressed")
		# 		pressed = True
		# 		print(networkStatus())
		# 	else:
		# 		pressed = False
		# 	time.sleep(2)	


def createMessageBody(report, temp, hightemp, lowtemp):
	tempString = createTempString() # Get the current temp string
	message = 	(report.meridian + ' Report ' + '\n' + tempString)
	return message

def formatTemperature(temp):
	return "{:.2f} F".format(temp)

def createTempString():
	temp = readTemperature()
	formTemp = formatTemperature(temp)
	formHiTemp = formatTemperature(dayHighTemp)
	formLowTemp = formatTemperature(dayLowTemp)
	currentTempString = 'Current Temp ' + formTemp + '\n'
	lowTempString = 'Low Temp ' + str(formLowTemp) + '\n'
	highTempString = 'High Temp ' + formHiTemp + '\n'
	tempString = (currentTempString + lowTempString + highTempString)
	return (tempString)

def startNewDay(reports):
	global dayLowTemp
	global dayHighTemp
	for report in reports:
		report.reported = False
		dayLowTemp = 200
		dayHighTemp = -50
		print ('The current Hour is : ' + str(currentHour))
		print (str(report.meridian) + ' report ' + 'is ' + str(report.reported))	

def destroy():
	ADC.write(0)

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()


