import asyncio
import discord
import sys
from discord.ext.commands import Bot

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

class BotCommandValidation:
    client = discord.Client()

    userRestrictions = {
        'admin': []
        }
    roleRestrictions = {
        'admin' : []
        }
    channelRestrictions = {
        'admin': []
        }

    def __init__(self, botClient: discord.Client):
        self.client = botClient
        return

    async def __base_cmd_validation(self, context):
        if context.message.server == None:
            await self.client.say("I don't run commands from DM's")
            return False
        return True
    async def __base_dm_cmd_validation(self, context):
        return context.message.server == None

    async def __channel_cmd_validation(self, context, channelListName):
        if not await self.__base_cmd_validation(context):
            return False
        if context.message.channel in self.channelRestrictions[channelListName]:
            return True
        await self.client.say("This is not a valid channel for this commamd.")
        return False

    async def __role_cmd_validation(self, context, roleListName: str):
        if not await self.__base_cmd_validation(context):
            return False
        command_author = context.message.author
        for role in command_author.roles:
            if role in self.roleRestrictions[roleListName]:
                return True
        await self.client.say("You are not authorized to use this command.")
        return False
    async def __role_dm_cmd_validation(self, context, roleListName: str):
        if not await self.__base_dm_cmd_validation(context):
            return False
        
        auth = context.message.author
        for server in self.client.servers:
            mem = server.get_member(auth.id)
            if mem != None:
                for role in mem.roles:
                    if role in self.roleRestrictions[roleListName]:
                        return True

        await self.client.say("I don't run commands from DM's")
        return False

    async def __usercat_cmd_validation(self, context, userListName: str):
        if not await self.__base_cmd_validation(context):
            return False
        command_user = context.message.author
        if command_user in self.userRestrictions[userListName]:
            return True
        await self.client.say("You are not authorized to use this command.")
        return False
    async def __usercat_dm_cmd_validation(self, context, userListName: str):
        if not await self.__base_dm_cmd_validation(context):
            return False
        command_user = context.message.author
        if command_user in self.userRestrictions[userListName]:
            return True
        await self.client.say("You are not authorized to use this command.")
        return False

    async def __load_usercat_id(self, catname: str, id: int, server: discord.Server):
        user = None
        for mem in server.members:
            if int(mem.id) == id:
                user = mem
        if user == None:
            return
        await self.register_user(user, catname)
        return
    async def __load_rolecat_id(self, catname: str, id: int, server: discord.Server):
        role = None
        for r in server.roles:
            if int(r.id) == id:
                role = r
        if role == None:
            return
        await self.register_role(role, catname)
        return
    async def __load_channelcat_id(self, catname: str, id: int, server: discord.Server):
        channel = None
        for c in server.channels:
            if int(c.id) == id:
                channel = c
        if channel == None:
            return
        await self.register_channel(channel, catname)
        return
    async def __switch_catagory_mode(self, mode, catname, id, server: discord.Server):
        switch = {
            0: self.__load_usercat_id,
            1: self.__load_rolecat_id,
            2: self.__load_channelcat_id
            }
        await switch[mode](catname, id, server)
        return

    async def load_restrictions(self, server: discord.Server):
        saveFile = open(self.client.user.name + "_restrictions.txt", 'r')
        
        mode = 0
        catName = '';

        for line in saveFile:
            if not RepresentsInt(line):
                if line[0] == '\n':
                    mode += 1
                else:
                    catName = line.translate({ord(c): None for c in '\n'})
            else:
                id = int(line);
                await self.__switch_catagory_mode(mode, catName, id, server)
        return
    async def save_restrictions(self):
        msg = "";
        saveFile = open(self.client.user.name + "_restrictions.txt", 'w')

        # Save user restrictions/catagories
        for catagory, list in self.userRestrictions.items():
            msg += catagory + "\n"
            for user in list:
                msg += str(user.id) + "\n"
        msg += "\n"

        # Save role restrictions/catagories
        for roleType, list in self.roleRestrictions.items():
            msg += roleType + "\n"
            for role in list:
                msg += str(role.id) + "\n"
        msg += "\n"

        # Save channel restrictions/catagories
        for channelType, list in self.channelRestrictions.items():
            msg += channelType + "\n"
            for channel in list:
                msg += str(channel.id) + "\n"

        #msg += "\n"
        saveFile.write(msg)
        saveFile.close()
        print("saved restrictions")
        return

    #These are the commands that are used outside the class

    async def cmd_validation(self, context, allow_dm = False):
        if allow_dm and await self.__base_dm_cmd_validation(context):
            return True
        return await self.__base_cmd_validation(context)

    async def user_cmd_validation(self, context, userListName: str, allow_dm = False):
        if allow_dm and await self.__usercat_dm_cmd_validation(context, userListName):
            return True
        return await self.__usercat_dm_cmd_validation(context, userListName)

    async def role_cmd_validation(self, context, roleListName:str, allow_dm = False):
        if allow_dm and await self.__role_dm_cmd_validation(context, roleListName):
            return True
        return await self.__role_cmd_validation(context, roleListName)

    async def channel_cmd_validation(self, context, channelListName: str):
        if not channelListName in self.channelRestrictions:
            return False
        return await self.__channel_cmd_validation(context, channelListName)


    async def register_user(self, user: discord.User, userListName: str):
        userList = self.userRestrictions.get(userListName, [])
        userList.append(user)
        self.userRestrictions[userListName] = userList
        print("Registered @" + user.name + "(" + user.id + ") to " + userListName)
        return
    async def unregister_user(self, user: discord.User, userListName: str):
        if self.userRestrictions.get(userListName):
            if user in self.userRestrictions[userListName]:
                self.userRestrictions[userListName].remove(user)
                # Remove category if it is empty
                if len(self.userRestrictions[userListName]) <= 0:
                    self.userRestrictions.pop(userListName)
                return True
        return False
    async def delete_user_category(self, userListName):
        if self.userRestrictions.popitem(userListName) == None:
            return False
        return True

    async def register_channel(self, channel: discord.Channel, channelListName: str):
        channelList = self.channelRestrictions.get(channelListName, [])
        channelList.append(channel)
        self.channelRestrictions[channelListName] = channelList
        print("Registered #" + channel.name + "(" + channel.id + ") to " + channelListName)
        return
    async def unregister_channel(self, channel: discord.Channel, channelListName: str):
        if self.channelRestrictions.get(channelListName):
            if channel in self.channelRestrictions[channelListName]:
                self.channelRestrictions[channelListName].remove(channel)
                # Remove category if it is empty
                if len(self.channelRestrictions[channelListName]) <= 0:
                    self.channelRestrictions.pop(channelListName)
                return True
        return False
    async def delete_channel_category(self, channelListName):
        if self.channelRestrictions.popitem(channelListName) == None:
            return False
        return True

    async def register_role(self, role: discord.Role, roleListName: str):
        roleList = self.roleRestrictions.get(roleListName, [])
        roleList.append(role)
        self.roleRestrictions[roleListName] = roleList
        print("Registered role " + role.name + "(" + role.id + ") to " + roleListName)
        return
    async def unregister_role(self, role: discord.Role, roleListName: str):
        if self.roleRestrictions.get(roleListName):
            if role in self.roleRestrictions[roleListName]:
                self.roleRestrictions[roleListName].remove(role)
                # Remove category if it is empty
                if len(self.roleRestrictions[roleListName]) <= 0:
                    self.roleRestrictions.pop(roleListName)
                return True
        return False
    async def delete_role_category(self, roleListName):
        if self.roleRestrictions.popitem(roleListName) == None:
            return False
        return True

    def print_role_catagory(self, roleListName: str):
        if roleListName in self.roleRestrictions:
            msg = "Roles in \'"+roleListName+"\':\n"
            for role in self.roleRestrictions[roleListName]:
                msg += role.name + '\n'
            return msg
        return "There is no role catagory \'" + roleListName + "\'"

    def print_channel_catagory(self, channelListName: str):
        if channelListName in self.channelRestrictions:
            msg = "Channels in \'" + channelListName + "\':\n"
            for channel in self.channelRestrictions[channelListName]:
                msg += channel.mention + '\n'
            return msg
        return "There is no channel catagory \'" + channelListName + "\'"

    def print_user_catagory(self, userListName: str):
        if userListName in self.userRestrictions:
            msg = "Users in \'"+userListName+"\':\n"
            for user in self.userRestrictions[userListName]:
                msg += user.name + '\n'
            return msg
        return "There is no user catagory \'" + userListName + "\'"