import discord
from discord.utils import get
import constants

client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if (message.author == client.user) or (message.channel.id != constants.CHANNEL_ID):
        return

    roles = message.channel.guild.roles
    words = message.content.split(' ')
    if words[0].lower() not in constants.COMMANDS:
        await message.author.send("Sorry, but `" + words[0] + "` is not a valid command!")
        await message.delete()
        return
    else:
        command = constants.ADD if words[0].lower() == constants.ADD else constants.REMOVE

    successfulRoles = []
    unsuccessfulRoles = []

    for word in words[1:]:
        if '-' in word and word.split('-')[0].upper() in constants.CLASS_SPECIFIERS:
            for role in roles:
                if role.name == word.upper():
                    if command == constants.ADD:
                        await message.author.add_roles(role)
                    else:
                        await message.author.remove_roles(role)
                    successfulRoles.append(word)
        elif word in constants.MAJORS:
            role = get(roles, id=constants.MAJORS.get(word))
            if command == constants.ADD:
                await message.author.add_roles(role)
            else:
                await message.author.remove_roles(role)
            successfulRoles.append(word)
        else:
            unsuccessfulRoles.append(word)

    messageString = ""
    if successfulRoles:
        messageString += "Successfully {verb} the following role(s):".format(verb="added" if command == constants.ADD else "removed")
        for role in successfulRoles:
            messageString += " `{role}`,".format(role=role)
        messageString = messageString[:-1] + '\n'
    if unsuccessfulRoles:
        messageString += "Had problems {verb} the following role(s):".format(verb="adding" if command == constants.ADD else "removing")
        for role in unsuccessfulRoles:
            messageString += " `{role}`,".format(role=role)
        messageString = messageString[:-1] + "\nCheck for any typos you may have made, and check to see if the role is on the list. If it's not, ping an admin, and they can add it for you."
    messageString.rstrip('\n')
    await message.author.send(messageString)
    await message.delete()

client.run(constants.TOKEN)
