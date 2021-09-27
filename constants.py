import config

CLASS_SPECIFIERS = ["SE", "COMS", "CPRE", "SD", "STAT", "EE"]
MAJORS = {
    "SE": 746125179842854922,
    "SYSE": 746125180702818486,
    "COMSCI": 746131438977417237,
    "COMPE": 746125166467088495,
    "CYBERSECE": 746125169264689184,
    "EE": 746125171206651964,
    "INFOASSURE": 746125174947971163,
    "DATASCI": 803318943049711687
}
OTHERS = {
    "GAMERS": 761764627377029120,
    "MOVIEWATCHER": 750880017390764062,
    "PLUGGEDIN": 750913471259869254,
    "ALUMNUS": 745267379897892914,
    "HELPER": 745404656586326116
}
ADD = "add"
REMOVE = "remove"
COMMANDS = [ADD, REMOVE, "rm"]
VALID_CHANNELS = [config.CHANNEL_ID, config.COMMAND_CHANNEL, config.POLL_CHANNEL]
COMMAND_CHANNELS = [config.COMMAND_CHANNEL, config.POLL_CHANNEL]

FOOTERS = [
    "This bot is open-source under RT-bot on github, not that you should hack it or anything, baka",
    "Don't let eye strain ruin your day. Protect your eyes from harmful blue light using Bakery Gaming's glasses. Use code 'plzDontThisIsAJoke' for 420% off your order.",
    "One out of ten hackers agree - binary is better!"
]
