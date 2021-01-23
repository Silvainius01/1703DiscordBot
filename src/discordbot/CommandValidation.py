import sys
import asyncio
import discord
import discord.ext.commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from src.discordbot.ServerCommandRestrictions import GuildCommandRestrictions
from src.discordbot.ServerCommandRestrictions import CommandRestrictions

def RepresentsInt(s):
    try: 
        int(s)
    except ValueError:
        return False
    return True

def restrictions(commandName: str, default: CommandRestrictions):
    def predicate(context):
        restrictions = BotCommandValidation.get_restrictions(context.guild, default)
        return restrictions.check_restrictions(context, commandName)
    return commands.check(predicate)

class BotCommandValidation(commands.Cog):
    directMessageErrorMsg = "This command cannot be run from DMs."
    guildRestrictions = dict()
    directMessageRestrictions = GuildCommandRestrictions(None)

    def __init__(self, botClient: Bot):
        self.client = botClient

        # On startup, initilize restriction objects, and load them from disk if they exist
        for guild in botClient.guilds:
            BotCommandValidation.guildRestrictions[guild.id] = GuildCommandRestrictions(guild)
            BotCommandValidation.guildRestrictions[guild.id].load_restrictions()
        return

    @commands.Cog.listener()
    def on_ready(self):
        for guild in self.client.guilds:
            BotCommandValidation.guildRestrictions[guild.id] = GuildCommandRestrictions(guild)
            BotCommandValidation.guildRestrictions[guild.id].load_restrictions()
            print(f'Added guild {guild.name} restrictions.')
        print("Command validation active.")
        return

    def get_restrictions(guild: discord.Guild):
        """ 
        Returns the ServerCommandRestrictons object for the given guild. 
        Returns an empty restrictions object if guild has no entry.
        """
        return BotCommandValidation.guildRestrictions.get(guild.id, BotCommandValidation.directMessageRestrictions)
    def add_guild_restrictions(self, guild: discord.Guild):
        """
        Adds a guild to the restrictions dictionary
        Returns True if the guild was added, False if it already exists.
        """
        if BotCommandValidation.guildRestrictions.get(guild.id) != None:
            return False

        BotCommandValidation.guildRestrictions[guild.id] = GuildCommandRestrictions(guild)
        BotCommandValidation.guildRestrictions[guild.id].save_restrictions()
        return True

    def add_user_restriction(self, guild: discord.Guild, user: discord.User, categoryName: str):
        """
        Adds a user to the the given user restrictions category.
        Returns true if succesful.
        """
        restrictions = BotCommandValidation.get_restrictions(guild)
        return restrictions.guild != None and restrictions.add_user_restriction(user, categoryName)
    def remove_user_restriction(self, guild: discord.Guild, user: discord.User, categoryName: str):
        """
        Removes a user from the the given user restrictions category.
        Returns true if succesful.
        """
        restrictions = BotCommandValidation.get_restrictions(guild)
        return restrictions.guild != None and restrictions.remove_user_restriction(user, categoryName)
    
    def add_role_restriction(self, guild: discord.Guild, role: discord.Role, categoryName: str):
        """
        Adds a role to the the given role restrictions category.
        Returns true if succesful.
        """
        restrictions = BotCommandValidation.get_restrictions(guild)
        return restrictions.guild != None and restrictions.add_role_restriction(role, categoryName)
    def remove_role_restriction(self, guild: discord.Guild, role: discord.Role, categoryName: str):
        """
        Removes a role from the the given role restrictions category.
        Returns true if succesful.
        """
        restrictions = BotCommandValidation.get_restrictions(guild)
        return restrictions.guild != None and restrictions.remove_role_restriction(role, categoryName)
    
    def add_channel_restriction(self, guild: discord.Guild, channel: discord.TextChannel, categoryName: str):
        """
        Adds a channel to the the given channel restrictions category.
        Returns true if succesful.
        """
        restrictions = BotCommandValidation.get_restrictions(guild)
        return restrictions.guild != None and restrictions.add_channel_restriction(channel, categoryName)
    def remove_channel_restriction(self, guild: discord.Guild, channel: discord.TextChannel, categoryName: str):
        """
        Removes a channel from the the given channel restrictions category.
        Returns true if succesful.
        """
        restrictions = BotCommandValidation.get_restrictions(guild)
        return restrictions.guild != None and restrictions.remove_channel_restriction(channel, categoryName)

    @commands.command(name="addRestriction")
    @restrictions(commandName="addRestriction", default=CommandRestrictions(False))
    async def add_restriction(self, context: Context, categoryName: str):
        """
        Sets restrictions in a category for all mentioned users, roles, and channels
        """
        for member in context.message.mentions:
            self.add_user_restriction(context.guild, member, categoryName)
        for role in context.message.role_mentions:
            self.add_role_restriction(context.guild, role, categoryName)
        for channel in context.message.channel_mentions:
            self.add_channel_restriction(context.guild, chanel, categoryName)
        return

    @commands.command(name="removeRestriction")
    @restrictions(commandName="removeRestriction", default=CommandRestrictions(False))
    async def remove_restriction(self, context: Context, categoryName: str):
        """
        Sets restrictions in a category for all mentioned users, roles, and channels
        """
        for member in context.message.mentions:
            self.remove_user_restriction(context.guild, member, categoryName)
        for role in context.message.role_mentions:
            self.remove_role_restriction(context.guild, role, categoryName)
        for channel in context.message.channel_mentions:
            self.remove_channel_restriction(context.guild, chanel, categoryName)
        return
    pass

def setup(client: Bot):
    client.add_cog(BotCommandValidation(client))
    return