
import logging as lg

logger = lg.getLogger(__name__)
logger.setLevel(lg.INFO)

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
    def __init__(self, num_of_keys):
        self.queue = []
        self.keys = [0]*num_of_keys
        self.last =[0]*num_of_keys

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
            logger.info(f"MOCK_GET key {value} -> {key}")
            return event(value, key)

        return None

    def update(self, keys):
        self.keys = keys

class Keys:
    
    def __init__(self, *args, value_when_pressed=True, pull=False):
        self.key_list = [0]*len(args[0])
        self.pin_list = [x for x in args[0]]
        self.events = events(len(args[0]))

    def set(self, number, value):
        self.key_list[number] = value
        self.events.update(self.key_list)
        logger.info(f"SIMULATOR_SET key {number} set to {value}")
