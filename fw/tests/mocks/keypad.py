
import logging as lg

class event:
    def __init__(self, num, state):
        self.key_number = num
        self.released = None
        self.pressed = None

        if(state == "released"):
            self.released = True
        elif(state == "pressed"):
            self.pressed = True

class events:
    def __init__(self):
        self.queue = []
        self.keys = [0, 0]
        self.last = [0, 0]

    def get(self):
        #refresh queue when its clear
        if len(self.queue) == 0:
            for n in range(len(self.keys)):
                if self.last[n] != self.keys[n]:
                    if self.keys[n]:
                        self.queue.append({"pressed": n})
                    else:
                        self.queue.append({"released": n})
                self.last[n] = self.keys[n]

        if self.queue:
            tmp = self.queue.pop(0)
            key, value =  next(iter(tmp.items()))
            return event(value, key)

        return None

    def update(self, keys):
        self.keys = keys

class Keys:
    
    def __init__(self, *args, value_when_pressed=True, pull=False):
        self.key_list = [0]*len(args[0])
        self.events = events()

    def set(self, number, value):
        self.key_list[number] = value
        self.events.update(self.key_list)

