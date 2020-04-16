import asyncio
import requests
import json

class DataFetcher:

    def fetchOutfitData(outfittag:str):
        dump_file_path = "C:/Users/User/Documents/whalewatcher/whalewatcher/"+outfittag+"_names.json"
        url = "https://census.daybreakgames.com/s:17034223270/get/ps2:v2/outfit?alias="+outfittag+"&c:resolve=member_character_name"
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                response_dict = json.loads(response_text)
                anus = namedtuple('nameList', response_dict.keys())(*response_dict.values)
                response_serialized = json.dumps(response_dict)
                try:
                    dump_file = open(dump_file_path, "w")
                    dump_file.write(response_serialized)
                    dump_file.close()
                    anus.get(anus.outfit_list[0]) #outfit info
                    
                    return {"status": True, "anus": (response_dict.keys)}

                    
                    
                except Exception as exc:
                    return {"status":False,"print": True, "exception":exc}

            else:
                raise BadStatus("Bad status code from request!")

        except BadStatus as exc:
                return {"status": False, "print": True, "exception": exc}


            

def bigGae():
    reply = DataFetcher.fetchOutfitData("1703")
    if (reply.get("status") == False):
        if (reply.get("print") == True):
            print(reply.get("exception"))

bigGae()