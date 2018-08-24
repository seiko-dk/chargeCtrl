# chargeCtrl
Python module to control my EV charger

Requires EasyModbus pyserial

Be sure to use python3

Install with
sudo pip3 install EasyModbus
sudo pip3 install pyserial

uninstall serial as it clashes with pyserial
sudo pip3 uninstall serial


Unfortunately lots of paths have to be absolute, so change to install location of main.py

install these crontabs to have the controller start automaticly, and restart if an error occurs.
And to fetch updated CO2 data from energinet.dk

0 */1 * * * /home/tajs/sw/chargeCtrl/co2forecast.sh
*/15 * * * *  /home/tajs/sw/chargeCtrl/go.sh

