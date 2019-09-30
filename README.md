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


#SIM setup
sudo route add default eth1    #This will make all network traffic going through lte device

#Network IP Check
- ifconfig eth1
	- Should return an inet 10.x.x.x If the first and second x return 0 sim is not connected to network
- ping -I eth1 8.8.8.8
	- Check for connection to network. Packets sent and returned means good connection.

# troubleshoot sim
minicom –b 115200 –D /dev/ttyACM0

- AT+CSQ
	- signal quality measured by the modem RSSI and BER
- AT+CPIN? 
	- returns ready if modem can read the sim card
- AT+CREG? 
	- returns if registered and connected to network
	- second character 
		- 1 -> registered on network
		- 5 -> registered but roaming

M2M Codes
https://m2msupport.net/m2msupport/atcreg-network-registration/


SMS Setup
https://iotguider.in/raspberrypi/send-sms-from-raspberry-pi-python/

##FRDM-K64F
https://os.mbed.com/platforms/FRDM-K64F/#technical-doc


##Run pi program on startup https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup/all

##sms bot with NGrok https://makezine.com/projects/sms-bot/

## remote temp monitor https://hackmypi.com/RemoteTemperatureMonitoring.php
