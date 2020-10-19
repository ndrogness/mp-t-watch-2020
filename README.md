# mp-t-watch-2020
Micropython on the LilyGo T-Watch-2020.
Firmware implementation based on the micropython lvgl implementation available at 
https://github.com/OPHoperHPO/lilygo-ttgo-twatch-2020-micropython

# Load firmware
```
shell# git clone https://github.com/ndrogness/mp-t-watch-2020.git
shell# cd mp-t-watch-2020
shell# esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
shell# esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 firmware.bin
```
# Setup watch face
Create config.json in which you setup your wifi settings
```
shell# cp example-config.json config.json
```

