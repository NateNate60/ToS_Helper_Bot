# WELCOME TO THE TOS_DEFINITION_BOT CONFIG FILE!

# How many posts should a user be able to make in a single day before they're warned about flooding?
max_posts = 10

# Who should not be able to make any requests with the bot?
blacklisted = []

# How many comments should the bot check in one go?
chknum = 50

# If you want the bot to pretend it's already checked the subreddit already, how many times should it pretend to have
# checked it? This is useful if you want to skip the time when it checks the last 1,000 comments on the first go.
tick = 0

# What should the bot sign its messages with?
signature = "\n\n I try my best to be accurate and trigger on only those who need it, but I do make mistakes. Report" \
            " mistakes to NateNate60 or the mods. \n\n ^NateNate60's ^ToS\\_Helper\\_Bot"

# What's the username the bot should sign in with?
username = "ToS_Helper_Bot"

# What's the account's password?
password = "NICE TRY LOL I'M KEEPING THIS SECRET FOR NOW"

# What's the bot's client ID?
client_id = "An-f7DowBxxuVw"

# What's the client_secret?
client_secret = "It's important that I keep this a... secret. Because it's the client_secret, obviously."

# Where is the bot installed to? Where did you git clone the repo to?
# This is needed because to run the bot as a service in systemd, absolute file paths are required.
# If you neglect to change this, FileNotFoundError will be raised and the bot will fail.
workingdir = '/thb'
