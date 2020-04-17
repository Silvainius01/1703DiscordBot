import asyncio
import requests
import json
import os

def saveDataToDisk(data, filePath:str, fileName:str):
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    response_serialized = json.dumps(data)
    dump_file = open(filePath+"\\"+fileName, "w")
    dump_file.write(response_serialized)
    dump_file.close()

class DataFetcher:
    def fetchOutfitData(outfittag:str, saveToDisk:bool):
        url = "https://census.daybreakgames.com/s:17034223270/get/ps2:v2/outfit?alias="+outfittag+"&c:resolve=member_character_name"
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                outfitData = json.loads(response_text)
                if(saveToDisk):
                    saveDataToDisk(outfitData, "..\\testdata\\outfit\\"+outfittag+".json")
                return {"status": True, "outfitData": outfitData.get("outfit_list")[0] }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
                return {"status": False, "print": True, "exception": exc}

    def fetchOutfitMemberList(outfitTag:str, saveToDisk:bool):
         response = DataFetcher.fetchOutfitData(outfitTag, False)
         if response.get("status") == True:
            memberList = []
            members = response.get("outfitData").get("members")
            for member in members:
                memberList.append([member["name"]["first"], member["character_id"]])
            if(saveToDisk):
                path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\testdata\\outfit"
                saveDataToDisk(memberList, path, outfitTag+"_members.json")
            return memberList
         else:
            print("Error fetching outift data: ")
            print(response.get("exception"))
            return response

def bigGae():
    reply = DataFetcher.fetchOutfitMemberList("1703", True)
    #if (reply.get("status") == False):
    #    if (reply.get("print") == True):
    #        print(reply.get("exception"))
    print(reply)
bigGae()