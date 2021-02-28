
class Smooth:
    def __init__(self, n):
        self._values = []
        self.n = n
        
    #ut
    def add(self, val): 
        self._values.append(val)
        while len(self._values) > self.n:
            self._values.pop(0)
        sum = 0
        for val in self._values:
            sum += val
        sum = sum / len(self._values)
        return sum

    def reset(self):
        self._values = []