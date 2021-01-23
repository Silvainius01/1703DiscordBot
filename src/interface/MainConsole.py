
import cmd
import distutils
import json
from distutils import util
import asyncio
import threading

from src.PsEventManager import *
from src.DataFetcher import *
from src.web_sock import *

from src.trackers.TrackerBase import *
from src.trackers.CharacterTracker import *
from src.trackers.OutfitTracker import *
from src.trackers.OutfitWarsTracker import *

class ParsingError(Exception):
    def __init__(self, desc:str):
        self.desc = desc
        return super().__init__()

class CmdArgParser():
    def ParseArgument(argument:str):
        try:
            return CmdArgParser.__ParseArgument__(argument, ',', ' ', '\\')
        except ParsingError as exc:
            print(exc.desc)
        return []

    def __ParseArgument__(argument, arrayChar, splitChar, escapeChar):
        argList = []
        skipCharIndexs = []
        arrayArgs = []

        startIndex = 0
        currIndex = -1
        escape = False
        findEndQuote = False
        beginStartIndex = False
        isArray = False
        prevChar = None

        for c in argument:
            currIndex += 1
            
            if beginStartIndex:
                startIndex = currIndex
                beginStartIndex = False

            if c == escapeChar:
                escape = True
                skipCharIndexs.append(currIndex)
                continue
            if not escape:
                if c == arrayChar:
                    isArray = True
                elif c == '"':
                    findEndQuote = not findEndQuote
                    prevWasEndQuote = not findEndQuote

                    if not isArray:
                        if findEndQuote and prevChar != splitChar and prevChar != None:
                            raise ParsingError("Starting quotes must be at the start of an argument")
                        skipCharIndexs.append(currIndex)
                    elif findEndQuote and prevChar != arrayChar:
                        raise ParsingError("Starting quotes in arrays must come directly after array seperator")
                    
                elif not findEndQuote:
                    if c == splitChar:
                        if currIndex == 0:
                            skipCharIndexs.append(0)
                        else:
                            arg = CmdArgParser.__GetArg__(startIndex, currIndex, argument, isArray, skipCharIndexs)
                            argList.append(arg)
                            skipCharIndexs = []
                            isArray = False
                            beginStartIndex = True
                    elif prevChar == '"':
                        raise ParsingError("End quote must be at the end of an argument or array entry")
                escape = False
                prevChar = c
        
        if findEndQuote:
            raise ParsingError("No end quote found!")

        argList.append(CmdArgParser.__GetArg__(startIndex, len(argument), argument, isArray, skipCharIndexs))
        return argList

    def __GetArg__(startIndex, endIndex, argument, isArray, skipIndexList):
        arg = "".join((argument[i] if i not in skipIndexList else "") for i in range(startIndex, endIndex, 1))
        if isArray:
            isArray = False
            arg = CmdArgParser.__ParseArgument__(arg, None, ',', '\\')
        return arg;

class CommandExecutor:
    def __init__(self):
        self.isTracking = False
        self.eventManager = EventManagerPS2()
        self.eventManager.SetTracker(TrackerBase())
        self.eventGatherer = PsEventGatherer()
        self.threads = {}
        self.maxThreads = 2
        self.numProcessThreads = 0
        self.eventGatherer.addCallback(self.eventManager.ReceiveEvent)
        return

    def StartThread(self, threadName, func):
        if self.threads.get(threadName) != None:
            print("Thread already exists")
            return
        if len(self.threads) > self.maxThreads:
            return

        thread = threading.Thread(name=threadName,target=self.StartInfiniteLoop,args=(func,))
        self.threads[threadName] = thread
        thread.start()
        return
    def StartInfiniteLoop(self, func):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(func())
        return
    def StartEventProcessingThread(self):
        self.StartThread("ProcessThread{0}".format(self.numProcessThreads), self.eventGatherer.ProcessBuffer)
        self.numProcessThreads+=1
        return

    def StartTracker(self, events = [], worlds = []):
        if self.isTracking:
            return
        self.eventGatherer.setCharIds([])
        self.eventGatherer.setEventNames(events)
        self.eventGatherer.setWorlds(worlds)
        self.StartThread("SocketThread", self.eventGatherer.socketConnect)

        for i in range(len(self.threads), self.maxThreads):
            self.StartEventProcessingThread()
        return

    def StopTracker(self):
        return

    def TrackOutfit(self, outfitTag:str, addOnlineChars = True):
        print("Fetching outfit [{0}] from API...".format(outfitTag))
        outfitData = OutfitMetaData.GetOutfitFromTag(outfitTag)
        if not self.eventManager.tracker.AddTrackedObject(outfitData):
            print("Failed to add [{0}] to tracker".format(outfitTag))
            return False

        if addOnlineChars:
            onlineChars = []
            for mem in outfitData["members"]:
                if mem.get("online_status") != "0":
                    onlineChars.append(mem.get("character_id"))
            print("Fetching {0} online chars from API...".format(len(onlineChars)))
            CharacterMetaData.GatherChars(onlineChars)
        return True
    def TrackOutfits(self, outfitTags:list):
        for tag in outfitTags:
            if not self.TrackOutfit(tag, False):
                print("Failed to gather outfit [{0}] from API".format(name))
                time.sleep(2)
        onlineChars = []
        for tag in outfitTags:
            outfit = OutfitMetaData.GetOutfitFromTag(tag)
            for mem in outfit["members"]:
                if mem.get("online_status") != "0":
                    onlineChars.append(mem.get("character_id"))
        print("Fetching {0} online chars from API...".format(len(onlineChars)))
        CharacterMetaData.GatherChars(onlineChars)
        return
    def TrackOutfitName(self, name):
        print("Fetching outfit {0} from API...".format(name))
        outfitData = OutfitMetaData.GetOutfitFromName(name)
        if not self.eventManager.tracker.AddTrackedObject(outfitData):
            return False
        return True
    def TrackOutfitNames(self, names:list):
        failed = []
        for name in names:
            if not self.TrackOutfitName(name):
                failed.append("Failed to gather outfit {0} from API".format(name))
        return

    def TrackCharacter(self, characterName:str):
        print("Fetching {0}'s data from API...")
        char = CharacterMetaData.GetCharFromName(characterName)
        if not self.eventManager.AddTargetCharacter(charId, characterName):
            print("Failed to add character.")
        return

    def SetFilter(self, filterName, filterValue, filterMode):
        self.eventManager.SetFilter(filterName, filterValue, filterMode)
        return
    def SetInverseFilter(self, filterName, filterValue, filterMode):
        self.eventManager.SetInverseFilter(filterName, filterValue, filterMode)
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

    def SetTrackerWriteSettings(self, interval, fileName, path):
        self.eventManager.writeTrackerData = True
        self.eventManager.writeToDiskInterval = interval
        self.eventManager.writePath = "{0}\\{1}".format(path,fileName)
        self.eventManager.trackerDataFileName = "trackerData.json"
        self.eventManager.eventLogName = "eventlog.txt"
        self.eventManager.metaDataFileName = "metaData.json"
        self.eventManager.eventSinceWrite = self.eventManager.writeToDiskInterval
        return

    def TrackEventLog(self, file, allowGatherChars = True, printTrackerData:bool = False, printMetaData:bool = False, logEvents:bool = False):

        if allowGatherChars:
            print("Gathering unique chars in file...")
            charIds = {}
            for line in file.readlines():
                event = json.loads(line)
                charId = event.get("character_id")
                attackerId = event.get("attacker_character_id")
                if charId != None:
                    charIds[charId] = True
                if attackerId != None:
                    charIds[attackerId] = True
            charIds = list(charIds)
            print("Fetching data for {0} characters from API...".format(len(charIds)))
            CharacterMetaData.GatherChars(list(charIds))

        print("Running events through tracker...")
        self.eventManager.writeMetaData = printMetaData
        self.eventManager.writeTrackerData = printTrackerData
        self.eventManager.eventLoggingMode = logEvents

        file.seek(0)

        for i in range(self.maxThreads):
            self.StartEventProcessingThread()
        self.eventGatherer.RunEventLog(file)

        self.eventManager.writeMetaData = True
        self.eventManager.writeTrackerData = True
        self.eventManager.eventLoggingMode = True
        return

    def SetTracker(self, arg):
        switch = {
            "char": CharacterTracker,
            "outfit": OutfitTracker,
            "ow": OutfitWarsTracker,
            "owretro": RetroactiveOutfitWarsTracker
        }
        try:
            self.eventManager.SetTracker(switch[arg]())
        except ValueError:
            print("{0} is not a valid tracker type.".format(arg))

    def SetEventLoggingMode(self, argList):
        try:
            state = EventProcessState(int(argList[0]))
            self.eventManager.eventLoggingMode = state
            print("Logging {0} events".format(state.name))
            return
        except: pass
        try:
            state = EventProcessState[argList[0]]
            self.eventManager.eventLoggingMode = state
            print("Logging {0} events".format(state.name))
            return
        except: pass
        print("{0} is not a valid logging mode".format(argList[0]))
        return

class CommandInterface(cmd.Cmd):
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
        super(CommandInterface, self).__init__(completekey = 'enter')
        self.tracker = CommandExecutor()
        self.outfitWarsMode = False
        self.outfitWarsFilter = False
        self.events = []
        self.worlds = []
        self.trackerStarted = False
        return

    def do_start(self, arg):
        """
            Connects the eventGatherer, and begins processing events.
            You cannot alter the eventGatherer or change the tracker type after this command.
        """
        self.tracker.StartTracker(self.events, self.worlds)
        return

    def do_trackoutfit(self, arg):
        """
            Track an outfit via tag, fetces data from API, and sets up a filter for that event.
            Can only be run if an outfit tracker is enabled.
        """
        tags = arg.split(",")
        if len(tags) > 1:
            self.tracker.TrackOutfits(tags)
        else: self.tracker.TrackOutfit(arg)
        return
    def do_trackoutfitname(self, arg):
        """
            Start tracking an outfit via name. If spaces are needed, encapsulate in quotes
            Can only be run if an outfit tracker is enabled
        """
        names = arg.split(",")
        if len(names) > 1:
            self.tracker.TrackOutfits(names)
        else: self.tracker.TrackOutfitName(arg)
        return

    def do_trackchar(self, arg):
        """
            Start tracking a character via name. 
            Can only be run if a character tracker is enabled
        """
        result = self.tracker.TrackCharacter(arg)
        print(result)
        return

    def do_setfilter(self, arg):
        """
            Set a processor-level filter for events.
            Usage: [entryName] [entryValue] [ex/in]
            Run help setfilter for more information.
        """
        args = arg.split(' ')
        if len(args) < 3:
            print("Command needs 3 arguments")
        vals = args[1].split(',')
        for v in vals:
            self.tracker.SetFilter(args[0], v, args[2])
            print("Set {2}clusive filter {0} = {1}".format(args[0], v, args[2]))
        return
    def help_setfilter(self):
        print("Filters are effectively a KeyValuePair that must exist within the event received in order to be processed.")
        print("Filters come in two modes: exclusive and inclusive. Events must pass ALL exclusive filters, and pass at least ONE inclusive filter")
        print("Generally, most filters you would want to run can be set socket-level, so that the API does the filtering for you, and doesn't slow down your processing speed.")
        print("For example, a socket-level server filter can be set with the addworld command")
        print("Other filter commands include:")
        print("\t - setinversefilter: processor-level filter for events that contain a KVP, instead of ones that don't")
        print("\t - setxpfilter: processor-level filter specically for xp types")
        print("\t - setowfilter: Sets a special processor-level filter for events on desolation")
        print("\t - settypefilter: sets a socket-level filter for event types")
        print("\t - setworldfilter: sets a socket-level filter for servers")
        #print("\t - setzonefilter: sets a socket-level filter for zones")
        return

    def do_setinversefilter(self, arg):
        """
            Sets a filter for events that DO contain a KVP
            Usage: setinversefilter [key] [value] [ex/in]
        """
        args = arg.split(' ')
        if len(args) < 3:
            print("Command needs 2 arguments")
        self.tracker.SetInverseFilter(args[0], args[1], args[3])
        print("Excluding events with {0} = {1}".format(args[0], args[1]))
        return

    def do_setowfilter(self, arg):
        """
            Sets special filter for desolation events, and:
                - Listens for Death, VehicleDestroy, and GainExperience events
                - Filters for Repair, Revive, and Cortium Harvest xp
                - Excludes Shield Repair xp
        """
        if not self.outfitWarsMode:
            self.outfitWarsMode = True
            self.do_settypefilter("Death,VehicleDestroy,GainExperience")
            self.do_setxpfilter("Repair,7,674,53 in")
            self.do_setxpfilter("438,439 ex") # Exclude shield repair
        try:
            if not self.outfitWarsFilter and bool(util.strtobool(arg)):
                self.outfitWarsFilter = True
                self.tracker.SetOutfitWarsFilter()
                print("Exlcuding all non-Desolation events")
        except ValueError:
            print("arg must parse as boolean value.")
        return

    def do_writesettings(self, arg):
        args = arg.split(' ')
        if len(args) != 3:
            print("Usage: [interval] [fileName] [filePath]")
            return
        interval = args[0]
        name = args[1]
        path = args[2]

        try:
            self.tracker.SetTrackerWriteSettings(int(interval), name, path)
        except ValueError:
            print("interval must be integer!")
        return
    
    def do_setworldfilter(self, arg):
        try:
            if arg in self.worlds:
                return
            int(arg)
            self.worlds.append(arg)
            print("Listening to world {0}".format(arg))
        except: return
        return

    def do_settypefilter(self, arg):
        args = arg.split(",")
        for name in args:
            if name in CommandInterface.validEventNames and not (name in self.events):
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

    def do_setzonefilter(self, arg):
        return

    def do_setreconnect(self, arg):
        try:
            retry = int(arg)
            self.tracker.eventGatherer.maxRetry = retry
        except ValueError:
            print("must use valid integer")
        return
    
    def do_analyzelog(self, arg):
        if not os.path.exists(arg):
            print("File does not exist")
            return
        data = open(arg)
        self.tracker.TrackEventLog(data)
        return

    def do_parse(self, arg):
        argList = CmdArgParser.ParseArgument(arg)
        for x in argList:
            print(x)
        return 

    def do_settracker(self, arg):
        argList = CmdArgParser.ParseArgument(arg)
        if len(argList) == 0:
            return False
        elif not isinstance(argList, list):
            return False
        self.tracker.SetTracker(arg)
        return

    def do_setloggingmode(self, arg):
        """
            Sets what events are put in the event log. Only processed events are logged by default.
            Raw (0): All events from the websocket
            PreHashFilter (1): All filtered events, including duplicates
            PostHashFilter (2): Unique filtered events
            Processed (3): Events processed by and included in the tracking data
        """
        argList = CmdArgParser.ParseArgument(arg)
        if len(argList) == 0:
            return False
        self.tracker.SetEventLoggingMode(argList)
        return
        

if __name__ == "__main__":
    interface = CommandInterface()
    interface.cmdloop()

# EMERALD:
# setworldfilter 17
# setowfilter false
# setloggingmode 3
# settracker ow
# trackoutfit SKL,VCO,AODR,PRAE,8SEC,1TMI,VKTZ,KN1,2RAF
# start


# SOLTECH:
# trackoutfit HHzs,YLBT,CN0P,RAVE,RvnX,TCFB,3KDC,RWCN,BSNE
# trackoutfit 3KDC,RWCN,BSNE
# COBALT:
# trackoutfit VS,TRXF,BOIS,91AR,BROS,TRID,RE4,RMIS,URGE

# CONNERY:
# settracker owretro
# trackoutfit FEAR,CIK,0O,DGia,FooI,TWC2,R18,P1GS,DPSO
# analyzelog C:\Users\conno\Desktop\OW_Matches\connery_ow_eventlog.txt

# testing stuff
# settracker outfit
# trackoutfit SKL,VCO,AODR,PRAE,8SEC,1TMI,VKTZ,KN1,2RAF
# addworld 17
# start


# settracker outfit
# trackoutfit SHSK,xTMq
# setowfilter false
# setworldfilter 19