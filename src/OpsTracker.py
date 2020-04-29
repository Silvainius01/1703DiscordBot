
import cmd
from PsEventManager import *
from CharacterData import *
from DataFetcher import *
from web_sock import *

class OpsTracker:
    def __init__(self):
        self.isTracking = False
        self.eventManager = EventManagerPS2()
        self.websocket = PS2_WebSocket_Listener([self.eventManager.ReceiveEvent])
        return

    def StartTracker(self):
        if self.isTracking:
            return

        self.isTracking = True
        self.websocket.startListener(list(self.eventManager.targetChars.keys()))
        return

    def StopTracker(self):
        return

    def TrackOutfit(self, outfitTag:str):
        members = DataFetcher.fetchOutfitMemberList(outfitTag, False)
        for member in members:
            self.eventManager.AddTargetCharacter(member.get("id"), member.get("name"))
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

class OpsTrackerCommandInterface(cmd.Cmd):

    def __init__(self):
        super(OpsTrackerCommandInterface, self).__init__(completekey = 'enter')
        self.tracker = OpsTracker()
        return

    def do_start(self, arg):
        self.tracker.StartTracker()
        return

    def do_trackoutfit(self, arg):
        self.tracker.TrackOutfit(arg)
        return

    def do_trackchar(self, arg):
        result = self.tracker.TrackCharacter(arg)
        print(result)
        return

if __name__ == "__main__":
    interface = OpsTrackerCommandInterface()
    interface.cmdloop()