import linecache
import os
import subprocess
import sys
import psutil

import discord
from discord.utils import get
from discord.ext import commands
import config
import constants

client = commands.Bot(command_prefix='.', help_command=None)


def get_exception():
    """Handling thrown exception from bot."""
    _, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


async def handle_roles(args, action, message):
    """
    Handles adding/removing roles to/from a user.

    :param args: The list of roles to add/remove.
    :param action: Whether to add or remove the list of roles.
    :param message: The original message that was sent
    """
    roles = message.channel.guild.roles
    successfulRoles = []
    unsuccessfulRoles = []

    for word in args:
        if '-' in word and word.split('-')[0].upper() in config.CLASS_SPECIFIERS:
            if "491" in word or "492" in word:  # Special cases for Senior Design classes
                newWord = "SE/COMS/CPRE/EE-" + "491" if "491" in word else "492"
            else:
                newWord = word.upper()
            for role in roles:
                if role.name == newWord:
                    if action == constants.ADD:
                        await message.author.add_roles(role)
                    else:
                        await message.author.remove_roles(role)
                    successfulRoles.append(word)
        elif word in constants.MAJORS or word in constants.OTHERS:
            role = get(roles, id=constants.MAJORS.get(word) if word in constants.MAJORS else constants.OTHERS.get(word))
            if action == constants.ADD:
                await message.author.add_roles(role)
            else:
                await message.author.remove_roles(role)
            successfulRoles.append(word)
        else:
            unsuccessfulRoles.append(word)

    messageString = ""
    if successfulRoles:
        messageString += "Successfully {verb} the following role(s):".format(
            verb="added" if action == constants.ADD else "removed")
        for role in successfulRoles:
            messageString += " `{role}`,".format(role=role)
        messageString = messageString[:-1] + '\n'
    if unsuccessfulRoles:
        messageString += "Had problems {verb} the following role(s):".format(
            verb="adding" if action == constants.ADD else "removing")
        for role in unsuccessfulRoles:
            messageString += " `{role}`,".format(role=role)
        messageString = messageString[
                        :-1] + "\nCheck for any typos you may have made, and check to see if the role is on the list. If it's not, ping an admin, and they can add it for you."
    messageString.rstrip('\n')
    await message.author.send(messageString)
    await message.delete()


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    try:
        if (message.author == client.user) or ((message.channel.id != config.CHANNEL_ID) and (message.channel.id != config.COMMAND_CHANNEL)):
            return

        if message.channel.id == config.COMMAND_CHANNEL:
            await client.process_commands(message)
            return

        words = message.content.split(' ')
        if words[0].lower() not in constants.COMMANDS:
            for command in client.commands:
                if words[0][1:] == command.name or words[0][1:] in command.aliases:
                    await client.process_commands(message)
                    return
            await message.author.send("Sorry, but `" + words[0] + "` is not a valid command!")
            await message.delete()
            return
        else:
            command = constants.ADD if words[0].lower() == constants.ADD else constants.REMOVE

        await handle_roles(words[1:], command, message)
    except Exception:
        channel = client.get_channel(config.ERROR_CHANNEL)
        await channel.send("```" + get_exception() + "```")
        await message.author.send("An error occured when processing your request:")
        await message.author.send("```" + get_exception() + "```")
        await message.author.send(
            "Your roles may or may not have been successfully added. If the problem persists, please DM <@262043915081875456>.")
        print(get_exception())


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @client.command(brief="Adds roles to a user based on the list of roles given.")
    async def add(self, *args):
        """
        Usage: `!add <name(s) of role(s)>`

        Adds roles to a user based on the list of roles given.
        """
        await handle_roles(list(set([i for i in args])), constants.ADD, self.message)

    @client.command(aliases=["rm"], brief="Removes roles from a user based on the list of roles given.")
    async def remove(self, *args):
        """
        Usage: `!(remove | rm) <name(s) of role(s)>`

        Removes roles from a user based on the list of roles given.
        """
        await handle_roles(list(set([i for i in args])), constants.REMOVE, self.message)

    @client.command()
    @commands.has_role(712353676299075704)
    async def restart(self):
        """Restarts the bot, given the user has the correct role."""
        await self.send("Restarting...")
        print("Shutting down")
        sys.exit()

    @client.command()
    @commands.has_role(712353676299075704)
    async def stats(self):
        """Shows the uptime and memory usage for the bot."""
        p = subprocess.Popen("uptime", stdout=subprocess.PIPE, shell=True)
        (output, _) = p.communicate()
        await self.send(f"Uptime: `{str(output)[3: -3]}`")
        process = psutil.Process(os.getpid())
        await self.send(f"Memory: `{str(process.memory_info().rss / float(1000000))} mb`")

    @client.command()
    @commands.has_role(712353676299075704)
    async def ping(self):
        """Shows the current ping for the bot."""
        await self.send(f"Pong! (`{str(round(client.latency, 3))} s`)")

    @client.command()
    @commands.has_role(712353676299075704)
    async def announcement(self):
        """Allows an announcement from the Admins to be posted without the bot deleting the message."""
        return

    @client.event
    async def on_command_error(self, error):
        """Global command error handler."""
        if isinstance(error, discord.ext.commands.MissingRole):
            await self.author.send("Oops, it looks like you don't have the correct role for running this!")
        else:
            await self.author.send("An error occured when processing your request:")
            await self.author.send(error)
            await self.author.send("Your roles may or may not have been successfully added. If the problem persists, please DM <@262043915081875456>.")
        await self.message.delete()
        channel = client.get_channel(config.ERROR_CHANNEL)
        await channel.send(error)


client.run(config.TOKEN)
