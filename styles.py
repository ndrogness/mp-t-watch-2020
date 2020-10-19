import lvgl as lv

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
LV_COLOR_WATCH = lv.color_hex(0x00fffa)

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


def get_style_text(size, color='0x000000'):

    if size not in gstyle_text_fonts:
        size = 14

    style = lv.style_t()
    style.init()
    style.set_text_font(lv.STATE.DEFAULT, gstyle_text_fonts[size][1])
    #style.set_text_color(lv.STATE.DEFAULT, lv.color_hex(0x0000ff))
    style.set_text_color(lv.STATE.DEFAULT, lv.color_hex(int(color)))

    return style




