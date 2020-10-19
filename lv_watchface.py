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


class LvWatchFaceObj:

    def __init__(self, watchface_cfg, parent_cont=None):
        print('obj cfg:', watchface_cfg)
        self.cont_main = lv.cont(parent_cont)
        self.size_x = int(watchface_cfg['x_end']) - int(watchface_cfg['x_start'])
        self.size_y = int(watchface_cfg['y_end']) - int(watchface_cfg['y_start'])
        self.pos_x = int(watchface_cfg['x_start'])
        self.pos_y = int(watchface_cfg['y_start'])
        self.can_update = False

        self.cont_main.set_pos(self.pos_x, self.pos_y)
        self.cont_main.set_size(self.size_x, self.size_y)

    def set_pos(self, x_pos, y_pos):
        if self.cont_main is None:
            self.pos_x = x_pos
            self.pos_y = y_pos
        else:
            self.cont_main.set_pos(x_pos, y_pos)

    def update(self):
        pass

    def deinit(self):
        pass


class LvDigitalClock(LvWatchFaceObj):

    def __init__(self, watchface_cfg, lv_cont=None):
        super().__init__(watchface_cfg=watchface_cfg, parent_cont=lv_cont)

        self.styles = watchface_cfg['styles']
        self.layout = watchface_cfg['layout']
        self.cont_main.set_fit(lv.FIT.NONE)

        # self.cont_main.set_layout(lv.LAYOUT.PRETTY_MID)
        self.cont_main.set_layout(lv.LAYOUT.ROW_MID)

        self.cont_style = lv.style_t()
        self.cont_style.init()
        self.cont_style.set_pad_all(lv.STATE.DEFAULT, 1)
        self.cont_style.set_margin_all(lv.STATE.DEFAULT, 1)
        self.cont_style.set_border_opa(lv.STATE.DEFAULT, lv.OPA.TRANSP)
        self.cont_style.set_bg_opa(lv.STATE.DEFAULT, lv.OPA.TRANSP)
        self.cont_main.add_style(self.cont_main.PART.MAIN, self.cont_style)

        self.time = time.time()
        (self.year, self.month, self.mday, self.hour, self.minute, self.second, self.weekday,
         self.yearday) = time.localtime()

        self.time_label = lv.label(self.cont_main)
        self.time_label.set_recolor(True)
        self.time_label.set_align(lv.label.ALIGN.CENTER)
        self.time_label.add_style(self.time_label.PART.MAIN,
                                  styles.get_style_text(int(self.styles['text']['size']), self.styles['text']['color']))

    def update(self):
        self.time = time.time()
        (self.year, self.month, self.mday, self.hour, self.minute, self.second, self.weekday, self.yearday) = time.localtime()

        # d_txt = '{:02n}:{:02n}:{:02n} {}'.format(self.hour, self.minute, self.second, self.biday)
        d_txt = ''

        if self.layout['include_hr'] == 'Yes':
            d_txt += '{:02n}'.format(self.hour)

        if self.layout['include_min'] == 'Yes':
            if d_txt != '':
                d_txt += ':'
            d_txt += '{:02n}'.format(self.minute)

        if self.layout['include_sec'] == 'Yes':
            if d_txt != '':
                d_txt += ':'
            d_txt += '{:02n}'.format(self.second)

        if self.layout['include_ampm'] == 'Yes':
            if d_txt != '':
                d_txt += ' '
            if self.hour >= 12:
                d_txt += 'pm'
            else:
                d_txt += 'am'
        print('Digitizing:', d_txt)
        self.time_label.set_text(d_txt)

    def deinit(self):
        self.cont_main.clean()


class WatchFace(lv.cont):

    def __init__(self, screen, config_file='/watchfaces/watchface_default.json', size_x=240, size_y=240):
        super().__init__()

        # Canvas approach
        # self._cbuff = bytearray(size_x * size_y * 4)
        # self.canvas = lv.canvas(screen)
        # self.canvas.set_buffer(self._cbuff, size_x, size_y, lv.img.CF.TRUE_COLOR)
        # self.canvas.fill_bg(styles.LV_COLOR_LIGHT_GREY, lv.OPA.COVER)
        self.screen = screen
        self.config_file = config_file
        with open(config_file) as wf_cfg:
            self.cfg = json.load(wf_cfg)

        # Use PNG from imagetools
        # Register new image decoder
        self.decoder = lv.img.decoder_create()
        self.decoder.info_cb = get_png_info
        self.decoder.open_cb = open_png

        self.bg_img_dsc = lv.img_dsc_t()
        self.bg_img = lv.img(screen)
        self.bg_draw_img = lv.draw_img_dsc_t()
        self.bg_draw_img.init()
        self.digital_clock = None

    def load(self):

        with open(self.cfg['png']['filename'], 'rb') as f:
            buff = f.read()
            self.bg_img_dsc.data = buff
            self.bg_img_dsc.data_size = len(buff)

            # print('buff size:', img_dsc.data_size)
        if self.bg_img_dsc.data_size > 0:
            self.bg_img.set_src(self.bg_img_dsc)

        self.update()

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

    def update(self):
        for lvitem in self.cfg['lv_objects'].keys():

            if lvitem == 'digital_clock':
                if self.digital_clock is None:
                    self.digital_clock = LvDigitalClock(watchface_cfg=self.cfg['lv_objects'][lvitem],lv_cont=self.screen)
                self.digital_clock.update()





