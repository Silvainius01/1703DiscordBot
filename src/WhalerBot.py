import sys
import asyncio
import datetime

import discord
from discord.ext.commands import Bot

import Calender
from CommandValidation import BotCommandValidation

client = Bot(command_prefix = '!')
cmdval = None 
botCalender = None

TOKEN = "NTU3MTM3MDg5OTI2Mzk3OTU1.D3D6jQ.VHjRBP00gsOJmf1mvY14yPL1Ud4"
botTestID = '499367739857698836'
boolArgs = {
    'true': True,
    '1': True,
    'false': False,
    '0': False
 }

debugModes = {
}

# Arrays for all bot management stuff
botServers = []
debugChannel = None
roleAliases = {}

@client.event
async def on_ready():
    global cmdval
    global botCalender

    cmdval = BotCommandValidation(client);
    botCalender = Calender.BotCalender(client, datetime.datetime.now().date())

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print("Connected Servers: ")
    print('------')
    for server in client.servers:
        await cmdval.load_restrictions(server)
    return

def user_name_id(member):
    return member.name + ' (' + member.id + ')'

class Channel_Management(object):
    @client.command(name='channelcat', pass_context=True, brief = "Displays a list of all channels in a given category (Admin)")
    async def cmdChannelcat(self, context, channelListName):
        if not await cmdval.cmd_validation(context):
            return
        await client.say(cmdval.print_channel_catagory(channelListName))
        return
    @client.command(name='registerchannel', pass_context=True, brief = "Register all mentioned channels to a given category. (Admin)")
    async def cmdRegisterChannel(context, channelListName):
        if not await cmdval.role_cmd_validation(context, 'admin'):
            return
        if len(context.message.channel_mentions) < 1:
            return

        msg = "Registered "
        for channel in context.message.channel_mentions:
            msg += channel.mention + " "
            await cmdval.register_channel(channel, channelListName)
        await client.say(msg + " to \'"+channelListName+"\'")
        return
    @client.command(name='unregisterchannel', pass_context=True, brief = "Remove channel from a given category (Admin)")
    async def cmdUsercat(context, userListName):
        if not await cmdval.role_cmd_validation(context, 'admin'):
            return
        msg = ''
        for channel in context.message.channel_mentions:
            result = await cmdval.unregister_user(channel, userListName)
            if result:
                msg += '\nRemoved ' + channel.name + ' from ' + userListName
            else:
                msg += '\n' + channel.name + ' is not in ' + userListName
        await client.say(msg)
        return

class Role_Management(object):
    @client.command(name='rolecat', pass_context=True, brief = "Displays a list of all roles in a given category (Admin)")
    async def cmdRolecat(context, roleListName):
        if not await cmdval.cmd_validation(context):
            return
        await client.say(cmdval.print_role_catagory(roleListName))
        return
    @client.command(name='registerrole', pass_context=True, brief = "Register all mentioned roles to a given category (Admin)")
    async def cmdRegisterRole(context, roleListName):
        if not await cmdval.role_cmd_validation(context, 'admin'):
            return
        if len(context.message.role_mentions) < 1:
            return

        msg = "Registered "
        for role in context.message.role_mentions:
            msg += role.mention + " "
            await cmdval.register_role(role, roleListName)
        await client.say(msg + " to \'"+roleListName+"\'")
        return
    @client.command(name='unregisterrole', pass_context=True, brief = "Remove role from a given category (Admin)")
    async def cmdUsercat(context, userListName):
        if not await cmdval.role_cmd_validation(context, 'admin'):
            return
        msg = ''
        for role in context.message.role_mentions:
            result = await cmdval.unregister_user(role, userListName)
            if result:
                msg += '\nRemoved ' + role.name + ' from ' + userListName
            else:
                msg += '\n' + role.name + ' is not in ' + userListName
        await client.say(msg)
        return

class User_Management(object):
    @client.command(name='usercat', pass_context=True, brief = "Displays a list of all users in a given category (Admin)")
    async def cmdUsercat(context, userListName):
        if not await cmdval.cmd_validation(context):
            return
        await client.say(cmdval.print_user_catagory(userListName))
        return
    @client.command(name='registeruser', pass_context=True, brief = "Register all mentioned users to a given category (Admin)")
    async def cmdRegisterUser(context, userListName):
        if not await cmdval.role_cmd_validation(context, 'admin'):
            return
        if len(context.message.mentions) < 1:
            return

        msg = "Registered "
        for user in context.message.mentions:
            msg += user.mention + " "
            await cmdval.register_user(user, userListName)
        await client.say(msg + " to \'"+userListName+"\'")
        return
    @client.command(name='unregisteruser', pass_context=True, brief = "Remove user from a given category (Admin)")
    async def cmdUsercat(context, userListName):
        if not await cmdval.role_cmd_validation(context, 'admin'):
            return
        msg = ''
        for user in context.message.mentions:
            result = await cmdval.unregister_user(user, userListName)
            if result:
                msg += '\nRemoved ' + user.name + ' from ' + userListName
            else:
                msg += '\n' + user.name + ' is not in ' + userListName
        await client.say(msg)
        return

@client.command(name='savecats', pass_context=True, brief = "Save current category settings manually (Admin)")
async def cmdSaveCatgories(context):
    if not await cmdval.role_cmd_validation(context, 'admin'):
        return
    await cmdval.save_restrictions();
    return

def deleteCategorySwitch(categoryName):
    dict = {
        "role" : cmdval.delete_role_category,
        "channel" : cmdval.delete_channel_category,
        "user" : cmdval.delete_user_category
        }
    return dict[categoryName];
@client.command(name='removecategory', pass_context=True, brief = "Removes a category of channels, users, or roles")
async def cmdRemoveCat(context, listName, categoryType):
    if not await cmdval.role_cmd_validation(context, 'admin'):
        return
    deleteCategory = deleteCategorySwitch(categoryType)
    if deleteCategory == None:
        await client.say("Category type \'" + categoryType + "\' does not exist" )
    if await (listName):
        await client.say("Deleted " + categoryType + " category \'" + listName + "\'")
    else:
        await client.say("Category name \'" + listName + "\' does not exist in \'" + category + "\'")
    return

#@client.command(name='setevent', pass_context=True, hidden=True)
async def cmdSetEvent(context, date, time, *, name):
    if not await cmdval.channel_cmd_validation(context, 'admin'):
        return

    dt = datetime.datetime.strptime(date+' '+time, "%m/%d/%Y %I:%M%p")
    event = Calender.CalenderEvent(name, dt)

    botCalender.set_event(event)
    events = botCalender.get_events(event.date)
    if events == None:
        await client.say("No events are scheduled for " + event.date.strftime('%a %b %d, %Y'))
    else:
        msg = "Events scheduled for " + event.date.strftime('%a %b %d, %Y:\n')
        for event in events:
            msg += event.dateTime.strftime('%I:%M%p ') + event.name + '\n'
        await client.say(msg)
    return

client.run(TOKEN)