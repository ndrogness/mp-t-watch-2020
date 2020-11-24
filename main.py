import json
import binascii
import time
import lvgl as lv
import ttgo
from axp_constants import *
import lv_watchface
from machine import Pin
import styles
import bma423_mp as bma423
import uerrno
import espidf
import wave
import uctypes
import sys

NETOK = False


def lv_event_callback(self, lv_obj, event):
    '''
    if event == lv.EVENT.VALUE_CHANGED:
    if event == lv.EVENT.REFRESH:
    if event == lv.EVENT.LEAVE:
    if event == lv.EVENT.INSERT:
    if event == lv.EVENT.APPLY:
    if event == lv.EVENT.CANCEL:
    if event == lv.EVENT.FOCUSED:
    if event == lv.EVENT.DEFOCUSED:
    '''

    point = lv.point_t()
    event_text = ''
    if event == lv.EVENT.CLICKED:
        event_text = 'clicked'
    if event == lv.EVENT.DRAG_BEGIN:
        event_text = 'drag begin'
    if event == lv.EVENT.DRAG_END:
        event_text = 'drag end'
    if event == lv.EVENT.DRAG_THROW_BEGIN:
        event_text = 'drag throw begin'
    if event == lv.EVENT.GESTURE:
        event_text = 'gesture'
    if event == lv.EVENT.KEY:
        event_text = 'key'
    if event == lv.EVENT.LONG_PRESSED:
        event_text = 'long pressed'
    if event == lv.EVENT.LONG_PRESSED_REPEAT:
        event_text = 'long pressed repeat'
    if event == lv.EVENT.PRESSED:
        event_text = 'pressed'
    if event == lv.EVENT.PRESSING:
        event_text = 'pressing'
    if event == lv.EVENT.PRESS_LOST:
        event_text = 'press lost'
    if event == lv.EVENT.RELEASED:
        event_text = 'released'
    if event == lv.EVENT.SHORT_CLICKED:
        event_text = 'short clicked'

    ptr = lv.indev_get_act()
    ptr.get_point(point)
    print(lv_obj, event_text, point)


class MyWatch(ttgo.Watch):

    def __init__(self, watch_cfg):
        super().__init__()
        self.cfg = watch_cfg
        self.wifi_int = None
        self.time = time.time() + (self.cfg['time']['UTC_offset']*3600)
        (self.year, self.month, self.mday, self.hour, self.minute, self.second, self.weekday,
         self.yearday) = time.localtime(self.time)
        self.is_awake = True
        self.defaults_wifi = {
            'connected': 0,
            'rssi': 0,
            'auth_mode': 'unknown',
            'mac': 'XX:XX:XX:XX:XX:XX',
            'SSID': 'NAN',
            'ip': '0.0.0.0',
            'netmask': '0.0.0.0',
            'dns1': '0.0.0.0',
            'dns2': '0.0.0.0',
            'gps_lat': 00.000000,
            'gps_lon': 00.000000,
            'last_update': None

        }
        self.status = {
            'digital_clock': {
                'local_time': self.time,
                'last_update': None

            },
            'power': {
                'usb_connected': False,
                'usb_volts': 0,
                'usb_power': 0,
                'battery_charging': False,
                'battery_volts': 0,
                'battery_perc': 0,
                'last_update': None
            },

            'debug': {
                'log': [],
                'last_update': None
            },

            'step_counter': {
                'current_count': 0,
                'last_update': None
            },

            'wifi': {},
            'weather': {}
        }
        self.status['wifi'].update(self.defaults_wifi)

    @property
    def step_counter(self):
        return self.__step_counter

    @step_counter.setter
    def step_counter(self, count):
        self.__step_counter = count
        self.status['step_counter']['current_count'] = count

    @property
    def get_time(self):
        return self.time

    @property
    def is_connected(self):
        if self.cfg['wifi']['enabled'] != 'yes':
            return False

        if self.wifi_int is None:
            return False

        return self.wifi_int.isconnected()

    def notify(self):
        self.motor.on()
        time.sleep(.5)
        self.motor.off()

    def disconnect(self):

        if self.cfg['wifi']['enabled'] != 'yes':
            return False

        if self.is_connected is False:
            return True

        wifi_disconnect()
        self.status['wifi'] = {}
        self.status['wifi'].update(self.defaults_wifi)

    def connect(self):
        _did_connect = False

        if self.cfg['wifi']['enabled'] != 'yes':
            return False

        if self.is_connected is True:
            return True

        self.status['wifi']['SSID'] = 'Connect...'
        watchface.update(self.status)

        for wifi_net in self.cfg['wifi']['networks']:
            # print(wifi_net)
            _did_connect = wifi_connect(ssid=wifi_net['ssid'], password=wifi_net['password'],
                                        timeout=self.cfg['wifi']['connect_timeout'])
            if _did_connect is True:
                # self.status['wifi']['auth_mode'] = self.wifi_int.config('auth_mode')
                self.status['wifi']['connected'] = 1
                self.status['wifi']['SSID'] = wifi_net['ssid']
                self.status['wifi']['mac'] = binascii.hexlify(self.wifi_int.config('mac'), ':').decode()
                self.status['wifi']['ip'] = self.wifi_int.ifconfig()[0]
                self.status['wifi']['netmask'] = self.wifi_int.ifconfig()[1]
                self.status['wifi']['dns1'] = self.wifi_int.ifconfig()[2]
                self.status['wifi']['dns2'] = self.wifi_int.ifconfig()[3]
                self.status['wifi']['gps_lat'] = wifi_net['gps_lat']
                self.status['wifi']['gps_lon'] = wifi_net['gps_lon']

                return True

        if _did_connect is False:
            self.status['wifi']['connected'] = 0
            self.status['wifi']['SSID'] = 'NAN'
            self.status['wifi']['mac'] = 'XX:XX:XX:XX:XX:XX'
            self.status['wifi']['ip'] = '0.0.0.0'
            self.status['wifi']['netmask'] = '0.0.0.0'
            self.status['wifi']['dns1'] = '0.0.0.0'
            self.status['wifi']['dns2'] = '0.0.0.0'

        return _did_connect

    def _update_time(self):
        # Update time
        self.time = time.time() + (self.cfg['time']['UTC_offset']*3600)
        (self.year, self.month, self.mday, self.hour, self.minute, self.second, self.weekday,
         self.yearday) = time.localtime(self.time)
        self.status['digital_clock']['local_time'] = self.time

    def debug_it(self, log, console=True):
        self.status['debug']['log'].append(log)
        if console is True:
            print(log)

    def _update_power(self):

        # self.debug_it('Usb: {}mV {}ma'.format(self.pmu.getVbusVoltage(), self.pmu.getVbusCurrent()))
        # self.debug_it('Char: charcur:{}ma discur:{}ma'.format(self.pmu.getBattChargeCurrent(), self.pmu.getBattDischargeCurrent()))
        # self.debug_it('bat:{}% {}mV Inpower:{}'.format(self.pmu.getBattPercentage()*100, self.pmu.getBattVoltage(), self.pmu.getBattInpower()))
        # self.debug_it('temp: {} tstemp: {}'.format(self.pmu.getTemp(), self.pmu.getTSTemp()))
        # self.debug_it('ischarging: {} vbusplug: {}'.format(self.pmu.isChargeing(), self.pmu.isVBUSPlug()))

        self.status['power']['usb_connected'] = self.pmu.isVBUSPlug()
        self.status['power']['usb_volts'] = self.pmu.getVbusVoltage()
        self.status['power']['usb_power'] = self.pmu.getVbusCurrent()
        self.status['power']['battery_charging'] = self.pmu.isChargeing()
        self.status['power']['battery_volts'] = self.pmu.getBattVoltage()
        # self.status['power']['battery_perc'] = self.pmu.getBattPercentage()

        # Lower end cutoff 3260mV, full charge 4100mV
        _batt_perc = int(self.pmu.getBattVoltage()) - 3260
        if _batt_perc < 0:
            _batt_perc = 0
        _batt_perc = int((_batt_perc / 840) * 100)
        if _batt_perc > 100:
            _batt_perc = 100
        self.status['power']['battery_perc'] = _batt_perc

    def update_always(self):
        self.status['debug']['log'].clear()
        self._update_time()
        self._update_power()
        # watchface.update(self.status)

    def update_routine(self):

        # Update time
        if sync_time_ntp() is True:
            self.update_always()
            # Update RTC clock
            # Range: seconds [0,59], minutes [0,59], hours [0,23],
            #    day [1,7], date [1-31], month [1-12], year [0-99].
            # watch.rtc.write_all(seconds=None, minutes=None, hours=None, day=None, date=None, month=None, year=None)
            self.rtc.write_all(
                seconds=watch.second,
                minutes=watch.minute,
                hours=watch.hour,
                day=watch.weekday + 1,
                date=watch.mday,
                month=watch.month,
                year=watch.year - 2000
            )
        else:
            self.update_always()

        if get_weather() is True:
            print('Got Weather')

    def wakeup(self):
        if self.is_awake is True:
            return
        else:
            self.update_always()
            self.tft.backlight(1)
            self.tft.display_wakeup()
            self.is_awake = True

    def sleep(self):
        if self.is_awake is False:
            return
        else:
            self.disconnect()
            self.tft.backlight(0)
            self.tft.display_sleep()
            self.is_awake = False


def load_cfg(cfg_file='/config.json'):
    '''
    Load config file
    :param cfg_file:
    :return: cfg dictionary
    '''
    cfg = {
        "watchface_dir": "/watchfaces",
        "display": {
            "inactivity_sleep_timer": 0,
            "brightness_perc_usb": 50,
            "brightness_perc_bat": 30
        },
        "wifi": {
            "enabled": "no"
        },
        "time": {
            "UTC_offset": -7
        },
        "updates": {
            "routine": 1800
        }
    }

    try:
        with open(cfg_file) as cf:
            cfg_json = json.load(cf)
            cfg.update(cfg_json)
    except OSError:
        print('Warning: Missing or error reading config.json file, using defaults')

    return cfg


def wifi_disconnect():

    if watch.cfg['wifi']['enabled'] != 'yes':
        return False

    if watch.wifi_int is None:
        watch.wifi_int = network.WLAN(network.STA_IF)

    if watch.wifi_int.isconnected() is True:
        watch.wifi_int.disconnect()

    if watch.wifi_int.active() is True:
        watch.wifi_int.active(False)

    if watch.wifi_int is not None:
        del watch.wifi_int

    watch.wifi_int = None


def wifi_connect(ssid, password, timeout=10):

    if watch.cfg['wifi']['enabled'] != 'yes':
        return False

    if watch.wifi_int is None:
        watch.wifi_int = network.WLAN(network.STA_IF)

    if watch.wifi_int.active() is not True:
        watch.wifi_int.active(True)
        #sta_if.active(True)

    # print("\n=== Connect to access point (30 sec timeout) ========\n")
    #sta_if.connect(watch.cfg['wifi']['ssid'], watch.cfg['wifi']['password'])
    watch.wifi_int.connect(ssid, password)

    # Wait until connected and show IF config
    tmo = timeout
    # while not sta_if.isconnected():
    while not watch.wifi_int.isconnected():
        time.sleep(1)
        tmo -= 1
        if tmo == 0:
            print("Failed to connect to AP within Timeout")
            return False

    print("\n=== STA Connected ==================\n", watch.wifi_int.ifconfig())
    return True


def init():
    #watch.pmu.adc1Enable(AXP202_VBUS_VOL_ADC1 | AXP202_VBUS_CUR_ADC1 | AXP202_BATT_CUR_ADC1 | AXP202_BATT_VOL_ADC1, True)
    watch.pmu.enablePower(AXP202_LDO2)
    watch.pmu.setLDO2Voltage(3300)
    watch.pmu.enableADC(AXP202_ADC1, AXP202_BATT_VOL_ADC1)
    watch.pmu.enableADC(AXP202_ADC1, AXP202_BATT_CUR_ADC1)
    watch.pmu.enableADC(AXP202_ADC1, AXP202_VBUS_VOL_ADC1)
    watch.pmu.enableADC(AXP202_ADC1, AXP202_VBUS_CUR_ADC1)
    watch.lvgl_begin()


def bma_handle_interrupt(pin):
    state = watch.bma.read_irq()
    if state == watch.bma.IRQ_STEP_COUNTER:
        s = watch.bma.stepcount()
        print('IRQ_STEP_COUNTER: {}, state: {}'.format(s, state))
        watch.status['step_counter']['current_count'] += 1
    elif state == watch.bma.IRQ_DOUBLE_WAKEUP:
        watch.wakeup()
        print('IRQ_DOUBLE_WAKEUP', state)
    else:
        print('Undefined BMA Interrupt:', state)


def rtc_handle_interrupt(pin):
    if watch.rtc.check_for_alarm_interrupt():
        print('is alarm clock interrupt')
    else:
        print('is not for alarm interrupt')
    watch.rtc.clear_alarm()


def get_weather():

    if watch.cfg['wifi']['enabled'] != 'yes':
        return False

    if watch.is_connected is False:
        watch.connect()

    if watch.is_connected is False or watch.status['wifi']['SSID'] == 'NAN':
        return False

    # Register for https://www.openweathermap.org
    # One call API
    #url = 'https://api.openweathermap.org/data/2.5/onecall?'
    url = '{}'.format(watch.cfg['weather']['base_url'])
    url += 'lat={:f}&lon={:f}'.format(watch.status['wifi']['gps_lat'], watch.status['wifi']['gps_lon'])
    url += '&exclude=hourly,daily,minutely'
    url += '&units={}'.format(watch.cfg['weather']['units'])
    url += '&appid={}'.format(watch.cfg['weather']['api_key'])
    print('Getting Weather:', url)
    resp = urequests.get(url)  # Send the request
    _cur_weather = resp.json()
    watch.status['weather'].update(_cur_weather['current'])
    print(watch.status['weather'])
    return True


def sync_time_ntp():

    if watch.cfg['wifi']['enabled'] != 'yes':
        return

    if watch.is_connected is False:
        watch.connect()

    # Update time from ntp server
    if watch.is_connected:
        try:
            ntptime.settime()
        except Exception as e:
            return False
    else:
        return False

    return True


def play_audio(file="one.wav"):

    i2s_pin_cfg = espidf.i2s_pin_config_t()
    i2s_pin_cfg.bck_io_num = 26
    # Not using input
    i2s_pin_cfg.data_in_num = espidf.I2S_PIN_NO.CHANGE
    i2s_pin_cfg.data_out_num = 33
    i2s_pin_cfg.ws_io_num = 25

    # Enable power to Max98357A I2S chip
    watch.enable_audio_power(True)

    i2s_cfg = espidf.i2s_config_t()

    # Set mode or'd espidf.I2S_MODE.[DC_BUILT_IN|DAC_BUILT_IN|MASTER|PDM|RX|SLAVE|TX
    # Only TX
    i2s_cfg.mode = espidf.I2S_MODE.MASTER | espidf.I2S_MODE.TX

    # 32bits per sample (espidf.I2S_BITS_PER_SAMPLE._[8BIT|16BIT|24BIT|32BIT]
    i2s_cfg.bits_per_sample = espidf.I2S_BITS_PER_SAMPLE._16BIT

    # Num channels espidf.I2S_CHANNEL_FMT.[ALL_LEFT|ALL_RIGHT|ONLY_LEFT|ONLY_RIGHT|RIGHT_LEFT]
    #
    i2s_cfg.channel_format = espidf.I2S_CHANNEL_FMT.RIGHT_LEFT

    # Or'd espidf.I2S_COMM_FORMAT.[I2S|I2S_LSB|I2S_MSB|PCM|PCM_LONG|PCM_SHORT]
    i2s_cfg.communication_format = espidf.I2S_COMM_FORMAT.I2S | espidf.I2S_COMM_FORMAT.I2S_MSB

    # for 36Khz sample rates, we create 100Hz sine wave, every cycle need 36000/100 = 360 samples (4-bytes or 8-bytes each sample)
    # depend on bits_per_sample
    # using 6 buffers, we need 60-samples per buffer
    # if 2-channels, 16-bit each channel, total buffer is 360*4 = 1440 bytes
    # if 2-channels, 24/32-bit each channel, total buffer is 360*8 = 2880 bytes
    i2s_cfg.sample_rate = 16000
    # Number of buffers
    i2s_cfg.dma_buf_count = 16

    # 8 samples per buffer (minimum)
    i2s_cfg.dma_buf_len = 64
    i2s_cfg.fixed_mclk = 0
    i2s_cfg.use_apll = 0

    # Interrupt Level in C file was ESP_INTR_FLAG_LEVEL1 defned as (1<<1) = 2
    i2s_cfg.intr_alloc_flags = 2

    # ? Not used?
    i2s_cfg.tx_desc_auto_clear = 0

    i2s_drv = espidf.i2s_driver_install(0, i2s_cfg, 0, None)
    # print(dir(i2s_drv))
    espidf.i2s_set_pin(0, i2s_pin_cfg)

    # esp_err_t i2s_set_clk(i2s_num, rate, i2s_bits_per_sample_tbits, i2s_channel_t ch)
    # i2s_num: I2S_NUM_0, I2S_NUM_1
    # rate: I2S sample rate (ex: 8000, 44100…)
    # bits: I2S bit width (I2S_BITS_PER_SAMPLE_16BIT, I2S_BITS_PER_SAMPLE_24BIT, I2S_BITS_PER_SAMPLE_32BIT)
    # ch: I2S channel, (I2S_CHANNEL_MONO, I2S_CHANNEL_STEREO)
    #
    espidf.i2s_set_clk(0, 16000, 16, espidf.I2S_CHANNEL.MONO)

    #The bit clock rate is determined by the sample rate and i2s_config_t configuration
    # parameters (number of channels, bits_per_sample).
    # bit_clock = rate * (number of channels) * bits_per_sample
    #espidf.i2s_set_sample_rates(0, 1)

    f = wave.open('test.wav', 'r')
    total_frames = f.getnframes()
    framerate = f.getframerate()

    bytes_out = bytearray(4)
    bsizeof = total_frames * f.getnchannels() * f.getsampwidth()
    print('Wave info:', f.getparams())

    # All at once write...in memory be careful
    # all_frames = f.readframes(total_frames)
    # ret = espidf.i2s_write(0, all_frames, bsizeof, bytes_out, espidf.portMAX.DELAY)
    # print(espidf.esp_err_to_name(ret))

    bsizeof = framerate * f.getnchannels() * f.getsampwidth()
    for position in range(0, total_frames, framerate):
        f.setpos(position)
        frame_data = f.readframes(framerate)
        print('Frame data:', len(frame_data), bsizeof)
        ret = espidf.i2s_write(0, frame_data, len(frame_data), bytes_out, espidf.portMAX.DELAY)
        print(espidf.esp_err_to_name(ret))

    '''
    bsizeof = framerate * f.getnchannels() * f.getsampwidth()
    ba = bytearray(2)
    for position in range(0, total_frames):
        f.setpos(position)
        frame = f.readframes(1)
        #frame_out = frame_out[0] << 8 | frame_out[1]
        #frame_out = frame_out >> 1
        #ba[0] = (frame_out & 0xff00) >> 8
        #ba[1] = frame_out & 0xff
        x = int.from_bytes(frame, sys.byteorder) >> 1
        frame_out = x.to_bytes(2, 'big')
        ret = espidf.i2s_write(0, frame_out, len(frame_out), bytes_out, espidf.portMAX.DELAY)
    '''

    espidf.i2s_stop(0)


def routine_sync():
    pass

irq = Pin(39, mode=Pin.IN)
irq.irq(handler=bma_handle_interrupt, trigger=Pin.IRQ_RISING)

# Grab config
#cfg = load_cfg()

# Initialize watch
# watch = ttgo.Watch()
watch = MyWatch(watch_cfg=load_cfg())
# watch.power_off()
# watch.init_power()
# watch.enable_audio_power(en=True)
tft = watch.tft
# watch.tft.display_off()
# watch.tft.display_sleep()
# watch.tft.display_wakeup()
# watch.tft.switch_scene()
power = watch.pmu
init()


# Attach a handler for the accel
# watch.bma_attach_interrupt(bma_handle_interrupt)

# Attach a handler for the Reat Time Clock
watch.rtc_attach_interrupt(rtc_handle_interrupt)

# Attach a handler for the PMU
# watch.pmu_attach_interrupt(pmu_handle_interrupt)

# Grab a lv screen
home_screen = lv.obj()
settings_screen = lv.obj()
settings_label = lv.label(settings_screen)
settings_label.set_text("Settings")
# Turn on backlight
# watch.tft.backlight_fade(100)
watch.tft.backlight_fade(30)

tiles_coords = [{"x":0, "y":0}, {"x":0,"y":1}]
tileview = lv.tileview(settings_screen)
tileview.set_valid_positions(tiles_coords, 2)
tileview.set_edge_flash(True)

tile_home = lv.obj(tileview)
tile_home.set_size(240, 240)
tileview.add_element(tile_home)

tile2 = lv.obj(tileview)
tile2.set_size(240, 240)
tileview.add_element(tile2)
dlabel = lv.label(tile2)
dlabel.set_text("Scroll Down")

# Load WatchFace
watchface = lv_watchface.WatchFace(watch=watch, screen=home_screen, config_file='/watchfaces/rr053.json')
watchface.load()

# Load the screen
lv.scr_load(home_screen)

watch.notify()
#print(watch.status)

update_counter = 0

if watch.cfg['wifi']['enabled'] == 'yes':
    import network
    import ntptime
    import urequests
    # watch.connect()

tick_time = .5
sleep_after = int(int(watch.cfg['display']['inactivity_sleep_timer']) / tick_time)
accel_last = [1, 1, 1]
motion_detect = False

# watch.bma.map_int(0, bma423.BMA423_TILT_INT | bma423.BMA423_WAKEUP_INT | bma423.BMA423_ANY_NO_MOTION_INT |
#                   bma423.BMA423_ACTIVITY_INT | bma423.BMA423_STEP_CNTR_INT)

'''
#bma423_py
watch.bma.accel_range = 2
watch.bma.feature_enable('step_cntr')
# watch.bma.feature_enable('tilt')
watch.bma.accel_enable = 1
watch.bma.step_dedect_enabled = 1
watch.bma.step_watermark=1
'''
'''
# bma42x module
watch.bma.set_accel_enable(True)
accel_conf = {}
accel_conf['odr'] = bma42x.OUTPUT_DATA_RATE_100HZ
# Gravity range of the sensor (+/- 2G, 4G, 8G, 16G)
accel_conf['range'] = bma42x.ACCEL_RANGE_2G
accel_conf['bandwidth'] = bma42x.ACCEL_NORMAL_AVG4
accel_conf['perf_mode'] = bma42x.CIC_AVG_MODE
watch.bma.set_accel_config(**accel_conf)

# Enable step counter
watch.bma.feature_enable(bma42x.STEP_CNTR, True)
# Map the interrupt pin with that of step counter interrupts
# Interrupt will  be generated when step activity is generated.
watch.bma.map_interrupt(bma42x.INTR1_MAP, bma42x.STEP_CNTR_INT, True)

# Set water-mark level 1 to get interrupt after 20 steps.
# Range of step counter interrupt is 0 to 20460(resolution of 20 steps).
watch.bma.step_counter_set_watermark(1)
'''

# play_audio(file="bob.wav")

try:

    while True:
        time.sleep(.5)

        # Doesn't work...use lv event
        # print(watch.touch.read())

        #temp = watch.bma.temperature()

        # Sleep is enabled, check for motion
        if sleep_after > 0:
            accel = watch.bma.accel()

            if (accel[1] > 0 and accel_last[1] < 0) or (accel[1] < 0 and accel_last[1] > 0):
                motion_detect = True
            elif accel_last[1] != 0 and (accel[1] / accel_last[1]) > 4:
                motion_detect = True
            else:
                motion_detect = False

            print("Accel:", accel, "Motion Detect:", motion_detect)
            if watch.is_awake is True:
                if update_counter > 1 and update_counter % sleep_after == 0 and motion_detect is False:
                    watch.sleep()
            elif motion_detect is True:
                print("Wakeup!")
                watch.wakeup()
            else:
                print("Sleeping...", sleep_after)

            accel_last = accel

        #datetime returns tuple(year, month, date, day, hours, minutes,seconds)
        if update_counter % int(watch.cfg['updates']['routine'] * 2) == 0:
            watch.update_routine()
            print(watch.rtc.datetime())
        # elif update_counter == 30:
        #     lv.scr_load(settings_screen)
        # elif update_counter == 240:
        #     lv.scr_load(home_screen)
        else:
            watch.update_always()

        update_counter += 1

except OSError as exc:
    print("Exception Caught:", uerrno.errorcode[exc.args[0]])

except KeyboardInterrupt as exc:
    print("Clean exit")

finally:
    print('Power down...')
    #watch.power_off()

