
from TrackerBase import *

class EventFilter:
    def __init__(self, filterName, filterValue):
        self.filterName = filterName
        self.filterValue = filterValue
        return

    # Filter is triggered if value does not exist or does not match
    def FilterEvent(self, event):
        val = event.get(self.filterName)
        if val == None or val != self.filterValue:
            return True
        return False

class InverseEventFilter(EventFilter):
    def __init__(self, filterName, filterValue):
        return super().__init__(filterName, filterValue)

    # Filter is triggered if value exists AND matches
    def FilterEvent(self, event):
        return not super().FilterEvent(event)

class EventNameFilter(EventFilter):
    def __init__(self, filterName):
        return super().__init__(filterName, None)

    #Filter is triggered if value exists
    def FilterEvent(self, event):
        return event.get(self.filterName)

class InverseEventNameFilter(EventNameFilter):
    def __init__(self, filterName):
        return super().__init__(filterName)

    # Filter is triggered if value DOES NOT exist
    def FilterEvent(self, event):
        return not super().FilterEvent(event)

class DesolationZoneFilter(EventFilter):
    def __init__(self):
        self.desolationZones = []
        self.excludedZones = ["2","4","6","8","97","98","99"]
        return super().__init__("zone_id", None)

    # Filter triggers if it detects an instanced zone that is not Koltyr or Sanctuary
    def FilterEvent(self, event):
        zoneId = event.get("zone_id")
        worldId = event.get("world_id")
        # If we know it is desolation, dont trigger
        if zoneId in self.desolationZones:
            return False
        # If no zoneId is in the event or we know the ID isn't desolation, trigger.
        if zoneId == None or worldId == None or (zoneId in self.excludedZones):
            return True
        # If the zone is dynamic, determine if it is desolation. If not, trigger.
        isKoltyrDict = DataFetcher.isDynamicZoneKoltyr(worldId, zoneId)
        if isKoltyrDict.get("status") == False or isKoltyrDict.get("isKoltyr") == True:
            self.excludedZones.append(zoneId)
            return True
        self.desolationZones.append(zoneId) # If it makes it this far, cache zone id
        return False

class ExclusiveExperienceDescFilter(InverseEventFilter):
    def __init__(self, desc):
        self.desc = desc
        return super().__init__("experience_id", None)

    # Filter triggers if GainExperience event AND desc contains substring
    def FilterEvent(self, event):
        expId = event.get("experience_id")
        if expId != None:
            desc = ExpMetaData.GetDesc(expId)
            if expDesc.find(self.desc) > -1:
                return True
        return False

# Filter triggers if event is GainExperience and ID matches
class ExclusiveExperienceIdFilter(InverseEventFilter):
    def __init__(self, id):
        return super().__init__("experience_id", id)

class InclusiveExperienceDescFilter(EventFilter):
    def __init__(self, desc:str):
        self.desc = desc
        return super().__init__("event_name", "GainExperience")

    # Event triggers filter if:
    #   - It is NOT a GainExperience 
    #               OR
    #   - Its description contains the provided substring
    def FilterEvent(self, event):
        isExpEvent = super().FilterEvent(event)
        if isExpEvent:
            return True
        expId = event["experience_id"]
        expDesc = ExpMetaData.GetDesc(expId)
        if expDesc.find(self.desc) > -1:
            return True
        return False

class InclusiveExperienceIdFilter(EventFilter):
    def __init__(self, id:str):
        self.expId = id
        return super().__init__("event_name", "GainExperience")

    # Event triggers filter if:
    #   - It is NOT a GainExperience 
    #               OR
    #   - Its id matches the provided one
    def FilterEvent(self, event):
        return super().FilterEvent(event) or self.expId == event["experience_id"]

