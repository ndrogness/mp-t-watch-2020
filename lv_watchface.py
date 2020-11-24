import sys
import time
import os
import json
import lvgl as lv
import styles
from imagetools import get_png_info, open_png

def load_png_img(png_filename='/watchfaces/watchface_default.png'):
    '''
    Load the png image
    :param filename:
    :return: lv img_desc
    '''

    # Image descriptor
    img_dsc = lv.img_dsc_t()
    # img_dsc.data_size = len(buff)
    # img_dsc.data = buff
    # img_dsc.header.always_zero = 0
    # img_dsc.header.w = 153
    # img_dsc.header.h = 154
    # img_dsc.header.cf = lv.img.CF.TRUE_COLOR
    # img_dsc.header.cf = lv.img.CF.RAW

    # Image from Lvgl bin builder (doesnt work)
    #with open('widgets/lv_img/wf565.bin', 'rb') as f:
    # with open('widgets/lv_img/wf888.bin', 'rb') as f:
    #     h = lv.img_header_t()
    #     h = f.read(4)
    #     lv.img.decoder_get_info(h, img_dsc.header)
    #     img_dsc.data_size = img_dsc.header.w * img_dsc.header.h * 4
    #     img_dsc.data = f.read()


    # with open('widgets/lv_img/png_decoder_test.png', 'rb') as f:
    with open(png_filename, 'rb') as f:
        buff = f.read()
        img_dsc.data = buff
        img_dsc.data_size = len(buff)

    #print('buff size:', img_dsc.data_size)
    return img_dsc
    # img = lv.img(screen)
    # img.set_src(img_dsc)


class LvWatchFaceContainer(lv.cont):

    def __init__(self, container_cfg=None, parent_cont=None):
        # Load default container config
        self.cont_cfg = styles.default_watchface_container
        if container_cfg is not None:
            if 'name' not in container_cfg:
                print('Must define a container name in config')
                raise ValueError
            self.cont_cfg.update(container_cfg)

        super().__init__(parent_cont)
        self.name = self.cont_cfg['name']
        if 'styles' not in self.cont_cfg:
            print('Using default style settings for container')
        self.styles = self.cont_cfg['styles']
        print(self.styles)
        self.num_objs = 0

        self.size_x = int(self.cont_cfg['x_end']) - int(self.cont_cfg['x_start'])
        self.size_y = int(self.cont_cfg['y_end']) - int(self.cont_cfg['y_start'])
        self.pos_x = int(self.cont_cfg['x_start'])
        self.pos_y = int(self.cont_cfg['y_start'])
        if self.size_x < 1 or self.size_y < 1 or self.pos_x < 0 or self.pos_y < 0:
            print('Invalid container size/coordinate config:', self.name)
            raise ValueError

        self.set_pos(self.pos_x, self.pos_y)
        self.set_size(self.size_x, self.size_y)

        if self.cont_cfg['fit'] in styles.LV_FIT.__dict__:
            self.set_fit(getattr(styles.LV_FIT, self.cont_cfg['fit']))
        else:
            print("Invalid container fit, using lv.FIT.NONE:", self.cont_cfg['fit'])
            self.set_fit(lv.FIT.NONE)

        if self.cont_cfg['layout'] in styles.LV_LAYOUT.__dict__:
            self.set_layout(getattr(styles.LV_LAYOUT, self.cont_cfg['layout']))
        else:
            print("Invalid container layout, using lv.LAYOUT.CENTER:", self.cont_cfg['layout'])
            self.set_layout(lv.LAYOUT.CENTER)
            # self.set_layout(lv.LAYOUT.PRETTY_MID)
            # self.set_layout(lv.LAYOUT.ROW_MID)
            # self.set_layout(lv.LAYOUT.CENTER)

        self.cont_style = lv.style_t()
        self.cont_style.init()
        if 'spacing' in self.styles:
            if 'padding' in self.styles['spacing']:
                self.cont_style.set_pad_all(lv.STATE.DEFAULT, int(self.styles['spacing']['padding']))
            if 'margin' in self.styles['spacing']:
                self.cont_style.set_margin_all(lv.STATE.DEFAULT, int(self.styles['spacing']['margin']))

        if 'transparent' in self.styles:
            if self.styles['transparent'] == 'yes':
                self.cont_style.set_border_opa(lv.STATE.DEFAULT, lv.OPA.TRANSP)
                self.cont_style.set_bg_opa(lv.STATE.DEFAULT, lv.OPA.TRANSP)
            elif self.styles['transparent'] == 'background':
                self.cont_style.set_border_opa(lv.STATE.DEFAULT, lv.OPA.COVER)
                self.cont_style.set_border_color(lv.STATE.DEFAULT, lv.color_hex(0xff0000))
                self.cont_style.set_border_width(lv.STATE.DEFAULT, 1)
                self.cont_style.set_bg_opa(lv.STATE.DEFAULT, lv.OPA.TRANSP)

        self.add_style(self.PART.MAIN, self.cont_style)

        # Used for layout viewing
        self.layout_style = lv.style_t()
        self.layout_style.init()
        self.layout_style.set_border_opa(lv.STATE.DEFAULT, lv.OPA.COVER)
        self.layout_style.set_bg_opa(lv.STATE.DEFAULT, lv.OPA.COVER)
        self.layout_style.set_bg_color(lv.STATE.DEFAULT, styles.LV_COLOR_WHITE)
        self.layout_label = None

    def show_layout(self):
        self.clean()
        self.reset_style_list(self.PART.MAIN)
        self.add_style(self.PART.MAIN, self.layout_style)
        self.layout_label = lv.label(self)
        self.layout_label.set_text(self.name)
        self.layout_label.set_align(lv.label.ALIGN.CENTER)

    def reset_layout(self):
        self.clean()
        self.reset_style_list(self.PART.MAIN)
        self.add_style(self.PART.MAIN, self.cont_style)
        self.layout_label = None


class LvWatchFaceObj:

    def __init__(self, watchface_cfg, parent_cont=None):
        # print('obj cfg:', watchface_cfg)
        # print('globals:', globals())
        self.cfg = watchface_cfg

        if 'name' in self.cfg:
            self.name = self.cfg['name']
        else:
            self.name = 'unnamed'

        if 'src' in watchface_cfg:
            self.src = watchface_cfg['src']
        else:
            self.src = 'not_defined'

        if 'refresh_interval_multiplier' in watchface_cfg:
            self.refresh_interval_multiplier = int(watchface_cfg['refresh_interval_multiplier'])
            if self.refresh_interval_multiplier < 0:
                self.refresh_interval_multiplier = 0
        else:
            self.refresh_interval_multiplier = 0

        self.parent_cont = parent_cont
        self.pos_x = 0
        self.pos_y = 0

        # self.indev = watchface_cfg['indev']
        # self.last_click_pt = watchface_cfg['last_click_pt']
        self.can_update = False

        # Load styles
        self.styles = styles.default_watchface_styles
        if 'styles' in watchface_cfg:
            self.styles.update(watchface_cfg['styles'])

        # Load options
        if 'options' in watchface_cfg:
            self.options = watchface_cfg['options']
        else:
            self.options = {}

        # Call back event
        self.parent_cont.set_event_cb(self._lv_event_callback)

    def _lv_event_callback(self, lv_obj, event):
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

        #ptr = lv.indev_get_act()
        # self.indev.get_point(self.last_click_pt)
        # print(self.name, event_text, self.last_click_pt)

    def set_pos(self, x_pos, y_pos):
        if self.parent_cont is None:
            self.pos_x = x_pos
            self.pos_y = y_pos
        else:
            self.parent_cont.set_pos(x_pos, y_pos)

    def update(self, watch_status_obj):
        pass

    def deinit(self):
        pass


class LvSymbolButton(LvWatchFaceObj):

    def __init__(self, watchface_cfg, lv_cont=None):
        super().__init__(watchface_cfg=watchface_cfg, parent_cont=lv_cont)

        self.symbol_button = lv.btn(self.parent_cont)
        # self.symbol_button.set_size(self.parent_cont.size_x - 10, self.parent_cont.size_y - 10)
        self.symbol_button.set_size(self.styles['button']['size_x'], self.styles['button']['size_y'])
        self.symbol_button.align(self.parent_cont, lv.ALIGN.CENTER, 0, 0)
        self.symbol_button_style = styles.button_style_3D
        self.symbol_button.add_style(self.symbol_button.PART.MAIN, self.symbol_button_style)

        self.symbol_button_label = lv.label(self.symbol_button)
        self.symbol_button_label.set_recolor(True)
        self.symbol_button_label.add_style(self.symbol_button_label.PART.MAIN,
                                     styles.get_style_text(int(self.styles['text']['size']), self.styles['text']['color']))

        if 'symbol_text_separator' in self.options:
            self.cur_sep = self.options['symbol_text_separator']
        else:
            self.cur_sep = ''

        self.cur_text = ''
        if 'text' in self.options and 'val' in self.options['text']:
            if 'color' in self.options['text']:
                self.cur_text += '#{} '.format(self.options['text']['color'])
            self.cur_text += self.options['text']['val']
            if 'color' in self.options['text']:
                self.cur_text += '#'

        self.cur_symbol = ''
        if 'symbol' in self.options and 'val' in self.options['symbol']:
            if 'color' in self.options['symbol']:
                self.cur_symbol += '#{} '.format(self.options['symbol']['color'])

            if self.options['symbol']['val'] in styles.LV_SYMBOL.__dict__:
                self.cur_symbol += getattr(styles.LV_SYMBOL, self.options['symbol']['val'])
            else:
                print('Invalid Symbol label symbol:', self.options['symbol']['val'])

            if 'color' in self.options['symbol']:
                self.cur_symbol += '#'

        self.label_text = '{}{}{}'.format(self.cur_symbol, self.cur_sep, self.cur_text)
        self.symbol_button_label.set_text(self.label_text)


class LvSymbolLabel(LvWatchFaceObj):

    def __init__(self, watchface_cfg, lv_cont=None):
        super().__init__(watchface_cfg=watchface_cfg, parent_cont=lv_cont)

        self.symbol_label = lv.label(self.parent_cont)
        self.symbol_label.set_recolor(True)
        self.symbol_label.set_align(lv.label.ALIGN.CENTER)
        self.symbol_label.add_style(self.symbol_label.PART.MAIN,
                                   styles.get_style_text(int(self.styles['text']['size']), self.styles['text']['color']))

        if 'states' in self.options:
            self.states = self.options['states']
        else:
            self.states = []

        self.cur_label_text = ''
        self.cur_symbol = ''
        self.cur_sep = ' '
        self.cur_text = ''

        # Build symbol text & colors for each state
        for sl_state in self.states:

            sl_state['symbol']['text'] = ''
            if 'symbol' in sl_state and 'val' in sl_state['symbol'] and sl_state['symbol']['val'] != "":
                if 'color' in sl_state['symbol']:
                    sl_state['symbol']['text'] += '#{} '.format(sl_state['symbol']['color'])

                if sl_state['symbol']['val'] in styles.LV_SYMBOL.__dict__:
                    # sl_state['symbol']['text'] += globals()[sl_state['symbol']['val']]
                    sl_state['symbol']['text'] += getattr(styles.LV_SYMBOL, sl_state['symbol']['val'])
                else:
                    print('Invalid Symbol:', sl_state['symbol']['val'])

                if 'color' in sl_state['symbol']:
                    sl_state['symbol']['text'] += '#'

            if sl_state['on'] == 'init':
                self.cur_symbol = sl_state['symbol']['text']
                self.cur_sep = sl_state['symbol_text_seperator']
                # Default value
                if 'default_val' in sl_state['text']:
                    if 'color' in sl_state['text']:
                        self.cur_text += '#{} '.format(sl_state['text']['color'])

                    if 'fixed_num_chars' in sl_state['text'] and sl_state['text']['fixed_num_chars'] > 0:
                        self.cur_text += '{0:0{1}}'.format(sl_state['text']['default_val'],
                                                           sl_state['text']['fixed_num_chars'])
                    else:
                        self.cur_text += '{}'.format(sl_state['text']['default_val'])

                    if 'units' in sl_state['text']:
                        self.cur_text += '{}'.format(sl_state['text']['units'])
                    if 'color' in sl_state['text']:
                        self.cur_text += '#'

        self.cur_label_text = '{}{}{}'.format(self.cur_symbol, self.cur_sep, self.cur_text)
        self.symbol_label.set_text(self.cur_label_text)

    def _do_cast(self, val, cast_text):
        if cast_text == 'text':
            return str(val)
        if cast_text == 'int':
            return int(val)
        if cast_text == 'float':
            return float(val)

    def _comparator(self, ls, op, rs, cast=None):

        if op == 'lt' and ls < rs:
            return True
        elif op == 'le' and ls <= rs:
            return True
        elif op == 'eq' and ls == rs:
            return True
        elif op == 'gt' and ls > rs:
            return True
        elif op == 'ge' and ls >= rs:
            return True
        elif op == 'ne' and ls != rs:
            return True
        else:
            return False

    def update(self, watch_status_obj):

        if 'state_value' not in self.options:
            return

        if self.options['state_value'] not in watch_status_obj:
            return

        _found_match = False
        _ls = watch_status_obj[self.options['state_value']]
        for sl_state in self.states:
            if sl_state['on'] != 'load':
                continue

            if _found_match is True:
                break

            _comp_retval = False
            _comp_logic = sl_state['comparator']['logic']
            for operand in sl_state['comparator']['operands']:
                _rs = operand['val']
                _op = operand['operator']
                _comp_retval = self._comparator(ls=_ls, op=_op, rs=_rs)
                if _comp_logic == "always":
                    _found_match = True
                    break
                elif _comp_logic == "or" and _comp_retval is True:
                    _found_match = True
                    break
                elif _comp_logic == "and" and _comp_retval is False:
                    _found_match = False
                    break
                else:
                    # logic = or and comp = False
                    # logic = and and comp = True
                    _found_match = _comp_retval

            if _found_match is True:
                self.cur_symbol = sl_state['symbol']['text']

                self.cur_text = ''
                if 'color' in sl_state['text']:
                    self.cur_text += '#{} '.format(sl_state['text']['color'])

                _noformat_val = ''
                # if sl_state['text']['cast'] == 'int':
                #     _noformat_val = 0
                # elif sl_state['text']['cast'] == 'float':
                #     _noformat_val = 0.0

                if sl_state['text']['src_val'] in watch_status_obj:
                    _noformat_val = watch_status_obj[sl_state['text']['src_val']]
                elif sl_state['text']['default_val'] in watch_status_obj:
                    _noformat_val = sl_state['text']['default_val']
                    self.cur_text += '{}'.format(sl_state['text']['default_val'])

                if 'fixed_num_chars' in sl_state['text'] and sl_state['text']['fixed_num_chars'] > 0:
                    self.cur_text += '{0:0{1}}'.format(_noformat_val, int(sl_state['text']['fixed_num_chars']))
                else:
                    self.cur_text += '{}'.format(_noformat_val)

                if 'units' in sl_state['text'] and sl_state['text']['units'] != '':
                    self.cur_text += '{}'.format(sl_state['text']['units'])

                if 'color' in sl_state['text']:
                    self.cur_text += '#'

                self.cur_sep = sl_state['symbol_text_seperator']

        if _found_match is True:
            self.cur_label_text = '{}{}{}'.format(self.cur_symbol, self.cur_sep, self.cur_text)
            # print("Found:", self.cur_text)
            self.symbol_label.set_text(self.cur_label_text)


class LvDebug(LvWatchFaceObj):

    def __init__(self, watchface_cfg, lv_cont=None):
        super().__init__(watchface_cfg=watchface_cfg, parent_cont=lv_cont)

        self.debug_label = lv.label(self.parent_cont)
        self.debug_label.set_recolor(True)
        self.debug_label.set_align(lv.label.ALIGN.CENTER)
        self.debug_label.add_style(self.debug_label.PART.MAIN,
                                  styles.get_style_text(int(self.styles['text']['size']), self.styles['text']['color']))

        self.debug_label.set_text('')

        self.debug_label.set_pos(0, 0)
        self.debug_label.set_size(240, 240)

    def update(self, watch_status_obj):
        _debug_txt = '\n'.join(watch_status_obj['log'])

        self.debug_label.set_text(_debug_txt)


class LvPower(LvWatchFaceObj):

    def __init__(self, watchface_cfg, lv_cont=None):
        super().__init__(watchface_cfg=watchface_cfg, parent_cont=lv_cont)


        # self.parent_cont.set_fit(lv.FIT.NONE)
        # self.parent_cont.set_layout(lv.LAYOUT.ROW_MID)

        self.batt_label = lv.label(self.parent_cont)
        self.batt_label.set_recolor(True)
        self.batt_label.set_align(lv.label.ALIGN.CENTER)
        self.batt_label.add_style(self.batt_label.PART.MAIN,
                                  styles.get_style_text(int(self.styles['text']['size']), self.styles['text']['color']))

        self.batt_label.set_text('#d3d3d3 {0}# 0%'.format(lv.SYMBOL.BATTERY_EMPTY))

        #self.batt_label.set_pos(self.pos_x, self.pos_y)
        #self.batt_label.set_size(self.size_x, self.size_y)

    def update(self, watch_status_obj):
        _batt_text = ''

        #print(watch_status_obj['battery_perc'])

        if watch_status_obj['battery_charging'] is True:
            _batt_text = '#0000ff {0}# '.format(lv.SYMBOL.CHARGE)
        elif watch_status_obj['usb_connected'] is True:
            _batt_text = '#0000ff {0}# '.format(lv.SYMBOL.USB)

        if watch_status_obj['battery_perc'] >= 90:
            _batt_text += '#00ff00 {0}#'.format(lv.SYMBOL.BATTERY_FULL)
            # self.wifi_label.set_text('#00ff00 {0}#'.format(lv.SYMBOL.WIFI, watch_status_obj['SSID']))
        elif 60 <= watch_status_obj['battery_perc'] < 90:
            _batt_text += '#00ff00 {0}#'.format(lv.SYMBOL.BATTERY_3)
        elif 40 <= watch_status_obj['battery_perc'] < 60:
            _batt_text += '#00ff00 {0}#'.format(lv.SYMBOL.BATTERY_2)
        elif 10 <= watch_status_obj['battery_perc'] < 40:
            _batt_text += '#ffff00 {0}#'.format(lv.SYMBOL.BATTERY_1)
        elif 0 <= watch_status_obj['battery_perc'] < 10:
            _batt_text += '#ff0000 {0}#'.format(lv.SYMBOL.BATTERY_EMPTY)

        if self.options['include_battery_percentage'] == 'yes':
            _batt_text += ' {}%'.format(watch_status_obj['battery_perc'])

        if self.options['include_battery_voltage'] == 'yes':
            _batt_text += ' {:.3}'.format((watch_status_obj['battery_volts']/1000))

        self.batt_label.set_text(_batt_text)


class LvWifi(LvWatchFaceObj):

    def __init__(self, watchface_cfg, lv_cont=None):
        super().__init__(watchface_cfg=watchface_cfg, parent_cont=lv_cont)

        # self.parent_cont.set_fit(lv.FIT.NONE)
        # self.parent_cont.set_layout(lv.LAYOUT.CENTER)

        self.wifi_label = lv.label(self.parent_cont)
        self.wifi_label.set_recolor(True)
        self.wifi_label.set_align(lv.label.ALIGN.CENTER)
        self.wifi_label.add_style(self.wifi_label.PART.MAIN,
                                  styles.get_style_text(int(self.styles['text']['size']), self.styles['text']['color']))

        self.wifi_label.set_text('#d3d3d3 {}#'.format(lv.SYMBOL.WIFI))

        # self.wifi_label.set_pos(self.pos_x, self.pos_y)
        # self.wifi_label.set_size(self.size_x, self.size_y)

    def update(self, watch_status_obj):
        _wifi_text = ''
        if watch_status_obj['connected'] is True:
            _wifi_text = '#00ff00 {0}#'.format(lv.SYMBOL.WIFI)
            # self.wifi_label.set_text('#00ff00 {0}#'.format(lv.SYMBOL.WIFI, watch_status_obj['SSID']))
        else:
            _wifi_text = '#ff0000 {0}#'.format(lv.SYMBOL.WIFI)

        if self.options['include_ssid'] == 'yes':
            _wifi_text += ' {}'.format(watch_status_obj['SSID'])

        self.wifi_label.set_text(_wifi_text)


class LvLabel(LvWatchFaceObj):

    def __init__(self, watchface_cfg, lv_cont=None):
        super().__init__(watchface_cfg=watchface_cfg, parent_cont=lv_cont)

        self.label = lv.label(self.parent_cont)
        self.label.set_recolor(True)
        self.label.set_align(lv.label.ALIGN.CENTER)
        self.label.add_style(self.label.PART.MAIN,
                                  styles.get_style_text(int(self.styles['text']['size']), self.styles['text']['color']))

        self.label.set_text('{}'.format('label'))

        # self.wifi_label.set_pos(self.pos_x, self.pos_y)
        # self.wifi_label.set_size(self.size_x, self.size_y)

    def update(self, watch_status_obj):
        pass


class LvDate(LvWatchFaceObj):

    def __init__(self, watchface_cfg, lv_cont=None):
        super().__init__(watchface_cfg=watchface_cfg, parent_cont=lv_cont)

        self.date_label = lv.label(self.parent_cont)
        self.date_label.set_recolor(True)
        self.date_label.set_align(lv.label.ALIGN.CENTER)
        self.date_label.add_style(self.date_label.PART.MAIN,
                                  styles.get_style_text(int(self.styles['text']['size']), self.styles['text']['color']))

        # self.date_label.set_pos(self.pos_x, self.pos_y)
        # self.date_label.set_size(self.size_x, self.size_y)
        (self.year, self.month, self.mday, _hour, _minute, _second, self.weekday, self.yearday) = time.localtime()
        self.date_text = self.format_date()
        self.date_label.set_text(self.date_text)

    def format_date(self):
        _date_text = '{0}/{1}/{2}'.format(self.month, self.mday, self.year)
        if 'format' not in self.options:
            return _date_text
        else:
            _date_text = ''

        for _fi in self.options['format']:

            if _fi == 'dow':
                if 'dow_format' in self.options and self.options['dow_format'] in styles.dow[self.weekday]:
                    _date_text += styles.dow[self.weekday][self.options['dow_format']]
                else:
                    _date_text += styles.dow[self.weekday]['short']

            elif _fi == 'date':
                _s_month = self.month - 1
                if 'date' in self.options and 'format' in self.options['date']:
                    for _df in self.options['date']['format']:

                        if _df == 'month':
                            if 'month_format' in self.options['date'] and self.options['date']['month_format'] \
                                    in styles.months[_s_month]:
                                _date_text += '{}'.format(styles.months[_s_month][self.options['date']['month_format']])
                            else:
                                _date_text += '{}'.format(styles.months[_s_month]['num'])

                        elif _df == 'day':
                            _date_text += '{}'.format(self.mday)

                        elif _df == 'year':
                            if 'year_format' in self.options['date'] and self.options['date']['year_format'] == 'short':
                                _date_text += '{}'.format(int(self.year - 2000))
                            else:
                                _date_text += '{}'.format(self.year)

                        else:
                            _date_text += '{}'.format(_df)

                else:
                    _date_text += '{0}/{1}/{2}'.format(self.month, self.mday, self.year)
            else:
                _date_text += '{}'.format(_fi)

        return _date_text

    def update(self, watch_status_obj):

        if 'local_time' in watch_status_obj:
            (self.year, self.month, self.mday, _hour, _minute, _second, self.weekday, self.yearday) =\
                time.localtime(watch_status_obj['local_time'])
        else:
            (self.year, self.month, self.mday, _hour, _minute, _second, self.weekday, self.yearday) = time.localtime()

        self.date_text = ''

        if 'text' in self.styles and 'color' in self.styles['text']:
            self.date_text += '#{} '.format(self.styles['text']['color'])

        self.date_text += self.format_date()

        if 'text' in self.styles and 'color' in self.styles['text']:
            self.date_text += '#'

        self.date_label.set_text(self.date_text)
        # print('Date:', self.date_text)


class LvDigitalClock(LvWatchFaceObj):

    def __init__(self, watchface_cfg, lv_cont=None):
        super().__init__(watchface_cfg=watchface_cfg, parent_cont=lv_cont)

        self.blink_second_on = True
        self.time_label = lv.label(self.parent_cont)
        self.time_label.set_recolor(True)
        self.time_label.set_align(lv.label.ALIGN.CENTER)
        self.time_label.add_style(self.time_label.PART.MAIN,
                                  styles.get_style_text(int(self.styles['text']['size']), self.styles['text']['color']))
        self.time_label.set_text('00:00:00')
        # self.time_label.set_long_mode(lv.label.LONG.SROLL_CIRC)

        # Do we need this after containers???
        # self.time_label.set_pos(self.pos_x, self.pos_y)
        # self.time_label.set_size(self.size_x, self.size_y)

        '''
        if self.options['include_hr'] == 'yes':
            self.time_label_hr = lv.label(self.parent_cont)
            self.time_label_hr.set_recolor(True)
            self.time_label_hr.set_align(lv.label.ALIGN.CENTER)
            self.time_label_hr.add_style(self.time_label_hr.PART.MAIN,
                                         styles.get_style_text(int(self.styles['text']['size']),
                                                               self.styles['text']['color']))

            self.time_label_hr.set_text('00')

        self.time_label_hrp = lv.label(self.parent_cont)
        self.time_label_hrp.set_recolor(True)
        self.time_label_hrp.set_align(lv.label.ALIGN.CENTER)
        self.time_label_hrp.add_style(self.time_label_hrp.PART.MAIN,
                                      styles.get_style_text(int(self.styles['text']['size']),
                                                            self.styles['text']['color']))
        self.time_label_hrp.set_text(':')

        if self.options['include_min'] == 'yes':
            self.time_label_min = lv.label(self.parent_cont)
            self.time_label_min.set_recolor(True)
            self.time_label_min.set_align(lv.label.ALIGN.CENTER)
            self.time_label_min.add_style(self.time_label_min.PART.MAIN,
                                          styles.get_style_text(int(self.styles['text']['size']),
                                                                self.styles['text']['color']))

            self.time_label_min.set_text('00')
        '''

    def update(self, watch_status_obj):
        (_year, _month, _mday, _hour, _minute, _second, _weekday, _yearday) = time.localtime(watch_status_obj['local_time'])

        # Gotta find out why styles are blown away during callback??
        if 'styles' in self.cfg:
            self.styles.update(self.cfg['styles'])
        # print('dclock cfg:', self.name, self.cfg)
        # print('dclock options styles:', self.options, self.styles)

        # d_txt = '{:02n}:{:02n}:{:02n} {}'.format(self.hour, self.minute, self.second, self.biday)
        d_txt = ''

        if self.options['include_hr'] == 'yes':
            if self.options['format'] == '24hr':
                d_txt += '{:02n}'.format(_hour)
            elif _hour == 0:
                d_txt += '{:02n}'.format(12)
            elif _hour > 12:
                d_txt += '{:02n}'.format(_hour - 12)
            else:
                d_txt += '{:02n}'.format(_hour)

            # self.time_label_hr.set_text(d_txt)

        if self.options['include_min'] == 'yes':
            if d_txt != '':
                if self.blink_second_on is True:
                    if 'background' in self.styles and 'color' in self.styles['background']:
                        d_txt += '#{} :#'.format(self.styles['background']['color'])
                    else:
                        print('Blink second is on but no background defined!')
                    # self.time_label_hrp.set_text(' ')
                    self.blink_second_on = False
                else:
                    d_txt += ':'
                    # self.time_label_hrp.set_text(':')
                    self.blink_second_on = True

            d_txt += '{:02n}'.format(_minute)
            # self.time_label_min.set_text('{:02n}'.format(_minute))

        if self.options['include_sec'] == 'yes':
            if d_txt != '':
                d_txt += ':'
            d_txt += '{:02n}'.format(_second)

        if self.options['include_ampm'] == 'yes':
            if d_txt != '':
                d_txt += ' '
            if _hour >= 12:
                d_txt += 'pm'
            else:
                d_txt += 'am'
        # print('Digitizing:', d_txt)
        self.time_label.set_text(d_txt)

    def deinit(self):
        self.parent_cont.clean()


# class WatchFace(lv.cont):
class WatchFace:

    def __init__(self, watch, screen, callback=None, config_file='/watchfaces/watchface_default.json', size_x=240, size_y=240):

        # Canvas approach
        # self._cbuff = bytearray(size_x * size_y * 4)
        # self.canvas = lv.canvas(screen)
        # self.canvas.set_buffer(self._cbuff, size_x, size_y, lv.img.CF.TRUE_COLOR)
        # self.canvas.fill_bg(styles.LV_COLOR_LIGHT_GREY, lv.OPA.COVER)
        self.name = 'Watchface Default'
        self.watch = watch
        self.screen = screen
        self.config_file = config_file
        self.containers = {}
        self.objs = {}
        self.lv_task_updater = None
        self.task_data = {}
        self.refresh_counter = 0
        try:
            with open(config_file) as wf_cfg:
                self.cfg = json.load(wf_cfg)
        except OSError:
            print('Missing or error reading watchface config:', config_file)
            exit(-1)

        # Use PNG from imagetools
        # Register new image decoder
        self.decoder = lv.img.decoder_create()
        self.decoder.info_cb = get_png_info
        self.decoder.open_cb = open_png

        self.bg_img_dsc = lv.img_dsc_t()
        self.bg_img = lv.img(screen)
        self.bg_draw_img = lv.draw_img_dsc_t()
        self.bg_draw_img.init()

        if callback is not None:
            self.bg_img.set_event_cb(callback)

        self.debug_cfg = {
            "type": "LvDebug",
            "src": "debug",
            "layout": {
                "format": "12h",
                "include_battery_percentage": "yes",
                "include_battery_voltage": "yes"
            },
            "styles": {
                "transparent": "no",
                "text": {
                    "size": 12,
                    "color": "0000ff"
                },
                "background": {
                    "color": "00fffa"
                }
            },
            "x_start": 5,
            "y_start": 5,
            "x_end": 230,
            "y_end": 230
        }

    def load(self):

        if 'wallpaper' in self.cfg and 'type' in self.cfg['wallpaper']:
            if self.cfg['wallpaper']['type'] == 'png':
                with open(self.cfg['wallpaper']['filename'], 'rb') as f:
                    buff = f.read()
                    self.bg_img_dsc.data = buff
                    self.bg_img_dsc.data_size = len(buff)

                    # print('buff size:', img_dsc.data_size)
                if self.bg_img_dsc.data_size > 0:
                    self.bg_img.set_src(self.bg_img_dsc)

        # Build containers for watchface, default if none defined in config file
        if 'containers' in self.cfg and len(self.cfg['containers']) > 0:
            for _cont_i in self.cfg['containers']:
                _cont = LvWatchFaceContainer(container_cfg=_cont_i, parent_cont=self.screen)
                self.containers[_cont.name] = _cont
        else:
            self.containers['DEFAULT'] = LvWatchFaceContainer(container_cfg=None, parent_cont=self.screen)


        # self.update()
        # Build watchface objects
        for lvitem in self.cfg['lv_objects']:

            if 'type' not in lvitem or 'name' not in lvitem:
                print('Invalid lv_object config -> type or name missing, skipping:', lvitem)
                continue

            if 'container' in lvitem and 'inside' in lvitem['container']:
                _cont_name = lvitem['container']['inside']
            else:
                _cont_name = 'DEFAULT'

            if _cont_name not in self.containers:
                print('Invalid lv_object config -> container doesnt exist, skipping:', lvitem)
                continue

            if lvitem['type'] in globals():
                print("Build object:", lvitem['type'], lvitem)
                self.objs[lvitem['name']] = globals()[lvitem['type']](watchface_cfg=lvitem,
                                                                      lv_cont=self.containers[_cont_name])
                self.containers[_cont_name].num_objs += 1
            else:
                print('Unknown watchface object type:', lvitem['type'], lvitem['name'])
                continue

            '''
            if lvitem == 'digital_clock' and self.digital_clock is None:
                self.digital_clock = LvDigitalClock(watchface_cfg=self.cfg['lv_objects'][lvitem], lv_cont=self.screen)

            if lvitem == 'wifi' and self.wifi is None:
                self.wifi = LvWifi(watchface_cfg=self.cfg['lv_objects'][lvitem], lv_cont=self.screen)

            if lvitem == 'power' and self.power is None:
                self.power = LvPower(watchface_cfg=self.cfg['lv_objects'][lvitem], lv_cont=self.screen)
           '''
        # Canvas approach
        # self.digital_clock = lv_digitlineclock.LvDigitLineClock(size_x=220, size_y=75, digit_margin=12)
        # self.digital_clock.set_pos(20, 90)
        # self.digital_clock.update()
        #self.canvas.draw_img(0, 0, self.bg_img, self.bg_draw_img)

        # for line_pts in self.digital_clock.digit_pts:
        #     print('Line:', line_pts)
        #     draw_line_dsc = lv.draw_line_dsc_t()
        #     draw_line_dsc.init()
        #     draw_line_dsc.color = styles.LV_COLOR_BLUE
        #     draw_line_dsc.width = 8
        #     draw_line_dsc.round_end = True
        #     draw_line_dsc.round_start = True
        #     self.canvas.draw_line(line_pts, len(line_pts), draw_line_dsc)
        # img = lv.img(screen)
        # img.set_src(img_dsc)
        if 'refresh' in self.cfg and 'interval_msec' in self.cfg['refresh']:
            _refresh_msec = int(self.cfg['refresh']['interval_msec'])
            if _refresh_msec < 200:
                _refresh_msec = 200
        else:
            _refresh_msec = 500

        self.lv_task_updater = lv.task_create(self.update_task, _refresh_msec, lv.TASK_PRIO.MID, self.task_data)
        # print(self.watch.status)
        # print(globals()['MyWatch.status'])

    def update(self, watch_status=None):
        #print('Task', lv_task)
        pass

    def update_task(self, lv_task):

        '''
        for _cont in self.containers.keys():
            self.containers[_cont].show_layout()

        time.sleep(10)
        for _cont in self.containers.keys():
            self.containers[_cont].reset_layout()
        '''

        if self.watch.is_awake is False:
            return

        for lvitem in self.objs.keys():
            if self.objs[lvitem] is None:
                continue
            if self.objs[lvitem].refresh_interval_multiplier == 0:
                continue

            if self.objs[lvitem].src in self.watch.status:
                # print('In here',self.refresh_counter,self.objs[lvitem].refresh_interval_multiplier)
                if self.refresh_counter % self.objs[lvitem].refresh_interval_multiplier == 0:
                    self.objs[lvitem].update(self.watch.status[self.objs[lvitem].src])
                    # print('Updating:', lvitem)

        #Overlay debugging info if present
        if 'debug' in self.watch.status and len(self.watch.status['debug']['log']) > 0:
            if 'LvDebug' not in self.objs:
                self.objs['LvDebug'] = LvDebug(watchface_cfg=self.debug_cfg, lv_cont=self.screen)
            self.objs['LvDebug'].update(self.watch.status['debug'])
        elif 'LvDebug' in self.objs:
            del self.objs['LvDebug']

        # Update refresh counter
        self.refresh_counter += 1
        if self.refresh_counter > 432000:
            self.refresh_counter = 0



