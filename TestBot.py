import asyncio
import discord
import sys
from discord.ext.commands import Bot

client = Bot(command_prefix = '!')
TOKEN = "NDk5Mjk0MjQ5NjQ5NTY5Nzky.DqExdA.ulGlcvtYIjQOtVduvCcM9dN816M"
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
setShipRoles = []
allAdminRoles = []
botDebugCmdChannels = []
botDebugMsgChannels = []
roleAliases = {}

@client.event
async def on_ready():
    global setShipRoles
    global botServers

    botServers = client.servers
    debugMsgChannels = ['504101054720507914', '504080535807852555']
    debugCmdChannels = ['504100982943121449', '499367739857698836']
    adminRoleIDs = ['501888889175408651' ]
    shipRoles = [ 'Lance', 'Bulldozer', 'Wormhole', 'Thorn', 'Grapple']

    for server in botServers:
        for role in server.roles:
            if role.name in shipRoles:
                setShipRoles.append(role)
            if role.id in adminRoleIDs:
                allAdminRoles.append(role)
        for channel in server.channels:
            if channel.id in debugCmdChannels:
                botDebugCmdChannels.append(channel)
            if channel.id in debugMsgChannels:
                botDebugMsgChannels.append(channel)

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print("Connected Servers: ")
    for server in botServers:
        print(server.name + ' ' + server.id)
    print('------')
    await send_bot_update("I have been started up! You may have to reset your settings with me.")
    await setShipAlias('Bulldozer', 'Bd')
    await setShipAlias('Bulldozer', 'Dozer')
    await setShipAlias('Bulldozer', 'Shockwave')
    await setShipAlias('Lance', 'Ln')
    await setShipAlias('Wormhole', 'Wh')
    await setShipAlias('Wormhole', 'Worm')
    return

def user_name_id(member):
    return member.name + ' (' + member.id + ')'

async def send_bot_update(msg: str):
    msg = "@here\nBot Update!" + '\n' + msg + '\n'
    for channel in botDebugMsgChannels:
        await client.send_message(channel, msg)
    return
async def send_bot_msg(msg: str):
    for channel in botDebugMsgChannels:
        await client.send_message(channel, msg)
    return
async def send_debug_msg(context, msg: str):
    msgStart  = "Server: "
    if context.message.server == None:
        msgStart += " N/A"
    else:
        msgStart += context.message.server.name
    msg = msgStart + '\n' + msg + '\n'
    for member in debugModes:
        if debugModes[member]:
            await client.send_message(member, msg)
    for channel in botDebugMsgChannels:
        await client.send_message(channel, msg)
    return

async def base_cmd_validation(context):
    if context.message.server == None:
        await client.say("I don't run commands from DM's")
        return False
    return True
async def channel_cmd_validation(context, validChannels = []):
    if not await base_cmd_validation(context):
        return False
    if not context.message.channel in validChannels:
        await client.say("This is not a valid channel for this commamd.")
        return False
    return True

async def admin_dm_cmd_validation(context):
    auth = context.message.author

    if auth in debugModes:
        return True

    for server in client.servers:
        mem = server.get_member(auth.id)
        if mem != None:
            for role in mem.roles:
                if role in allAdminRoles:
                    return True
    await client.say("I don't run commands from DM's")
    return False
async def admin_base_cmd_validation(context):
    if not await base_cmd_validation(context):
        return False
    command_author = context.message.author
    for role in command_author.roles:
        if role in allAdminRoles:
            return True
    await client.say("You are not authorized to use this command.")
    return False
async def admin_channel_cmd_validation(context, validChannels = []):
    if not await channel_cmd_validation(context, validChannels):
        return False
    command_author = context.message.author
    for role in command_author.roles:
        if role in allAdminRoles:
            return True
    await client.say("You are not authorized to use this command.")
    return False

@client.command(name='setship', pass_context = True, brief = "Allows user to set their ship role.")
async def setShip(context, message):
    if not await base_cmd_validation(context):
        return False

    roles = context.message.server.roles
    author = context.message.author
    message = message.lower();
    message = message.capitalize();
    message = roleAliases.get(message, message);
    role = discord.utils.get(context.message.server.roles, name=message)
    debugMsg = ""
    if role != None:
        if role in setShipRoles:
            for role2 in author.roles:
                if role2 in setShipRoles:
                    await client.remove_roles(author, role2)
            await client.add_roles(author, role)
            await client.say(author.name + " is a " + role.name + " main!")
            await send_debug_msg(context, user_name_id(author) + " set their ship role to " + role.name + " (" + role.id + ")")
            return
    await client.say("That ship does not exist")
    return
async def setShipAlias(roleName, alias):
    global roleAliases
    roleAliases[alias] = roleName
    await send_bot_msg("Alias \'"+alias+"\' set for ship '"+roleName+"\'");
    return

@client.command(name='ban', pass_context = True, hidden = True)
async def ban(context, user, *, reason: str = None):
    if not await admin_base_cmd_validation(context):
        return
    mem = context.message.mentions
    if len(mem) > 0:
        result = "Failed"
        try:
            await client.ban(mem[0], 1)
            result = "Succesful"
            await client.say("Banned " + mem[0].name + "\nReason: " + arg1)
        except discord.errors.Forbidden:
            await client.say("Could not ban '" + user_name_id(mem[0]) + "', user is of an unbannable role!")
        except:
            await client.say("Could not ban '" + user_name_id(mem[0]) + "', error occured.")
        await send_debug_msg(context, "Ban command called by '" + user_name_id(context.message.author) + " on " + user_name_id(mem[0]) + ".\nResult: " + result)
    return

async def printDebug(context):
    author = context.message.author
    if author in debugModes:
        msg = "Debug Mode for " + user_name_id(author) + ": " + str(debugModes[author])
        await client.send_message(context.message.channel, msg)
        return
    await client.send_message(context.message.channel, user_name_id(author) + " has no stored debug mode.")

@client.command(name='debug', pass_context=True, hidden=True, help="Allows an admin or mod to ban a user. Technically, this command will ban the first user mention found in the message, but the reason will contain the user's name if it is not the first argument.")
async def debugComm(context, message: str = None):
    if not await admin_dm_cmd_validation(context) and not await admin_channel_cmd_validation(context, botDebugCmdChannels):
        return
    if message == None:
        await printDebug(context)
        return
    else:
        msg =""
        d = boolArgs.get(message.lower())
        if d == None:
            msg +="Cannot set debug to \'" + message + "\'\n"
        else:
            global debugModes
            debugModes[context.message.author] = d
            msg += "Debug set to " + str(d) + " for user " + context.message.author.name + " (" + context.message.author.id + ")"
        await client.say(msg)
    return

@client.command(name='write', pass_context=True, hidden=True)
async def writeComm(context, *, message):
    file = open("testwrite.txt", "w");
    file.write(message);
    await send_bot_msg("Succesfully wrote to file")
    return

@client.command(name='read', pass_context=True, hidden=True)
async def readComm(context, message):
    try:
        file = open(message+'.txt', "r");
        await client.say(file.read())
    except:
        await client.say("File does nto exist")
    return

@client.command(name='notify', pass_context=True, hidden=True)
async def notifyComm(context):
    return

@client.command(name='register', pass_context=True, hidden=True)
async def registerComm(context, message):
    server = context.server
    return

@client.command(name='edit', pass_context=True, hidden=True)
async def createNotifier(context, message):
    return

client.run(TOKEN)