import discord
from discord.utils import get
import config

client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if (message.author == client.user) or (message.channel.id != config.CHANNEL_ID):
        return

    roles = message.channel.guild.roles
    words = message.content.split(' ')
    if words[0].lower() not in config.COMMANDS:
        await message.author.send("Sorry, but `" + words[0] + "` is not a valid command!")
        await message.delete()
        return
    else:
        command = config.ADD if words[0].lower() == config.ADD else config.REMOVE

    successfulRoles = []
    unsuccessfulRoles = []

    for word in words[1:]:
        if '-' in word and word.split('-')[0].upper() in config.CLASS_SPECIFIERS:
            for role in roles:
                if role.name == word.upper():
                    if command == config.ADD:
                        await message.author.add_roles(role)
                    else:
                        await message.author.remove_roles(role)
                    successfulRoles.append(word)
        elif word in config.MAJORS:
            role = get(roles, id=config.MAJORS.get(word))
            if command == config.ADD:
                await message.author.add_roles(role)
            else:
                await message.author.remove_roles(role)
            successfulRoles.append(word)
        else:
            unsuccessfulRoles.append(word)

    messageString = ""
    if successfulRoles:
        messageString += "Successfully {verb} the following role(s):".format(verb="added" if command == config.ADD else "removed")
        for role in successfulRoles:
            messageString += " `{role}`,".format(role=role)
        messageString = messageString[:-1] + '\n'
    if unsuccessfulRoles:
        messageString += "Had problems {verb} the following role(s):".format(verb="adding" if command == config.ADD else "removing")
        for role in unsuccessfulRoles:
            messageString += " `{role}`,".format(role=role)
        messageString = messageString[:-1] + "\nCheck for any typos you may have made, and check to see if the role is on the list. If it's not, ping an admin, and they can add it for you."
    messageString.rstrip('\n')
    await message.author.send(messageString)
    await message.delete()

client.run(config.TOKEN)
