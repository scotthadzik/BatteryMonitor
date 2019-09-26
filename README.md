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

Tutorial for connecting avnet M14A2A board to rasp pi 3
http://cloudconnectkits.org/sites/default/files/GettingStartedGuide_Pi3_LTE_rv1-3_0_0.pdf

M2M Codes
https://m2msupport.net/m2msupport/atcreg-network-registration/


SMS Setup
https://iotguider.in/raspberrypi/send-sms-from-raspberry-pi-python/

##FRDM-K64F
https://os.mbed.com/platforms/FRDM-K64F/#technical-doc


##Run pi program on startup https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup/all

##sms bot with NGrok https://makezine.com/projects/sms-bot/

## remote temp monitor https://hackmypi.com/RemoteTemperatureMonitoring.php
