
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

    def StartTracker(self, events = [], worlds = []):
        if self.isTracking:
            return
        self.websocket.setCharIds([])
        self.websocket.setEventNames(events)
        self.websocket.setWorlds(worlds)
        self.websocket.startListener()
        return

    def StopTracker(self):
        return

    def TrackOutfit(self, outfitTag:str):
        print("Fetching [{0}]'s data from API...".format(outfitTag))
        outfitData = DataFetcher.fetchOutfitData(outfitTag, True).get("outfitData")
        if outfitData != None:
            print("Adding data to tracker...")
            self.eventManager.tracker.AddTrackedObject(outfitData)
        else: print("No data found!")
        return
    def TrackOutfits(self, outfitTags:list):
        for tag in outfitTags:
            self.TrackOutfit(tag)
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
    def SetExpDescFilter(self, desc, mode):
        self.eventManager.SetExpDescFilter(desc, mode)
        return
    def SetExpIdFilter(self, id, mode):
        self.eventManager.SetExpIdFilter(id, mode)
        return

    def SetTrackerWriteSettings(self, interval, path, fileName):
        self.eventManager.writeEnabled = True
        self.eventManager.writeToDiskInterval = interval
        self.eventManager.writePath = path
        self.eventManager.sessionFileName = fileName
        return

class OpsTrackerCommandInterface(cmd.Cmd):
    validEventNames = [
        "AchievementEarned",
        "BattleRankUp",
        "Death",
        "ItemAdded",
        "SkillAdded",
        "VehicleDestroy",
        "GainExperience",
        "PlayerFacilityCapture",
        "PlayerFacilityDefend"
    ]

    def __init__(self):
        super(OpsTrackerCommandInterface, self).__init__(completekey = 'enter')
        self.tracker = OpsTracker()
        self.outfitWarsMode = False
        self.events = []
        self.worlds = []
        return

    def do_start(self, arg):
        #if self.outfitWarsMode:
            #self.do_listenfor("Death,VehicleDestroy,GainExperience")
            #self.do_setxpfilter("Repair,7,674")
            #self.tracker.SetOutfitWarsFilter()
        self.tracker.StartTracker(self.events)
        return

    def do_trackoutfit(self, arg):
        tags = arg.split(",")
        if len(tags) > 1:
            self.tracker.TrackOutfits(tags)
        else: self.tracker.TrackOutfit(arg)
        return

    def do_trackchar(self, arg):
        result = self.tracker.TrackCharacter(arg)
        print(result)
        return

    def do_setfilter(self, arg):
        args = arg.split(' ')
        if len(args) < 3:
            print("Command needs 3 arguments")
        vals = args[1].split(',')
        for v in vals:
            self.tracker.SetFilter(args[0], v, args[2])
            print("Set {2}clusive filter {0} = {1}".format(args[0], v, args[2]))
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
            self.do_listenfor("Death,VehicleDestroy,GainExperience")
            self.do_setxpfilter("Repair,7,674 in")
            self.do_setxpfilter("438,439 ex") # Exclude shield repair
        else:
            print("Disabled OW mode")
        return

    def do_listenfor(self, arg):
        args = arg.split(',');
        print("Listening for {0} events")
        self.events = args
        return

    def do_writesettings(self, arg):
        args = arg.split(' ')
        if len(args) != 3:
            print("Usage: [interval] [fileName] [filePath]")
            return
        interval = args[0]
        name = args[1]
        path = args[2]
        self.tracker.SetTrackerWriteSettings(interval, name, path)
        return
    
    def do_addworld(self, arg):
        try:
            if arg in self.worlds:
                return
            int(arg)
            self.worlds.append(arg)
            print("Listening to world {0}".format(arg))
        except: return
        return

    def do_listenfor(self, arg):
        args = arg.split(",")
        for name in args:
            if name in OpsTrackerCommandInterface.validEventNames and not (name in self.events):
                self.events.append(name)
                print("Listening for {0} events".format(name))
        return

    def do_setxpfilter(self, arg):
        args = arg.split(' ');
        types = args[0].split(',')
        mode = args[1] if len(args) >= 2 else "in"
        for xp in types:
            try:
                int(xp)
                self.tracker.SetExpIdFilter(xp, mode)
                print("Set {1}clusive XP filter for ID: {0}".format(xp, mode))
            except ValueError:
                self.tracker.SetExpDescFilter(xp, mode)
                print("Set {1}clusive XP filter for Desc: {0}".format(xp, mode))
        return

if __name__ == "__main__":
    interface = OpsTrackerCommandInterface()
    interface.cmdloop()

# trackoutfit SKL,PRAE,VKTZ,AODR,1TMI,2RAF,VCO,8SEC,KN1