import asyncio
import discord
import sys
from discord.ext.commands import Bot
from discord.ext.commands import Context

class CommandRestrictions:
    def __init__(self, allow_dm: bool):
        self.userRestrictionCategories = set()
        self.roleRestrictionCategories = set()
        self.channelRestrictionCategories = set()
        self.allow_dm = allow_dm
        return

    def __switch_restriction_set(self, name: str):
        """
        Returns a restriction dict based on a provided string.
        Throws an error for invalid restriction types
        """
        switch = {
            "user": self.userRestrictionCategories,
            "role": self.roleRestrictionCategories,
            "channel": self.channelRestrictionCategories
        }
        return switch[name]

    def __add_category(self, setName: str, categoryName: str):
        restrictionSet = self.__switch_restriction_set(setName)
        added = not (categoryName in restrictionSet)
        restrictionSet.add(categoryName)
        return added
    def __remove_category(self, setName: str, categoryName: str):
        restrictionSet = self.__switch_restriction_set(setName)
        removed = (categoryName in restrictionSet)
        restrictionSet.discard(categoryName)
        return removed

    def add_user_category(self, categoryName: str):
        return self.__add_category("user", categoryName)
    def remove_user_category(self, categoryName: str):
        return self.__remove_category("user", categoryName)
    
    def add_role_category(self, categoryName: str):
        return self.__add_category("role", categoryName)
    def remove_role_category(self, categoryName: str):
        return self.__remove_category("role", categoryName)
    
    def add_channel_category(self, categoryName: str):
        return self.__add_category("channel", categoryName)
    def remove_channel_category(self, categoryName: str):
        return self.__remove_category("channel", categoryName)
    pass

# Handles a server's restrictions for users, roles, and channels.
# It also contains the desired error messages for when a command doesnt pass validation
class GuildCommandRestrictions:
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        self.commandRestrictions = dict()
        self.userRestrictions = dict()
        self.roleRestrictions = dict()
        self.channelRestrictions = dict()
        self.channelErrorMsg = "This is not a valid channel for this command."
        self.roleErrorMsg = "You are not authorized to use this command."
        self.userErrorMsg = "You are not authorized to use this command."
        return

    def __switch_restriction_type(self, categoryType):
        """
        Returns a restriction dict based on a provided string.
        Throws an error for invalid restriction types
        """
        switch = {
            "user": self.userRestrictions,
            "role": self.roleRestrictions,
            "channel": self.channelRestrictions
        }
        return switch[categoryType]

    def __add_restriction(self, restrictionType: str, object, categoryName: str):
        """
        Adds an object to a given category within a restriction type.
        If that type doesnt contain a given set, the set will be created.
        Returns true if the object was added.
        """
        category = self.__switch_category(restrictionType)
        categorySet = category.get(categoryName)
        if categorySet == None:
            categorySet = set()
            category[categoryName] = categorySet
        objectAdded = not (object in categorySet)
        categorySet.add(object)
        return objectAdded

    def __remove_restriction(self, restrictionType: str, object, categoryName: str):
        """
        Removes an object from a given category within a restriction type.
        Will delete a category if no more entries exist in it.
        Returns true if the object was removed.
        """
        category = self.__switch_category(restrictionType)
        categorySet = category.get(categoryName)
        if categorySet == None:
            return False
        objectRemoved = object in categorySet
        categorySet.discard(object)
        if len(categorySet) == 0:
            category.pop(categoryName)
        return objectRemoved

    def check_restrictions(self, context: Context, commandName: str):
        commandRestrictions = self.get_command_restrictions(commandName)
        
        if context.guild == None:
            return allow_dm

        # Is a valid user if no restrictions in place, or belongs to at least one of the categories.
        validUser = len(commandRestrictions.userRestrictionCategories) == 0
        if not validUser:
            for category in set.intersection(commandRestrictions.userRestrictionCategories, set(self.userRestrictions.keys)):
                validUser |= context.author.id in self.userRestrictions[category]

        # User has valid roles if no role restrictions in place, or has at least one beloning in required categories
        validRole = len(commandRestrictions.roleRestrictionCategories) == 0
        if not validRole:
            memberRoles = set([role.id for role in context.author.roles])
            for category in set.intersection(commandRestrictions.roleRestrictionCategories, set(self.roleRestrictions.keys)):
                roleInCategory = set.intersection(memberRoles, self.roleRestrictions[category])
                validRole |= len(rolesInCategory) > 0

        # Channel is valid if no restrictions in place, or exists in at least once category
        validChannel = len(commandRestrictions.channelRestrictionCategories) == 0
        if not validChannel:
            for category in set.intersection(commandRestrictions.channelRestrictionCategories, set(self.channelRestrictions.keys)):
                validChannel |= context.channel.id in self.channelRestrictions[category]

        return validUser and validRole and validChannel

    def add_user_restriction(self, user: discord.User, categoryName: str):
        return self.__add_restriction("user", user.id, categoryName)
    def remove_user_restriction(self, user: discord.User, categoryName: str):
        return self.__remove_restriction("user", user.id, categoryName)

    def add_role_restriction(self, role: discord.Role, categoryName: str):
        return self.__add_restriction("role", role.id, categoryName)
    def remove_role_restriction(self, role: discord.Role, categoryName: str):
        return self.__remove_restriction("role", role.id, categoryName)

    def add_channel_restriction(self, channel: discord.TextChannel, categoryName: str):
        return self.__add_restriction("channel", channel.id, categoryName)
    def remove_channel_restriction(self, channel: discord.TextChannelUser, categoryName: str):
        return self.__remove_restriction("channel", channel.id, categoryName)

    def set_user_category_error(self, msg: str):
        self.userErrorMsg = msg
        return
    def set_role_category_error(self, msg: str):
        self.roleErrorMsg = msg
        return
    def set_channel_category_error(self, msg: str):
        self.channelErrorMsg = msg
        return
    def set_direct_message_error(self, msg: str):
        self.directMessageErrorMsg = msg
        return

    def get_command_restrictions(self, commandName: str, default: CommandRestrictions = CommandRestrictions()):
        if self.commandRestrictions.get(commandName) == None:
            self.commandRestrictions[commandName] = default
        return self.commandRestrictions.get(commandName,default)

    # Writes saved restrictions of a server to its respective text file
    async def save_restrictions(self):
        # saveFile = open(self.guild.id + "_restrictions.txt", 'w')
        return

    # Loads and parses the restrictions for a given server
    async def load_restrictions(self):
        # saveFile = open(self.guild.id + "_restrictions.txt", 'r')
        return
    pass