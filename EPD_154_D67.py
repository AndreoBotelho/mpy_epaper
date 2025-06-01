"""
MicroPython 1.54" Black/White GDEY0154D67 e-paper display driver
https://www.good-display.com/product/388.html
"""
from micropython import const
from time import sleep_ms
import ustruct

# Display resolution
EPD_WIDTH  = const(200)
EPD_HEIGHT = const(200)
EPD_ARRAY = const(5000)
MAX_X     = const(24)
MAX_Y     = const(199)

# Display commands
DRIVER_OUTPUT_CONTROL                = const(0x01)
BOOSTER_SOFT_START_CONTROL           = const(0x0C)
#GATE_SCAN_START_POSITION             = const(0x0F)
DEEP_SLEEP_MODE                      = const(0x10)
DATA_ENTRY_MODE_SETTING              = const(0x11)
SW_RESET                             = const(0x12)
READ_TEMPERATURE_SENSOR              = const(0x18)
TEMPERATURE_SENSOR_CONTROL           = const(0x1A)
MASTER_ACTIVATION                    = const(0x20)
#DISPLAY_UPDATE_CONTROL_1             = const(0x21)
DISPLAY_UPDATE_CONTROL_2             = const(0x22)
WRITE_RAM                            = const(0x24)
WRITE_RED_RAM                       = const(0x26)
WRITE_VCOM_REGISTER                  = const(0x2C)
WRITE_LUT_REGISTER                   = const(0x32)
SET_DUMMY_LINE_PERIOD                = const(0x3A)
SET_GATE_TIME                        = const(0x3B) # not in datasheet
BORDER_WAVEFORM_CONTROL              = const(0x3C)
SET_RAM_X_ADDRESS_START_END_POSITION = const(0x44)
SET_RAM_Y_ADDRESS_START_END_POSITION = const(0x45)
SET_RAM_X_ADDRESS_COUNTER            = const(0x4E)
SET_RAM_Y_ADDRESS_COUNTER            = const(0x4F)
TERMINATE_FRAME_READ_WRITE           = const(0xFF) # aka NOOP
BUSY = const(1)  # 1=busy, 0=idle
NORMAL                             = const(0x1)
INVERTED                           = const(0x2)
UPDATE_FULL                        = const(0x0)
UPDATE_PART                        = const(0x1)
UPDATE_FAST                        = const(0x2)

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
        self._init_display_done = False
        self._hibernating = True
        self._power_is_on = False
        self._initial_refresh = True
        self._part_update_counter = 0
        self.init = self.init_full
        self.set_frame_memory = self.set_frame_memory_full
        self.display_frame = self.display_frame_full
        self.update_mode = refresh
        self.set_update_mode(refresh)
        self.set_ram_area = self.set_ram_area_normal
        self.orientation = NORMAL

    def set_update_mode(self, mode):
        if mode == UPDATE_FULL:
            self.init = self.init_full
            self.set_frame_memory = self.set_frame_memory_full
            self.display_frame = self.display_frame_full
        elif mode == UPDATE_PART:
            self.init = self.init_part
            self.set_frame_memory = self.set_frame_memory_part
            self.display_frame = self.display_frame_part
        elif mode == UPDATE_FAST:
            self.init = self.init_fast
            self.set_frame_memory = self.set_frame_memory_fast
            self.display_frame = self.display_frame_fast
            
    def set_orientation(self, ori):
        if ori == NORMAL:
            self.set_ram_area = self.set_ram_area_normal
        else:
            self.set_ram_area = self.set_ram_area_inverted
        self.orientation = ori
        
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

    def _data(self, data):
        if self.dc:
            self.dc(1)
        if self.cs:
            self.cs(0)
        self.spi.write(data)
        if self.cs:
            self.cs(1)

    def wait_until_idle(self, t= 2200):
        while  t > 0:
            if self.busy:
                if self.busy.value() != BUSY:
                    return
            sleep_ms(50)
            t = t - 50

    def reset(self):
        self.rst(0)
        sleep_ms(200)
        self.rst(1)
        sleep_ms(20)
       
    #Normal refresh initialization
    def init_full(self):
        self.reset()
        sleep_ms(10)
        self._command(SW_RESET)
        sleep_ms(100)
        self.power_on()
        self._command(DRIVER_OUTPUT_CONTROL,  b'\xC7\x00\x00')
        self._command(DATA_ENTRY_MODE_SETTING,  b'\x01')
        self._command(SET_RAM_X_ADDRESS_START_END_POSITION,  b'\x00\x24')
        self._command(SET_RAM_Y_ADDRESS_START_END_POSITION,  b'\x00\x00\xC7\x00')
        self._command(BORDER_WAVEFORM_CONTROL,  b'\x05')
        self._command(READ_TEMPERATURE_SENSOR,  b'\x80')
        self._command(SET_RAM_X_ADDRESS_COUNTER,  b'\x00')
        self._command(SET_RAM_Y_ADDRESS_COUNTER,  b'\xC7\x00')
        self._command(DATA_ENTRY_MODE_SETTING, b'\x03')
        self._init_display_done = True
        
    #partial refresh initialization
    def init_part(self):
        if self._init_display_done:
            return
        self.reset()
        sleep_ms(10)
        self._command(SW_RESET)
        sleep_ms(10)
        self.power_on()
        self._command(DRIVER_OUTPUT_CONTROL,  b'\xC7\x00\x00')
        self._command(DATA_ENTRY_MODE_SETTING,  b'\x01')
        self._command(BORDER_WAVEFORM_CONTROL,  b'\x05')
        self._command(READ_TEMPERATURE_SENSOR,  b'\x80')
        #self.set_ram_area(0, 0, EPD_WIDTH, EPD_HEIGHT)
        self._command(DATA_ENTRY_MODE_SETTING, b'\x03')
        self._init_display_done = True

    #Fast refresh initialization
    def init_fast(self):
        self.reset()
        sleep_ms(10)
        self._command(SW_RESET)
        sleep_ms(10)
        self.wait_until_idle(50)
        self.power_on()
        self._command(READ_TEMPERATURE_SENSOR,  b'\x80')
        self._command(DISPLAY_UPDATE_CONTROL_2,  b'\xB1')
        self._command(MASTER_ACTIVATION)
        self.wait_until_idle(50)
        self._command(TEMPERATURE_SENSOR_CONTROL,  b'\x5A\x00')
        self._command(DISPLAY_UPDATE_CONTROL_2,  b'\x91')
        self._command(MASTER_ACTIVATION)
        self.wait_until_idle(50)
        self._command(DATA_ENTRY_MODE_SETTING, b'\x03')
        self._init_display_done = True
    
    def set_ram_area_normal(self, x, y, w, h):
        self._command(DATA_ENTRY_MODE_SETTING, b'\x03')
        self._command(SET_RAM_X_ADDRESS_START_END_POSITION)
        self._data(bytes([x // 8]))
        self._data(bytes([(x + w - 1) // 8]))
        self._command(SET_RAM_Y_ADDRESS_START_END_POSITION)
        self._data(bytes([int(y % 256),0]))
        self._data(bytes([int((y + h - 1) % 256),0]))
        self._command(SET_RAM_X_ADDRESS_COUNTER)
        self._data(bytes([x // 8]))
        self._command(SET_RAM_Y_ADDRESS_COUNTER)
        self._data(bytes([int(y % 256),0]))
        
    def set_ram_area_inverted(self, x, y, w, h):
        self._command(DATA_ENTRY_MODE_SETTING, b'\x00')
        self._command(SET_RAM_X_ADDRESS_START_END_POSITION)
        self._data(bytes([MAX_X - (x // 8)]))
        self._data(bytes([MAX_X - ((x + w - 1) // 8)]))
        self._command(SET_RAM_Y_ADDRESS_START_END_POSITION)
        self._data(bytes([MAX_Y - (int(y % 256)),0]))
        self._data(bytes([MAX_Y - (int((y + h - 1) % 256)),0]))
        self._command(SET_RAM_X_ADDRESS_COUNTER)
        self._data(bytes([MAX_X - (x // 8)]))
        self._command(SET_RAM_Y_ADDRESS_COUNTER)
        self._data(bytes([MAX_Y - (int(y % 256)),0]))

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
        
    # put an image in the frame memory
    def set_frame_memory_full(self, image, x, y, w, h):
        self.init()
        x, y, x_end, y_end = self.calc_coords(x, y, w, h)
        self.set_ram_area(x, y, x_end, y_end)
        self._command(WRITE_RAM, image)

    # put an image in the frame memory
    def set_frame_memory_part(self, image, x, y, w, h):
        self.init()
        x, y, x_end, y_end = self.calc_coords(x, y, w, h)
        self._command(BORDER_WAVEFORM_CONTROL, b'\x80')
        self.set_ram_area(x, y, x_end, y_end)
        self._command(WRITE_RAM, image)
        
    # put an image in the frame memory
    def set_frame_memory_fast(self, image, x, y, w, h):
        self.init()
        x, y, x_end, y_end = self.calc_coords(x, y, w, h)
        self.set_ram_area(x, y, x_end, y_end)
        self._command(WRITE_RAM, image)
        self._command(WRITE_RED_RAM)
        for i in range(len(image)):
            self._data('\x00')

    # replace the frame memory with the specified color
    def clear_frame_memory(self, color):
        self.set_ram_area(0, 0, self.width, self.height)
        self._command(WRITE_RAM)
        # send the color data
        for i in range(0, self.width // 8 * self.height):
            self._data(color)

    def refresh(self, x, y, w, h):
        if (self._initial_refresh):
            self._initial_refresh = False
            return self.display_frame()
        w1 =  w + x if x < 0 else w # reduce
        h1 =  h + y if y < 0 else h # reduce
        x1 =  0 if x < 0 else x # limit
        y1 =  0 if y < 0 else y # limit
        w1 =  w1 if x1 + w1 < EPD_WIDTH else EPD_WIDTH - x1 # limit
        h1 =  h1 if y1 + h1 < EPD_HEIGHT else EPD_HEIGHT - y1 # limit
        if ((w1 <= 0) or (h1 <= 0)):
            return; 
        # make x1, w1 multiple of 8 
        w1 += x1 % 8;
        if (w1 % 8 > 0):
            w1 += 8 - w1 % 8
        x1 -= x1 % 8;
        self.set_ram_area(x1, y1, w1, h1)
        self.display_frame()

    # draw the current frame memory and switch to the next memory area
    def display_frame_full(self):
        self._command(DISPLAY_UPDATE_CONTROL_2, b'\xF7')
        self._command(MASTER_ACTIVATION)
        self._command(TERMINATE_FRAME_READ_WRITE)
        self.wait_until_idle(2200)
    
    # draw fast the current frame memory
    def display_frame_fast(self):
        self._command(DISPLAY_UPDATE_CONTROL_2, b'\xC7')
        self._command(MASTER_ACTIVATION)
        self._command(TERMINATE_FRAME_READ_WRITE)
        self.wait_until_idle(1100)
        self.power_off()
        
    def display_frame_part(self):
        self._command(DISPLAY_UPDATE_CONTROL_2, b'\xFF')
        self._command(MASTER_ACTIVATION)
        self._command(TERMINATE_FRAME_READ_WRITE)
        self.wait_until_idle(300)
     
    def power_on(self):
        if (self._power_is_on is False):
            self._command(DISPLAY_UPDATE_CONTROL_2,b'\xE0')
            self._command(MASTER_ACTIVATION)
            self.wait_until_idle(100)
        self._power_is_on = True

    def power_off(self):
        if (self._power_is_on):
            self._command(DISPLAY_UPDATE_CONTROL_2, b'\x83')
            self._command(MASTER_ACTIVATION)
            self.wait_until_idle(150)
        self._power_is_on = False
        self._using_partial_mode = False
        
    # to wake call reset() or init()
    def hibernate(self):
        self.power_off()
        if self.rst.value():
            self._command(DEEP_SLEEP_MODE, b'\x01')     #enter deep sleep
            self._hibernating = True;
            self._init_display_done = False
            
    # to wake call reset() or init()
    def sleep(self):
        self.hibernate()
        self.wait_until_idle(10)
      
