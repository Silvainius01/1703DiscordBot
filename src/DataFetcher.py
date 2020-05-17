import asyncio
import requests
import json
import os

saveDirectory = os.path.dirname(os.path.abspath(__file__)) + "\\testdata"
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

class DataFetcher:
    def fetchOutfitData(outfitTag:str, saveToDisk:bool):
        url = "{0}/outfit?alias={1}&c:resolve=member_character_name&c:resolve=member_online_status".format(baseRequestUrl, outfitTag)
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                outfitData = json.loads(response_text)
                if(saveToDisk):
                    saveDataToDisk(outfitData, saveDirectoryOutfit, outfitTag+".json")
                return {"status": True, "outfitData": outfitData.get("outfit_list")[0] }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
        return {"status":False}
    def fetchOutfitNameData(outfitName:str, saveToDisk:bool):
        url = "{0}/outfit?name={1}&c:resolve=member_character_name&c:resolve=member_online_status".format(baseRequestUrl, outfitName)
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                outfitData = json.loads(response_text)
                if(saveToDisk):
                    saveDataToDisk(outfitData, saveDirectoryOutfit, outfitName+".json")
                return {"status": True, "outfitData": outfitData.get("outfit_list")[0] }
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
            
    def fetchCharacterId(characterId:str, saveToDisk:bool):
        url = "{0}/character/?character_id={1}&c:resolve=outfit".format(baseRequestUrl, characterId)
        return DataFetcher.__fetchCharacter__(url, saveToDisk)
    def fetchCharacterName(characterName:str, saveToDisk:bool):
        url = "{0}/character/?name.first={1}&c:resolve=outfit".format(baseRequestUrl, characterName)
        return DataFetcher.__fetchCharacter__(url, saveToDisk)
    def __fetchCharacter__(url, saveToDisk:bool):
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                charData = json.loads(response_text).get("character_list")[0]
                if(saveToDisk):
                    charId = charData.get("character_id")
                    charName = charData.get("name").get("first")
                    saveDataToDisk(charData, saveDirectoryPlayer, "{0}_{1}.json".format(charName, charId))
                return {"status": True, "charData": charData }
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
    outfitNames = {}
    outfitFactionMap = {}

    def GetOutfitDataId(id):

        return
    def GetOutfitDataTag(tag:str):
        data = DataFetcher.fetchOutfitData(tag, True)
        if data["status"]:
            outfitData = data.get("outfitData")
            outfitId = outfitData.get("outfit_id")
            outfitName = outfitData.get("name")

            outfits[outfitId] = outfitData
            outfitNames[outfitName] = outfitId

            return outfitData.get("outfitData")
        return

    def GetOutfitIdFaction(id):
        return

class CharacterMetaData:
    charFactionMap = {}

    def GetCharIdFaction(id):
        factionId = CharacterMetaData.charFactionMap.get(id)
        if factionId == None:
            # Register character faction if not found
            factionId = DataFetcher.fetchCharacterIdFaction(id)
            if factionId.get("status"):
                factionId = factionId.get("faction_id")
                CharacterMetaData.charFactionMap[id] = factionId
            return "-1";
        return factionId

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