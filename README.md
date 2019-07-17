# Setup Instructions
Runs on Raspian without Desktop

## External Modules
Run this before running program
- sudo apt install python3-pip
- sudo pip3 install guizero
- sudo apt update
- sudo apt upgrade
- modify /boot/config.txt
	- dtoverlay=w1-gpio
- sudo reboot

SMS Setup
https://iotguider.in/raspberrypi/send-sms-from-raspberry-pi-python/

Modify file send_sms.py
import nexmo
client = nexmo.Client(key='YOUR-API-KEY', secret='YOUR-API-SECRET')
client.send_message({'from': 'Nexmo', 'to': 'YOUR-PHONE-NUMBER', 'text': 'Hello world'})
