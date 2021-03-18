'''
Author: Gregor Holzner
Company: Tratter Engineering SRL September 2020
Website: www.monsterrhino.it, www.trattereng.com

BSD 3-Clause License

Copyright (c) 2021, 
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''


import time
from rpi_ws281x import *


class LED():
    """Handles the ws2811 LED
    """
    def __init__(self):
        self.LED_COUNT = 4  # Number of LED pixels.
        self.LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
        # LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
        self.LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        self.LED_DMA = 10  # DMA channel to use for generating signal (try 10)
        self.LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
        self.LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
        self.LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

    def init_led(self):
        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()

    def set_red_white(self):
        for i in range(4):
            self.strip.setPixelColor(i, Color(255, 0, 0))
            self.strip.show()
        for t in range(4, self.LED_COUNT):
            self.strip.setPixelColor(t, Color(255, 255, 255))
            self.strip.show()

    def set_green(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, Color(0, 255, 0))
            self.strip.show()

    def set_red(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, Color(255, 0, 0))
            self.strip.show()

    def set_blue(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, Color(0, 0, 255))
            self.strip.show()

    def set_purple(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, Color(128, 0, 128))
            self.strip.show()

    def set_orange(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, Color(255, 165, 0))
            self.strip.show()

    def set_orange_green_mix(self):
        for i in range(self.LED_COUNT):
            if i % 2 != 0:
                self.strip.setPixelColor(i, Color(230, 67, 0))
                self.strip.show()
            else:
                self.strip.setPixelColor(i, Color(0, 255, 0))
                self.strip.show()

    def set_orange_green_mix2(self):
        for i in range(self.LED_COUNT):
            if i % 2 != 0:
                self.strip.setPixelColor(i, Color(0, 255, 0))
                self.strip.show()
            else:
                self.strip.setPixelColor(i, Color(230, 67, 0))
                self.strip.show()
                
    def set_mix(self):
        self.strip.setPixelColor(0, Color(0, 255, 0))
        self.strip.show()
        self.strip.setPixelColor(1, Color(255, 0, 0))
        self.strip.show()
        self.strip.setPixelColor(2, Color(0, 0, 255))
        self.strip.show()
        self.strip.setPixelColor(3, Color(255, 255, 255))
        self.strip.show()

    def set_white(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, Color(255, 255, 255))
            self.strip.show()

    def switch_off(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
            self.strip.show()


# Main program logic follows:
if __name__ == '__main__':

    my_led = LED()
    my_led.init_led()
    
    my_led.set_orange_green_mix()
    print("Color 1")
    time.sleep(2)
    my_led.set_orange_green_mix2()
    print("Color 2")
    time.sleep(2)
    my_led.set_green()
    print("Color 3")
    time.sleep(2)
    my_led.set_blue()
    print("Color 4")
    time.sleep(2)
    my_led.set_red()
    print("Color 5")
    time.sleep(2)
    my_led.set_purple()
    print("Color 6")
    time.sleep(2)
    my_led.set_white()
    print("Color 7")
    time.sleep(2)
    my_led.set_mix()
    print("Color 8")
    time.sleep(2)
    my_led.switch_off()