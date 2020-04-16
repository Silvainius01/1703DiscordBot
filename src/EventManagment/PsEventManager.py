
class BasePsEvent:
    payload = ""
    service = ""
    type = ""

class EventManagerPS2:
    i = 0
    
    def AddEvent(event :BasePsEvent):
        return null