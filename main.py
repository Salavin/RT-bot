import linecache
import os
import subprocess
import sys
import psutil
from datetime import datetime

import discord
from discord.utils import get
from discord.ext import commands
import config
import constants
import re

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
        if '-' in word and word.split('-')[0].upper() in constants.CLASS_SPECIFIERS:
            if "491" in word or "492" in word:  # Special cases for Senior Design classes
                newWord = "SE/COMS/CPRE/EE-491" if "491" in word else "SE/COMS/CPRE/EE-492"
            elif word.upper() == "CPRE-430" or word.upper() == "CPRE-530":
                newWord = "CPRE-430/530"  # Special case for CPRE-430/530
            else:
                newWord = word.upper()
            successfulRoleFound = False
            for role in roles:
                if role.name == newWord:
                    successfulRoleFound = True
                    if action == constants.ADD:
                        await message.author.add_roles(role)
                    else:
                        await message.author.remove_roles(role)
                    successfulRoles.append(word)
                    break
            if not successfulRoleFound:
                unsuccessfulRoles.append(word)
        elif word.upper() in constants.MAJORS or word.upper() in constants.OTHERS:
            role = get(roles, id=constants.MAJORS.get(word.upper()) if word.upper() in constants.MAJORS else constants.OTHERS.get(word.upper()))
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
    try:
        await message.author.send(messageString)
    except discord.errors.Forbidden:
        await client.get_channel(config.ERROR_CHANNEL).send(f"Unable to send messages to user `{message.author.name + '#' + message.author.discriminator}`")
    await message.delete()


async def handle_errors(user, error, message):
    """
    Handles any errors by sending an error message to the user and also posting an error to the error channel for the admins to view.
    :param user: The user that triggered the error.
    :param error: The error.
    :param message: The message that triggered the error.
    """
    try:
        await user.send(f"An error occurred when processing your request:\n```{error}```\nYour roles may or may not have been successfully added. If the problem persists, please DM <@262043915081875456>.")
    except discord.errors.Forbidden:
        await client.get_channel(config.ERROR_CHANNEL).send(f"Unable to send messages to user `{user.name + '#' + user.discriminator}`")

    channel = client.get_channel(config.ERROR_CHANNEL)
    date = datetime.now()
    embed = discord.Embed(
        type="rich",
        description=f"At `{date}`, {user.name}, with the input `{message}`, triggered the following error:\n```{error}```"
    )
    embed.set_author(
        name=user.name + "#" + user.discriminator,
        icon_url=str(user.avatar_url))

    await channel.send(embed=embed)
    print(error)


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    try:
        if (message.author == client.user) or (message.channel.id not in config.VALID_CHANNELS):
            return

        if message.channel.id in config.COMMAND_CHANNELS:
            await client.process_commands(message)
            return

        words = message.content.split(' ')
        if words[0].lower() not in constants.COMMANDS:
            for command in client.commands:
                if words[0][1:] == command.name or words[0][1:] in command.aliases:
                    await client.process_commands(message)
                    return
            try:
                await message.author.send("Sorry, but `" + words[0] + "` is not a valid command!")
            except discord.errors.Forbidden:
                await client.get_channel(config.ERROR_CHANNEL).send(
                    f"Unable to send messages to user `{message.author.name + '#' + message.author.discriminator}`")

            await message.delete()
            return
        else:
            command = constants.ADD if words[0].lower() == constants.ADD else constants.REMOVE

        await handle_roles(words[1:], command, message)
    except Exception:
        await handle_errors(message.author, get_exception(), message.content)


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @client.command(brief="Adds roles to a user based on the list of roles given.")
    async def add(self: discord.ext.commands.Context, *args):
        """
        Usage: `.add <name(s) of role(s)>`

        Adds roles to a user based on the list of roles given.
        """
        await handle_roles(list(set([i for i in args])), constants.ADD, self.message)

    @client.command(aliases=["rm"], brief="Removes roles from a user based on the list of roles given.")
    async def remove(self: discord.ext.commands.Context, *args):
        """
        Usage: `.(remove | rm) <name(s) of role(s)>`

        Removes roles from a user based on the list of roles given.
        """
        await handle_roles(list(set([i for i in args])), constants.REMOVE, self.message)

    @client.command(brief="Makes a poll.")
    async def poll(self: discord.ext.commands.Context, *, arg):
        """
        Usage: `.poll {<poll title>} [<poll option 1>] [<poll option 2>] ... [<poll option n (up to 26)>]`

        Creates a poll with a given title and options, and adds the proper react emotes.
        """
        title = re.findall("{(.+)}", arg)
        options = re.findall("(?:\s*\[([^\]]+))+", arg)

        if len(title) == 0:
            await self.send("Invalid title\nUsage: `.poll {<poll title>} [<poll option 1>] [<poll option 2>] ... [<poll option n (up to 26)>]`")
            return
        if len(options) == 0 or len(options) > 26:
            await self.send("Invalid args\nUsage: `.poll {<poll title>} [<poll option 1>] [<poll option 2>] ... [<poll option n (up to 26)>]`")
            return

        description = ""
        index = 0
        unicode = ord('🇦')
        for option in options:
            description += f"{chr(unicode)} {option}\n\n"
            index += 1
            unicode += 1
        embed = discord.Embed(title=title[0], description=description)
        message = await self.send(embed=embed)

        unicode = ord('🇦')
        for i in range(index):
            await message.add_reaction(f'{chr(unicode)}')
            unicode += 1

    @client.command()
    @commands.has_role(712353676299075704)
    async def restart(self: discord.ext.commands.Context):
        """Restarts the bot, given the user has the correct role."""
        await self.send("Restarting...")
        print("Shutting down")
        sys.exit()

    @client.command()
    @commands.has_role(712353676299075704)
    async def stats(self: discord.ext.commands.Context):
        """Shows the uptime and memory usage for the bot."""
        p = subprocess.Popen("uptime", stdout=subprocess.PIPE, shell=True)
        (output, _) = p.communicate()
        await self.send(f"Uptime: `{str(output)[3: -3]}`")
        process = psutil.Process(os.getpid())
        await self.send(f"Memory: `{str(process.memory_info().rss / float(1000000))} mb`")

    @client.command()
    @commands.has_role(712353676299075704)
    async def ping(self: discord.ext.commands.Context):
        """Shows the current ping for the bot."""
        await self.send(f"Pong! (`{str(round(client.latency, 3))} s`)")

    @client.command()
    @commands.has_role(712353676299075704)
    async def announcement(self):
        """Allows an announcement from the Admins to be posted without the bot deleting the message."""
        return

    @client.event
    async def on_command_error(self: discord.ext.commands.Context, error):
        """Global command error handler."""
        if isinstance(error, discord.ext.commands.MissingRole):
            await handle_errors(self.author, "You do not have permission to run this command.", self.message.content)
        else:
            await handle_errors(self.author, error, self.message.content)
        await self.message.delete()


client.run(config.TOKEN)
