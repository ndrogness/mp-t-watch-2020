import lvgl as lv
import lvgl_fs_driver

# Layout & Fit & Symbol classes
LV_FIT = getattr(lv, 'FIT')
LV_LAYOUT = getattr(lv, 'LAYOUT')
LV_SYMBOL = getattr(lv, 'SYMBOL')

# Some lvgl C to python shortcuts
LV_OPA_COVER = lv.OPA.COVER
LV_STATE_DEFAULT = lv.STATE.DEFAULT

LV_COLOR_BLACK = lv.color_hex(0x000000)
LV_COLOR_WHITE = lv.color_hex(0xffffff)
LV_COLOR_RED = lv.color_hex(0xff0000)
LV_COLOR_BLUE = lv.color_hex(0x0000ff)
LV_COLOR_LIGHT_GREY = lv.color_hex(0xd3d3d3)
LV_COLOR_GREY = lv.color_hex(0x808080)
LV_COLOR_SILVER = lv.color_hex(0xc0c0c0)
LV_COLOR_YELLOW = lv.color_hex(0xffff00)
LV_COLOR_WATCH = lv.color_hex(0x00fffa)

# Days of the Week
dow = [
    {'short': 'Mon', 'long': 'Monday'},
    {'short': 'Tue', 'long': 'Tuesday'},
    {'short': 'Wed', 'long': 'Wednesday'},
    {'short': 'Thu', 'long': 'Thursday'},
    {'short': 'Fri', 'long': 'Friday'},
    {'short': 'Sat', 'long': 'Saturday'},
    {'short': 'Sun', 'long': 'Sunday'}
]

months = [
    {'short': 'Jan', 'long': 'January', 'num': 1},
    {'short': 'Feb', 'long': 'February', 'num': 2},
    {'short': 'Mar', 'long': 'March', 'num': 3},
    {'short': 'Apr', 'long': 'April', 'num': 4},
    {'short': 'May', 'long': 'May', 'num': 5},
    {'short': 'Jun', 'long': 'June', 'num': 6},
    {'short': 'Jul', 'long': 'July', 'num': 7},
    {'short': 'Aug', 'long': 'August', 'num': 8},
    {'short': 'Sep', 'long': 'September', 'num': 9},
    {'short': 'Oct', 'long': 'October', 'num': 10},
    {'short': 'Nov', 'long': 'November', 'num': 11},
    {'short': 'Dec', 'long': 'December', 'num': 12},
]
    #    'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# File system driver for Font loading
fs_drv = lv.fs_drv_t()
lvgl_fs_driver.fs_register(fs_drv, 'S')

myfont_cn = lv.font_t()
myfont_cn = lv.font_load("S:/fonts/font_ds_digital_20.bin")

class SymbolButton(lv.btn):
    def __init__(self, parent, symbol, text):
        super().__init__(parent)
        self.symbol = lv.label(self)
        self.symbol.set_text(symbol)
        self.symbol.set_style(symbolstyle)

        self.label = lv.label(self)
        self.label.set_text(text)

# Default Styles
default_watchface_styles = {
    "transparent": "yes",
    "text": {
        "size": 12,
        "color": "0000ff"
    },
    "background": {
        "color": "00fffa"
    },
    "spacing": {
        "margin": 1,
        "padding": 1,
    }
}

default_watchface_container = {
    "name": "A",
    "x_start": 0,
    "y_start": 0,
    "x_end": 240,
    "y_end": 240,
    "fit": "NONE",
    "layout": "CENTER",
    "styles": {
        "transparent": "yes",
        "spacing": {
            "margins": 1,
            "padding": 1
        }
    }
}

# 3D button
button_style_3D = lv.style_t()
button_style_3D.init()
# Set a background color and radius
button_style_3D.set_radius(lv.STATE.DEFAULT, 20)
button_style_3D.set_bg_opa(lv.STATE.DEFAULT, lv.OPA.COVER)
button_style_3D.set_bg_color(lv.STATE.DEFAULT, LV_COLOR_LIGHT_GREY)
# Add border to bottom right
button_style_3D.set_border_color(lv.STATE.DEFAULT, LV_COLOR_BLUE)
button_style_3D.set_border_width(lv.STATE.DEFAULT, 5)
button_style_3D.set_border_opa(lv.STATE.DEFAULT, lv.OPA._50)
button_style_3D.set_border_side(lv.STATE.DEFAULT, lv.BORDER_SIDE.BOTTOM | lv.BORDER_SIDE.RIGHT)

# Background style - color blue
gstyle_bg1 = lv.style_t()
gstyle_bg1.init()
gstyle_bg1.set_bg_color(lv.STATE.DEFAULT, LV_COLOR_BLUE)
gstyle_bg1.set_border_color(lv.STATE.DEFAULT, LV_COLOR_BLUE)

# Line style - color red
gstyle_line1 = lv.style_t()
gstyle_line1.init()
gstyle_line1.set_line_color(lv.STATE.DEFAULT, LV_COLOR_RED)

# Shadow Style - grey with blue shadow
gstyle_shadow1 = lv.style_t()
gstyle_shadow1.init()
#  Add background color and a radius
gstyle_shadow1.set_radius(lv.STATE.DEFAULT, 5)
gstyle_shadow1.set_bg_opa(lv.STATE.DEFAULT, lv.OPA.COVER)
gstyle_shadow1.set_bg_color(lv.STATE.DEFAULT, LV_COLOR_SILVER)
#  Add Shadow
gstyle_shadow1.set_shadow_width(lv.STATE.DEFAULT, 8)
gstyle_shadow1.set_shadow_color(lv.STATE.DEFAULT, LV_COLOR_BLUE)
gstyle_shadow1.set_shadow_ofs_x(lv.STATE.DEFAULT, 10)
gstyle_shadow1.set_shadow_ofs_y(lv.STATE.DEFAULT, 20)

gstyle_font1 = lv.style_t()
gstyle_font1.init()
gstyle_font1.set_text_font(lv.STATE.DEFAULT, lv.font_montserrat_28)
gstyle_font1.set_size(lv.STATE.DEFAULT, 50)

gstyle_text_fonts = {
    12: [lv.style_t(), lv.font_montserrat_12],
    14: [lv.style_t(), lv.font_montserrat_14],
    16: [lv.style_t(), lv.font_montserrat_16],
    18: [lv.style_t(), lv.font_montserrat_18],
    20: [lv.style_t(), lv.font_montserrat_20],
    22: [lv.style_t(), lv.font_montserrat_22],
    24: [lv.style_t(), lv.font_montserrat_24],
    26: [lv.style_t(), lv.font_montserrat_26],
    28: [lv.style_t(), lv.font_montserrat_28],
    30: [lv.style_t(), lv.font_montserrat_30],
    32: [lv.style_t(), lv.font_montserrat_32],
    34: [lv.style_t(), lv.font_montserrat_34],
    36: [lv.style_t(), lv.font_montserrat_36],
    38: [lv.style_t(), lv.font_montserrat_38],
    40: [lv.style_t(), lv.font_montserrat_40],
    42: [lv.style_t(), lv.font_montserrat_42],
    44: [lv.style_t(), lv.font_montserrat_44],
    46: [lv.style_t(), lv.font_montserrat_46],
    48: [lv.style_t(), lv.font_montserrat_48]
}

for fkey in gstyle_text_fonts.keys():
    gstyle_text_fonts[fkey][0].init()
    gstyle_text_fonts[fkey][0].set_text_font(lv.STATE.DEFAULT, gstyle_text_fonts[fkey][1])
    # gstyle_font1.set_size(lv.STATE.DEFAULT, 50)


def get_style_text(size, color='000000'):

    if size not in gstyle_text_fonts:
        size = 14

    style = lv.style_t()
    style.init()
    style.set_text_font(lv.STATE.DEFAULT, gstyle_text_fonts[size][1])
    # style.set_text_font(lv.STATE.DEFAULT, myfont_cn)
    style.set_text_color(lv.STATE.DEFAULT, lv.color_hex(int('0x{}'.format(color))))


    return style




