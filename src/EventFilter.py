
from PsEventManager import *
from CharacterTracker import *
from DataFetcher import *
from web_sock import *

class EventFilter:
    def __init__(self, filterName, filterValue):
        self.filterName = filterName
        self.filterValue = filterValue
        return

    def FilterEvent(self, event):
        val = event.get(self.filterName)
        if val == None or val != self.filterValue:
            return True
        return False

class InverseEventFilter(EventFilter):
    def __init__(self, filterName, filterValue):
        return super().__init__(filterName, filterValue)
    def FilterEvent(self, event):
        return not super().FilterEvent(event)

class OutfitWarsFilter(EventFilter):
    def __init__(self):
        self.desolationZones = []
        self.excludedZones = ["2","4","6","8","97","98","99"]
        return super().__init__("zone_id", None)

    def FilterEvent(self, event):
        zoneId = event.get("zone_id")
        worldId = event.get("world_id")
        # Dont filter if we have cached this zone id
        if zoneId in self.desolationZones:
            return False
        # If no zoneId is in the event or we know the ID isn't desolation, discard.
        if zoneId == None or worldId == None or (zoneId in self.excludedZones):
            print("Not desolation: {0}".format(zoneId))
            return True
        # If the zone is dynamic, determine if it is desolation. If not, discard.
        isKoltyrDict = DataFetcher.isDynamicZoneKoltyr(worldId, zoneId)
        if isKoltyrDict.get("status") == False or isKoltyrDict.get("isKoltyr") == True:
            self.excludedZones.append(zoneId)
            print("Not desolation: {0} | isKolytr: {1}".format(zoneId, isKoltyrDict.get("isKoltyr")))
            return True
        self.desolationIds.append(zoneId) # If it makes it this far, cache zone id
        return False
