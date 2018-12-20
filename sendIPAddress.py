import RPi.GPIO as GPIO
import os
import sys

def setup():
    IPAddress = '10.0.0.9'
                    
if _name_ == "_main_":     # Program start from here
        setup()
        try:
            print("sms sent")
			os.system("python send_sms.py") #Using this line in any python program you can send sms. This call the send_sms.py program and runs it.
			break				              		
		
        except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
                destroy()