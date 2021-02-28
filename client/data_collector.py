import time
from time import sleep
import threading
from random import uniform


class DataCollector:
    def __init__(self):
        self.mutex = threading.Lock()
        self.steps(250)
        self.reset()

    def add(self, val):
        v = (self.now(), val)
        self.mutex.acquire()
        self.values.append(v)
        self.mutex.release()
        #print("added: ")
        #print(v)

    def reset(self):
        self.mutex.acquire()
        self.values = []
        self.start_ms = self.get_ms()
        self.next_value_time = self.step_ms
        self.last_added_time = 0
        self.mutex.release()

    def steps(self, ms):
        self.step_ms = ms
        pass

    def get_ms(self):
        return round(time.time() * 1000)

    def now(self):
        return self.get_ms() - self.start_ms

    def get(self):
        ret = None
        sum = 0
        n = 0
        st = self.next_value_time
        ms = self.now()
        if ms >= self.next_value_time:
            self.mutex.acquire()
            #print("test")
            while len(self.values) > 0:
                #print("while %d" % len(self.values))
                v = self.values[0]
                if v[0] < self.next_value_time:
                    sum += v[1]
                    n += 1
                    self.values.pop(0)
                    #print("add %d" % n)
                else:
                    #print("finish %d" % n)
                    self.next_value_time += self.step_ms
                    break
            self.mutex.release()
        if n > 0:
            ret = (st, sum / n)
        return ret


"""
dc = DataCollector()


def generator_thread():
    while True:
        dc.add(uniform(1000,1200))
        sleep(uniform(0.1, 0.2))
    pass

serial_thread = threading.Thread(target=generator_thread)
serial_thread.start()

while True:
    sleep(0.1)
    v = dc.get()
    #print("read: ")
    if v:
        print(v)
"""        