export LC_ALL=C.UTF-8
export LANG=C.UTF-8

cd /home/tajs/sw/chargeCtrl
python3 main.py  2>>/home/tajs/sw/chargeCtrl/dbg.log &
