class MedianFilter:
    def __init__(self):
        self.values = []

    def add(self, val):
        self.values.append(val)

    def get(self):
        ret = 0
        l = len(self.values) 
        if l > 0:
            v = self.values.sort()
            ret = self.values[int(l/2)]
            self.values.clear()
        return ret


"""
m = MedianFilter()
m.add(7)
m.add(3)
m.add(5)
m.add(4)
m.add(9)

print(m.get())
"""