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
pushButton = 36 # BCM16 physical pin 36

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


# color for network status
red = 0xFF000
green = 0x0FF00
yellow = 0xFFFF00

R_pin = 32
G_pin = 33
B_pin = 31




def setup(R_pin,G_pin,B_pin):
	global beginningOfTheDay
	ADC.setup(0x48)
	global ds18b20
	
	global pins
	global p_R, p_G, p_B
	pins = {'pin_R': R_pin, 'pin_G': G_pin, 'pin_B': B_pin}
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	for i in pins:
		GPIO.setup(pins[i], GPIO.OUT)   # Set pins' mode is output
		GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off led
	
	p_R = GPIO.PWM(pins['pin_R'], 2000)  # set Frequece to 2KHz
	p_G = GPIO.PWM(pins['pin_G'], 1999)
	p_B = GPIO.PWM(pins['pin_B'], 5000)
	
	p_R.start(0)      # Initial duty Cycle = Turn red on until network detected
	p_G.start(100)
	p_B.start(100)
	networkStatus()
	
	for i in os.listdir('/sys/bus/w1/devices'):
		if i != 'w1_bus_master1':
			ds18b20 = i
	LCD1602.init(0x27, 1)	# init(slave address, background light)
	LCD1602.clear
	LCD1602.write(0, 0, 'Battery Monitor')
	# sendMessage('The monitor has started') #TODO Remove for production
	print ('The monitor has started')

	

def networkStatus():
	phone = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=1.0)

	phone.write(str.encode('AT+CSQ\r\n'))
	result=phone.readline()
	first_num = re.findall("[0-9]", result)
	print (result)
	

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
		setup(R_pin, G_pin, B_pin)
		loop()
	except KeyboardInterrupt:
		destroy()


