<img src="RT_Logo.png" alt="Logo" title = "Logo" align="right" width="100" height="100" />

# RT Bot
## About
A bot made for the Runtime Terror Discord server. The purpose of the bot is to give users the ability to easily add/remove roles from themselves for classes and majors.
## Configuration
You will need to add your own `config.py` if you would like to fork this repo and run it yourself. The file must include:
* `TOKEN`: This is the token that you get when you create your bot. To see how to create your own bot and how to find your token, check out [this tutorial](https://discordpy.readthedocs.io/en/latest/discord.html).
* `CHANNEL_ID`: The channel that the bot will listen for implicit commands in (without the `.` command prefix).
* `COMMAND_CHANNEL`: The channel where the Admins can interact with the bot separately from the channel above.
* `CLASS_SPECIFIERS`: The class acronyms before the listing number.
* `MAJORS`: A dictionary of key-value pairs, where the key is the exact name of the major role, and the value is the ID of the role.
* `ADD`: A string identifying the `add` command.
* `REMOVE`: A string identifying the `remove` command.
* `COMMANDS`: A list containing `ADD` and `REMOVE`.
## Contributing
If you are from the Runtime Terror server, and you would like to contribute to this bot, please create an issue under the "Issues" tab.