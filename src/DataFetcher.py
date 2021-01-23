import asyncio
import requests
import json
import os

saveDirectory = os.path.dirname(os.path.abspath(__file__)) + "\\..\\testdata"
saveDirectoryOutfit = saveDirectory + "\\outfit"
saveDirectoryPlayer = saveDirectory + "\\player"
saveDirectoryDyZone = saveDirectory + "\\DynamicZone"

baseRequestUrl = "https://census.daybreakgames.com/s:17034223270/get/ps2:v2"

def saveDataToDisk(data, filePath:str, fileName:str):
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    response_serialized = json.dumps(data)
    dump_file = open(filePath+"\\"+fileName, "w")
    dump_file.write(response_serialized)
    dump_file.close()
    return
def CharacterNameOrIdUrl(nameOrId:str, ext:str):
    try:
        int(nameOrId)
        return "{0}/character/?character_id={1}{2}".format(baseRequestUrl, nameOrId, ext)
    except ValueError:
        return "{0}/character/?name.first={1}{2}".format(baseRequestUrl, nameOrId, ext)
    return

def ListToUrlArray(valueList):
    if valueList == None or not isinstance(valueList, list) or len(valueList) == 0:
        return ""
    strList = []
    for v in valueList:
        if isinstance(v, str):
            strList.append(v)
        else: strList.append(str(v))
    return ",".join(strList)
def ChunkList(lst, chunkSize):
    for i in range(0, len(lst), chunkSize):
        yield lst[i:i + chunkSize]

class DataFetcher:
    def fetchOutfitData(outfitTag:str, saveToDisk:bool):
        return DataFetcher.__fetchOutfit__("alias={0}".format(outfitTag), False, saveToDisk)
    def fetchOutfitIds(outfitIds):
        return DataFetcher.__fetchOutfit__("alias={0}".format(ListToUrlArray(outfitIds)), True, False)
    def fetchOutfitNameData(outfitName:str, saveToDisk:bool):
        return DataFetcher.__fetchOutfit__("name={0}".format(outfitName), False, saveToDisk)
    def fetchOutfitIdData(outfitId, saveToDisk:bool):
        return DataFetcher.__fetchOutfit__("outfit_id={0}".format(outfitId), False, saveToDisk)
    def __fetchOutfit__(urlAug, returnList:bool, saveToDisk:bool):
        url = "{0}/outfit?{1}&c:resolve=member_character_name&c:resolve=member_online_status".format(baseRequestUrl, urlAug)
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                outfitData = json.loads(response_text).get("outfit_list")
                if(saveToDisk):
                    outfit = outfitData[0]
                    saveDataToDisk(outfitData, saveDirectoryOutfit, "{0}_{1}.json".format(outfit["alias"], outfit["name"]))
                if not returnList:
                    return {"status": True, "outfitData": outfitData[0] }
                return {"status": True, "outfit_list": outfitData }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
        return {"status":False}

    def fetchOutfitMemberList(outfitTag:str, saveToDisk:bool):
        response = DataFetcher.fetchOutfitData(outfitTag, False)
        if response.get("status") == True:
            memberList = []
            members = response.get("outfitData").get("members")
            for member in members:
                memberList.append({ "name": member["name"]["first"], "id" : member["character_id"] })
            if(saveToDisk):
                saveDataToDisk(memberList, saveDirectoryOutfit, outfitTag+"_members.json")
            return memberList
        else:
            print("Error fetching outift data: ")
            print(response.get("exception"))
        return response
            
    def fetchCharacterId(charId:str, saveToDisk:bool):
        return DataFetcher.__fetchCharacter__("character_id={0}".format(charId), False, saveToDisk)
    def fetchCharacterName(charName:str, saveToDisk:bool):
        return DataFetcher.__fetchCharacter__("name.first={0}".format(charName), False, saveToDisk)
    def fetchCharacterIds(charIdList):
        urlAug = "character_id={0}".format(ListToUrlArray(charIdList))
        return DataFetcher.__fetchCharacter__(urlAug, True, False)
    def __fetchCharacter__(urlAug, returnList, saveToDisk:bool):
        url = "{0}/character/?{1}&c:resolve=outfit".format(baseRequestUrl, urlAug)
        try:
            response = requests.get(url)
            if(response.status_code == 200):
                response_text = response.text
                charData = json.loads(response_text).get("character_list")
                if(saveToDisk):
                    charDataT = charData[0]
                    charId = charDataT.get("character_id")
                    charName = charDataT.get("name").get("first")
                    saveDataToDisk(charDataT, saveDirectoryPlayer, "{0}_{1}.json".format(charName, charId))
                if not returnList:
                    return {"status": True, "charData": charData[0] }
                return {"status": True, "character_list": charData }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
        return {"status":False}

    def fetchCharacterIdFaction(id:str):
        url = "{0}/character/?character_id={1}&c:show=faction_id".format(baseRequestUrl, id)
        return DataFetcher.__fetchCharacterFaction__(url)
    def fetchCharacterNameFaction(name:str):
        url = "{0}/character/?name.first={1}&c:show=faction_id".format(baseRequestUrl, nameOrId)
        return DataFetcher.__fetchCharacterFaction__(url)
    def __fetchCharacterFaction__(url):
        try:
            response = requests.get(url)
            if(response.status_code == 200):
                response_text = response.text
                factionId = json.loads(response_text).get("character_list", ["-1"])[0].get("faction_id")
                return {"status": True, "faction_id": factionId }
        except Exception as exc:
            return {"status":False, "exception": exc}
        return {"status":False}
    
    def fetchExperienceDataList(saveToDisk:bool):
        url = "{0}/experience?c:limit=999999".format(baseRequestUrl)
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                expTypeData = json.loads(response_text)
                if(saveToDisk):
                    saveDataToDisk(expTypeData, saveDirectory, "ExpTypes.json")
                return {"status": True, "experience_list": expTypeData.get("experience_list") }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
        return {"status":False}

    def fetchDynamicZoneData(worldId:str, zoneId:str, saveToDisk:bool):
        url = "{0}/map/?world_id={1}&zone_ids={2}".format(baseRequestUrl, worldId, zoneId)
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                zoneData = json.loads(response_text)
                if zoneData.get("map_list").__len__() == 0:
                    return {"status":False}
                if(saveToDisk):
                    saveData = zoneData.get("map_list")[0]
                    saveDataToDisk(saveData, saveDirectory, "world{0}_{1}.json".format(worldId, zoneId))
                return {"status": True, "zoneData": zoneData.get("map_list")[0] }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
        return {"status":False}
    def isDynamicZoneKoltyr(worldId:str, zoneId:str):
        zoneData = DataFetcher.fetchDynamicZoneData(worldId, zoneId, False)
        if zoneData.get("status") == True:
            isKoltyr = len(zoneData.get("zoneData").get("Regions").get("Row")) == 9
            return {"status":True, "isKoltyr":isKoltyr}
        return {"status":False}

    def fetchVehicleDataList(saveToDisk:bool):
        url = "{0}/vehicle?c:limit=5000".format(baseRequestUrl)
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                data = json.loads(response_text)
                if(saveToDisk):
                    saveDataToDisk(data, saveDirectory, "VehicleTypes.json")
                return {"status": True, "vehicle_list": data.get("vehicle_list") }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
        return {"status":False}

class OutfitMetaData:
    outfits = {}
    outfitTagToId = {}
    outfitNameToId = {}

    def GetOutfit(id):
        try:
            return OutfitMetaData.outfits[id]
        except KeyError:
            data = DataFetcher.fetchOutfitIdData(id, False)
            if data["status"]:
                return OutfitMetaData.__RegisterOutfit__(data["outfitData"])
        print("Failed to get data for outfit {0}".format(id))
        return {}
    def GetOutfitFromTag(tag:str):
        try:
            id = OutfitMetaData.outfitTagToId[tag]
            return OutfitMetaData.outfits[id]
        except KeyError:
            data = DataFetcher.fetchOutfitData(tag, False)
            if data["status"]:
                return OutfitMetaData.__RegisterOutfit__(data["outfitData"])
        print("Failed to get data for outfit {0}".format(tag))
        return {}
    def GetOutfitFromName(name:str):
        try:
            id = OutfitMetaData.outfitNameToId[name]
            return OutfitMetaData.outfits[id]
        except KeyError:
            data = DataFetcher.fetchOutfitNameData(name, False)
            if data["status"]:
                return OutfitMetaData.__RegisterOutfit__(data["outfitData"])
        print("Failed to get data for outfit {0}".format(name))
        return {}

    def GatherOutfits(ids):
        """
            Gathers a set of outfits from the API and stores them. Returns a True on success and False on failure
        """
        result = True
        for idList in ChunkList(ids, 100):
            if not OutfitMetaData.__GatherOutfitTags__(idList):
                result = False
        return result
    def __GatherOutfits__(ids):
        outfitList = DataFetcher.fetchOutfitIds(ids)
        if not outfitList["status"]:
            return False
        outfitList = outfitList["outfit_list"]
        for outfitData in outfitList:
            outfitId = outfitData.get("outfit_id")
            OutfitMetaData.__RegisterOutfit__(outfitId, outfitData)
        return True

    def GetOutfitFaction(id):
        return OutfitMetaData.GetOutfit(id).get("faction_id", "-1")

    def __RegisterOutfit__(outfitData):
        outfitId = outfitData.get("outfit_id")
        outfitName = outfitData.get("name")
        outfitTag = outfitData.get("alias")

        OutfitMetaData.outfits[outfitId] = outfitData
        OutfitMetaData.outfitTagToId[outfitTag] = outfitId
        OutfitMetaData.outfitNameToId[outfitName] = outfitId

        outfitLeader = outfitData.get("leader_character_id")
        outfitFaction = CharacterMetaData.GetCharFaction(outfitLeader)
        OutfitMetaData.outfits[outfitId]["faction_id"] = outfitFaction
        return outfitData

class CharacterMetaData:
    charDataDict = {}
    charNameToId = {}
    invalidChars = { "0" : "-1" }

    def GetChar(id):
        """
            Get a character's data from API via id.
        """
        try:
            if not CharacterMetaData.invalidChars.get(id):
                return CharacterMetaData.charDataDict[id]
            return {}
        except KeyError:
            charData = DataFetcher.fetchCharacterId(id, False)
            if charData["status"]:
                return CharacterMetaData.__RegisterCharacter__(id, charData["charData"])
        print("Failed to fetch data for character {0}".format(id))
        return {}
    def GetCharFromName(name):
        try:
            id = CharacterMetaData.charNameToId[name]
            return CharacterMetaData.charDataDict[id]
        except KeyError:
            charData = DataFetcher.fetchCharacterName(name, False)
            if charData["status"]:
                id  = charData["charData"]["character_id"]
                return CharacterMetaData.__RegisterCharacter__(id, charData["charData"])
        print("Failed to fetch data for character {0}".format(name))
        return {}

    def GetChars(idList):
        """
        Returns a list character data. It will be in the same order as the input IDs.
        Invalid charIds will have empty dictionaries in their place.
        """
        if not CharacterMetaData.GatherChars(idList):
            print("Could not gather data on desired characters!")
            return []
        charList = []
        for id in idList:
            charList.append(charDataDict.get(id, {}))
        return charList

    def GatherChars(ids:list):
        """
            Gathers a set of ids from the API and stores them. Returns a True on success and False on failure
        """
        result = True
        for idList in ChunkList(ids, 100):
            if not CharacterMetaData.__GatherCharsInternal__(idList):
                result = False
        return result

    def __GatherCharsInternal__(ids:list):
        charList = DataFetcher.fetchCharacterIds(ids)
        if not charList["status"]:
            return False
        charList = charList["character_list"]
        for charData in charList:
            charId = charData.get("character_id")
            CharacterMetaData.__RegisterCharacter__(charId, charData)
        return True

    def CharsOnSameTeam(char1Id, char2Id):
        return CharacterMetaData.GetCharFaction(char1Id) == CharacterMetaData.GetCharFaction(char2Id)

    def GetCharFaction(id):
        return CharacterMetaData.GetChar(id).get("faction_id", "-1")
    def GetCharFactionFromName(name):
        return CharacterMetaData.GetCharFromName(name).get("faction_id", "-1")

    def GetCharOutfitId(charId):
        if charId == None:
            return None
        return CharacterMetaData.GetChar(charId).get("outfit", {}).get("outfit_id", None)

    def __RegisterCharacter__(id, charData):
        CharacterMetaData.charDataDict[id] = charData
        CharacterMetaData.charNameToId[id] = charData["name"]["first"]
        return charData

class ExpMetaData:
    experienceTypes = {
        "AllRepairs" : [],
        "InfantryKills" : "1",
        "Revive" : "7",
        "CortiumHarvest" : "674"
    }
    experienceDict = {}

    def __init__():
        ExpMetaData.experienceDict = ExpMetaData.__InitExperienceDict__()
        return

    def GetExp(expId):
        data = ExpMetaData.experienceDict.get(expId)
        if data == None:
            data = { 
                "experience_id": "{0}".format(expId),
                "description":"Unknown Exp Type {0}".format(expId),
                "xp": "0"
            }
            ExpMetaData.experienceDict[expId] = data
        return data
    def GetDesc(expId):
        return ExpMetaData.GetExp(expId).get("description")

    def __GetRawExperienceData__():
        print("Getting Experience Data from API...")
        expList = DataFetcher.fetchExperienceDataList(True)
        while not expList["status"]:
            print("Failed getting experience data. Retrying...")
            expList = DataFetcher.fetchExperienceDataList(True)
        return expList

    def __InitExperienceDict__():
        expDict = {}
        for expType in ExpMetaData.__GetRawExperienceData__().get("experience_list"):
            expDict[expType.get("experience_id")] = expType
            ExpMetaData.__AnalyzeExpType__(expType)
        print("Experience data retrieved.")
        return expDict

    def __AnalyzeExpType__(expData):
        id = expData.get("experience_id")
        desc = expData.get("description")

        if ExpMetaData.__CheckRepair__(id, desc): return
        return

    def __CheckRepair__(expId, expDesc):
        if expDesc.find("Repair") > -1:
            ExpMetaData.experienceTypes["AllRepairs"].append(expId)
            return True
        return False

class VehicleMetaData:
    airVehicles = []
    groundVehicles = []
    vehicleDict = {}

    def __init__():
        VehicleMetaData.vehicleDict = VehicleMetaData.__InitVehicleData__()
        return

    def GetVehicle(id):
        return VehicleMetaData.vehicleDict.get(id, {})
    def GetVehicleName(id):
        return VehicleMetaData.GetVehicle(id).get("name", {}).get("en", "UNKNOWN VEHICLE")

    def IsGroundVehicle(id):
        vtype = VehicleMetaData.GetVehicle(id).get("type_id", "")
        return vtype == "5" or vtype == "2"
    def IsAirVehicle(id):
        vtype = VehicleMetaData.GetVehicle(id).get("type_id", "")
        return vtype == "1"

    def __GetRawVehicleData__():
        print("Getting Vehicle Data from API...")
        vlist = DataFetcher.fetchVehicleDataList(True)
        while not vlist["status"]:
            print("Failed. Retrying...")
            vlist = DataFetcher.fetchVehicleDataList(True)
        return vlist["vehicle_list"]

    def __InitVehicleData__():
        vdict = {}
        for v in VehicleMetaData.__GetRawVehicleData__():
            vdict[v.get("vehicle_id")] = v
        print("Vehicle Data retrieved")
        return vdict
    
    def __AnalyzeVehicle__(vdata):
        id = vdata["vehicle_id"]

        if VehicleMetaData.IsAirVehicle(id): airVehicles.append(id)
        elif VehicleMetaData.IsGroundVehicle(id): groundVehicles.append(id)
        return

ExpMetaData.__init__()
VehicleMetaData.__init__()