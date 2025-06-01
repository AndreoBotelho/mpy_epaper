import EPD_154_D67 as epaper
import machine
from machine import SPI,Pin
import time

spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(6), mosi=Pin(7))
#cs = Pin(7, Pin.OUT, value=0)
dc = Pin(4)
rst = Pin(8)
#busy = Pin(3)

e = epaper.EPD(spi, dc=dc, rst=rst)#cs=cs, busy=busy)

import framebuf
buf = bytearray(200 * 200 // 8)
fb = framebuf.FrameBuffer(buf, 200, 200, framebuf.MONO_HLSB)
black = 0
white = 1

w = 200
h = 200
x = 0
y = 0

# --------------------

# write hello world with black bg and white text
fb.fill(white)
fb.text('FULL REFRESH 2S',40,90,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
time.sleep_ms(500)
e.set_frame_memory(bg_cat, x, y, w, h)
e.display_frame()
# --------------------

# write hello world with white bg and black text
e.set_update_mode(epaper.UPDATE_FAST)
fb.fill(white)
fb.text('FAST REFRESH 1S',40,90,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
time.sleep_ms(500)
e.set_frame_memory(bg_cat, x, y, w, h)
e.display_frame()

# --------------------

# write hello world with white bg and black text
fb.fill(white)
fb.text('VERTICAL INVERTED DISPLAY',5,90,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
time.sleep_ms(500)
e.set_orientation(epaper.INVERTED)
e.set_frame_memory(bg_cat, x, y, w, h)
e.display_frame()
time.sleep_ms(500)
e.set_orientation(epaper.NORMAL)
fb.fill(white)
fb.text('VERTICAL NORMAL DISPLAY',5,90,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
time.sleep_ms(500)

# --------------------

# clear display
fb.fill(white)
fb.text('PART REFRESH 300ms',40,90,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
e.set_update_mode(epaper.UPDATE_PART)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()


# use a frame buffer
# 128 * 296 / 8 = 4736 - thats a lot of pixels
fb.fill(white)
fb.text('Hello World',30,0,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
fb.pixel(30, 10, black)
fb.hline(30, 30, 10, black)
fb.vline(30, 50, 10, black)
fb.line(30, 70, 40, 80, black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
fb.rect(30, 90, 10, 10, black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
fb.fill_rect(30, 110, 10, 10, black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
fb.text('Line 24',0,192,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
time.sleep(1)

# --------------------

# wrap text inside a box
# clear
fb.fill(white)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
time.sleep(1)

# display as much as this as fits in the box
str = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam vel neque in elit tristique vulputate at et dui. Maecenas nec felis lectus. Pellentesque sit amet facilisis dui. Maecenas ac arcu euismod, tempor massa quis, ultricies est.'

# this could be useful as a new method in FrameBuffer
def text_wrap(str,x,y,color,w,h,border=None):
    # optional box border
    if border is not None:
        fb.rect(x, y, w, h, border)
    cols = w // 8
    # for each row
    j = 0
    for i in range(0, len(str), cols):
        # draw as many chars fit on the line
        fb.text(str[i:i+cols], x, y + j, color)
        j += 8
        # dont overflow text outside the box
        if j >= h:
            break

# draw text box 1
# box position and dimensions
bx = 8
by = 8
bw = w - 16 # 112 = 14 cols
bh = w - 16 # 112 = 14 rows (196 chars in total)
text_wrap(str,bx,by,black,bw,bh,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
time.sleep(1)

# draw text box 2
bx = 0
by = 100
bw = w # 128 = 16 cols
bh = 6 * 8 # 48 = 6 rows (96 chars in total)
text_wrap(str,bx,by,black,bw,bh,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
time.sleep(1)

# draw text box 3
bx = 0
by = 150
bw = w//2 # 64 = 8 cols
bh = 8 * 8 # 64 = 8 rows (64 chars in total)
text_wrap(str,bx,by,black,bw,bh,None)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
time.sleep(1)

# --------------------
e.set_update_mode(epaper.UPDATE_FAST)
e.set_frame_memory(bg_cat, x, y, w, h)
e.display_frame()
e.hibernate()
time.sleep(1)

#machine.reset()
