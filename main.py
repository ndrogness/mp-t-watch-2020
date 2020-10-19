import json
import time
import lvgl as lv
import ttgo
from axp_constants import *
import lv_watchface
import styles


def load_cfg(cfg_file='/config.json'):
    '''
    Load config file
    :param cfg_file:
    :return: cfg dictionary
    '''
    default_cfg = {
        'WIFI': {
            'USE_WIFI': 'NO',
        },
        'WATCHFACE_DIR': '/watchfaces'

    }
    with open(cfg_file) as cf:
        cfg_json = json.load(cf)

    return cfg_json


def init():
    # power.adc1Enable(AXP202_VBUS_VOL_ADC1
    #                  | AXP202_VBUS_CUR_ADC1 |
    #                  AXP202_BATT_CUR_ADC1 | AXP202_BATT_VOL_ADC1, True)
    watch.lvgl_begin()


# Grab config
cfg = load_cfg()
print(cfg['WIFI']['WIFI_SSID'])

# Initialize watch
watch = ttgo.Watch()
tft = watch.tft
power = watch.pmu
init()

# Grab a lv screen
scr = lv.obj()

# Turn on backlight
# watch.tft.backlight_fade(100)
watch.tft.backlight_fade(50)

# Load WatchFace
watchface = lv_watchface.WatchFace(screen=scr)
watchface.load()

# Load the screen
lv.scr_load(scr)

while True:
    time.sleep(1)
    watchface.update()

