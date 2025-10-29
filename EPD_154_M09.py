"""
MicroPython Waveshare 1.54" Black/White GDEH0154D27 e-paper display driver
https://github.com/mcauser/micropython-waveshare-epaper

MIT License
Copyright (c) 2017 Waveshare
Copyright (c) 2018 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from micropython import const
from time import sleep_ms
import ustruct


_lut_20_vcomDC = bytearray([
  0x01, 0x05, 0x05, 0x05, 0x05, 0x01, 0x01,0x01, 0x05, 0x05, 0x05, 0x05, 0x01, 0x01,
  0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

_lut_21_ww = bytearray([
  0x01, 0x45, 0x45, 0x43, 0x44, 0x01, 0x01,0x01, 0x87, 0x83, 0x87, 0x06, 0x01, 0x01,
  0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

_lut_22_bw = bytearray([
  0x01, 0x05, 0x05, 0x45, 0x42, 0x01, 0x01,0x01, 0x87, 0x85, 0x85, 0x85, 0x01, 0x01,
  0x01, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

_lut_23_wb = bytearray([
  0x01, 0x08, 0x08, 0x82, 0x42, 0x01, 0x01,0x01, 0x45, 0x45, 0x45, 0x45, 0x01, 0x01,
  0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

_lut_24_bb = bytearray([
  0x01, 0x85, 0x85, 0x85, 0x83, 0x01, 0x01,0x01, 0x45, 0x45, 0x04, 0x48, 0x01, 0x01,
  0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

_lut_20_vcomDC_partial = bytearray([
  0x01, 0x04, 0x04, 0x03, 0x01, 0x01, 0x01,0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

_lut_21_ww_partial = bytearray([
  0x01, 0x04, 0x04, 0x03, 0x01, 0x01, 0x01,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])
_lut_22_bw_partial = bytearray([
  0x01, 0x84, 0x84, 0x83, 0x01, 0x01, 0x01,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

_lut_23_wb_partial = bytearray([
  0x01, 0x44, 0x44, 0x43, 0x01, 0x01, 0x01,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

_lut_24_bb_partial = bytearray([
  0x01, 0x04, 0x04, 0x03, 0x01, 0x01, 0x01,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

# Display resolution
EPD_WIDTH  = const(200)
EPD_HEIGHT = const(200)
EPD_ARRAY = const(5000)
MAX_X     = const(24)
MAX_Y     = const(199)

BUSY = const(0)  # 0=busy, 1=idle

NORMAL                             = const(0x1)
INVERTED                           = const(0x2)

UPDATE_FULL                        = const(0x0)
UPDATE_PART                        = const(0x1)

class EPD:
    def __init__(self, spi, cs = None, dc = None, rst= None, busy=None, refresh= UPDATE_FULL, orientation= NORMAL):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        if cs:
            self.cs.init(self.cs.OUT, value=0)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=1)
        if busy:
            self.busy.init(self.busy.IN)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self._hibernating = True
        self._power_is_on = False
        self._initial_refresh = True
        self._part_update_counter = 0
        self.set_frame_memory = self.set_frame_memory_full
        self.display_frame = self.display_frame_full
        self.update_mode = refresh
        self.set_update_mode(refresh)
        self.set_ram_area = self.set_ram_area_normal
        self.orientation = NORMAL
        self.initial_refresh = True
        self._using_partial_mode = False

    # set display update mode
    def set_update_mode(self, mode):
        if mode == self.update_mode:
            return
        if mode == UPDATE_FULL:
            self.set_frame_memory = self.set_frame_memory_full
            self.display_frame = self.display_frame_full
        elif mode == UPDATE_PART:
            self.set_frame_memory = self.set_frame_memory_part
            self.display_frame = self.display_frame_part
        self.update_mode = mode
        self.power_off()
        
    # send command and data(if any) to display
    def _command(self, command, data=None):
        if self.dc:
            self.dc(0)
        if self.cs:
            self.cs(0)
        self.spi.write(bytearray([command]))
        if self.cs:
            self.cs(1)
        if data is not None:
            self._data(data)
            
    # send data to display
    def _data(self, data):
        if self.dc:
            self.dc(1)
        if self.cs:
            self.cs(0)
        self.spi.write(data)
        if self.cs:
            self.cs(1)

    # wait for busy state or specified time
    def wait_until_idle(self, t= 2200):
        if self.busy:
            while self.busy.value() == BUSY:
                sleep_ms(10)
        else:
            while  t > 0:
                if self.busy:
                    if self.busy.value() != BUSY:
                        return
                sleep_ms(50)
                t = t - 50

    # hard reset display
    def reset(self):
        self.rst(0)
        sleep_ms(100)
        self.rst(1)
        sleep_ms(100)
        self._hibernating = False
        
    #Normal refresh initialization
    def init(self):
        self.reset()
        self._command(0x00, b'\xff\x0e');
        self._command(0x01, b'\x03\x09\x39\x39'); # power setting
        self._command(0x4D, b'\x55');
        self._command(0xaa, b'\x0f');
        self._command(0xE9, b'\x02');
        self._command(0xb6, b'\x11');
        self._command(0xF3, b'\x0a');
        self._command(0x06, b'\xc7\x0c\x0c') # boost soft start
        self._command(0x61, b'\xc8\x00\xc8')  #resolution setting// 200
        self._command(0x60, b'\x00') #// Tcon setting
        self._command(0x82, b'\x12') # VCOM DC setting
        self._command(0x30, b'\x3C'); # PLL control  // default 50Hz
        self._command(0X50, b'\x97'); # VCOM and data interval
        self._command(0XE3, b'\x00'); # power saving register // default

    def init_full(self):
        self.init()
        self._command(0x20);
        self._data(_lut_20_vcomDC)
        self._command(0x21);
        self._data(_lut_21_ww);
        self._command(0x22);
        self._data(_lut_22_bw)
        self._command(0x23);
        self._data(_lut_23_wb)
        self._command(0x24);
        self._data(_lut_24_bb)
        self.power_on()
        self._using_partial_mode = False

    def init_part(self):
        self.init()
        self._command(0x20);
        self._data(_lut_20_vcomDC_partial)
        self._command(0x21);
        self._data(_lut_21_ww_partial)
        self._command(0x22);
        self._data(_lut_22_bw_partial)
        self._command(0x23);
        self._data(_lut_23_wb_partial)
        self._command(0x24);
        self._data(_lut_24_bb_partial)
        self.power_on()
        self._using_partial_mode = True
    
    # set image pos on display Ram
    def set_ram_area_normal(self, x, y, w, h):
        xe = (x + w - 1) | 0x0007; # byte boundary inclusive (last byte)
        ye = y + h - 1;
        x =  x & 0xFFF8; # byte boundary
        self._command(0x90); # partial window
        self._data(bytes([x % 256,xe % 256]));
        self._data(bytes([0,y % 256]));
        self._data(bytes([0,ye % 256]));
        self._data('b\x00'); # don't see any difference

    # calc display coordinates
    def calc_coords(self, x, y, w, h):
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        x = x & 0xF8
        w = w & 0xF8
        if (x + w >= self.width):
            x_end = self.width - 1
        else:
            x_end = x + w - 1
        if (y + h >= self.height):
            y_end = self.height - 1
        else:
            y_end = y + h - 1
        return x, y, x_end, y_end
        
    # put an image in the frame memory for full refresh
    def set_frame_memory_full(self, image, x, y, w, h):
        self.init_full()
        self._command(0x13, image)
        self.display_frame_full()
        self._command(0x10, image)
        self.power_off()

    # put an image in part of the frame memory
    def set_frame_memory_part(self, image, x, y, w, h):
        if self._hibernating == True:
            self.set_frame_memory_full(image, x, y, w, h)
            return
        if self._using_partial_mode == False:
            self.init_part()
            self.clear_frame_memory()
        x, y, x_end, y_end = self.calc_coords(x, y, w, h)
        self._command(0x91); # partial in
        self._command(0x13, image)
        self.set_ram_area(x, y, x_end, y_end)
        self.display_frame_part()
        self._command(0x10, image)
        self._command(0x92); # partial out
        
    # replace the frame memory with the specified color
    def clear_frame_memory(self):
        self._command(0x91); # partial in
        self.set_ram_area(0, 0, self.width, self.height)
        self._command(0x13)
        # send the color data
        for i in range(5000):
            self._data(bytes([0xFF]))
        self.display_frame_part()
        self._command(0x10)
        for i in range(5000):
            self._data(bytes([0xFF]))
        self._command(0x92); # partial out

    # draw the current frame memory
    def display_frame_full(self):
        self._command(0x12)
        sleep_ms(10)
        self.wait_until_idle(1500)

    # draw part of the current frame memory
    def display_frame_part(self):
        self._command(0x12)
        sleep_ms(10)
        self.wait_until_idle(400)
     
    # power on display
    def power_on(self):
        if (self._power_is_on is False):
            self._command(0x04)
            sleep_ms(10)
            self.wait_until_idle(100)
            self._power_is_on = True

    # power off display
    def power_off(self):
        if (self._power_is_on):
            self._command(0x02)
            sleep_ms(10)
            self.wait_until_idle(100)
            self._power_is_on = False
            self._using_partial_mode = False

    # hibernate display - low power state
    # require active reset Pin to wake
    # to wake call reset() or init()
    def hibernate(self):
        self.power_off()
        if self.rst.value():
            self._command(0x07, b'\xA5')     #enter deep sleep
            sleep_ms(300)
            self.wait_until_idle(200)
            self._hibernating = True;
            
    # to wake call reset() or init()
    def sleep(self):
        self.hibernate()
        self.wait_until_idle(10)
        
    