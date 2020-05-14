
import cmd
from PsEventManager import *
from CharacterTracker import *
from OutfitTracker import *
from DataFetcher import *
from web_sock import *

class OpsTracker:
    def __init__(self):
        self.isTracking = False
        self.eventManager = EventManagerPS2()
        self.eventManager.SetTracker(OutfitTracker())
        self.websocket = PS2_WebSocket_Listener([self.eventManager.ReceiveEvent])
        return

    def StartTracker(self):
        if self.isTracking:
            return
        self.isTracking = True
        self.websocket.startListener(None, ["Death","VehicleDestroy","GainExperience","PlayerFacilityCapture","PlayerFacilityDefend"])
        # ["AchievementEarned","BattleRankUp","Death","ItemAdded","SkillAdded","VehicleDestroy","GainExperience","PlayerFacilityCapture","PlayerFacilityDefend"]
        return

    def StopTracker(self):
        return

    def TrackOutfit(self, outfitTag:str):
        print("Fetching data from API...")
        outfitData = DataFetcher.fetchOutfitData(outfitTag, True).get("outfitData")
        if outfitData != None:
            print("Adding data to tracker...")
            self.eventManager.tracker.AddTrackedObject(outfitData)
        else: print("No data found!")
        return

    def TrackCharacter(self, characterName:str):
        char = DataFetcher.fetchCharacterName(characterName, True)
        if char.get("status"):
            charId = char.get("charData").get("character_id")
            if not self.eventManager.AddTargetCharacter(charId, characterName):
                print("Failed to add character")
        else:
            print("Failed to fetch character")
        return

    def SetFilter(self, filterName, filterValue, filterMode):
        self.eventManager.SetFilter(filterName, filterValue, filterMode)
        return
    def SetOutfitWarsFilter(self):
        self.eventManager.SetOutfitWarsFilter()
        return

class OpsTrackerCommandInterface(cmd.Cmd):

    def __init__(self):
        super(OpsTrackerCommandInterface, self).__init__(completekey = 'enter')
        self.tracker = OpsTracker()
        self.outfitWarsMode = False
        return

    def do_start(self, arg):
        if self.outfitWarsMode:
            self.tracker.SetOutfitWarsFilter()
        self.tracker.StartTracker()
        return

    def do_trackoutfit(self, arg):
        self.tracker.TrackOutfit(arg)
        return

    def do_trackchar(self, arg):
        result = self.tracker.TrackCharacter(arg)
        print(result)
        return

    def do_setfilter(self, arg):
        args = arg.split(' ')
        if len(args) < 3:
            print("Command needs 3 arguments")
        self.tracker.SetFilter(args[0], args[1], args[2])
        print("Excluding events without {0} = {1}".format(args[0], args[1]))
        return

    def do_setinversefilter(self, arg):
        args = arg.split(' ')
        if len(args) < 2:
            print("Command needs 2 arguments")
        self.tracker.SetFilter(args[0], args[1])
        print("Excluding events with {0} = {1}".format(args[0], args[1]))
        return

    def do_trackow(self, arg):
        self.outfitWarsMode = not self.outfitWarsMode
        if self.outfitWarsMode:
            print("Exlcuding all non-Desolation events")
        else:
            print("Disabled OW mode")
        return

if __name__ == "__main__":
    interface = OpsTrackerCommandInterface()
    interface.cmdloop()