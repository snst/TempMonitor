from machine import ADC
from machine import Pin
import time


class Smooth:
    def __init__(self):
        self._values = []
        
    def add(self, val, n): 
        self._values.append(val)
        while len(self._values) > n:
            self._values.pop(0)
        sum = 0
        for val in self._values:
            sum += val
        sum = sum / len(self._values)
        return sum

smooth = Smooth()

adc = ADC(Pin(32))
adc.atten(ADC.ATTN_6DB)
adc.width(ADC.WIDTH_12BIT)
 
while (True):
    val = adc.read()
    #val = smooth.add(val,30)
    print(val)
    time.sleep_ms(100)