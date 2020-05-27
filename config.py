# WELCOME TO THE TOS_DEFINITION_BOT CONFIG FILE!


# ARE YOU USING THE SEPARATE AUTH.PY FILE? IF YES, UNCOMMENT LINES 48, 44, 40, 36, 31, and 5
#import auth






# How many posts should a user be able to make in a single day before they're warned about flooding?
max_posts = 999

# Who should not be able to make any requests with the bot?
blacklisted = []

# How many comments should the bot check in one go?
chknum = 50

# If you want the bot to pretend it's already checked the subreddit already, how many times should it pretend to have
# checked it? This is useful if you want to skip the time when it checks the last 1,000 comments on the first go.
tick = 0

# What should the bot sign its messages with?
signature = "\n\n I try my best to be accurate and trigger on only those who need it, but I do make mistakes. Report" \
            " mistakes to u/NateNate60 or the mods. \n\n [About ToS Helper Bot](https://natenate60.xyz/tos-helper-bot)"

# What's the username the bot should sign in with?
username = "ToS_Helper_Bot"
#username = auth.username


# What's the account's password?
password = "password"
#password = auth.password

# What's the bot's client ID?
client_id = "client_id"
#client_id = auth.client.id

# What's the client_secret?
client_secret = "client_secret"
#client_secret = auth.client_secret

#THE SLASH IS NECESSARY
workingdir="/thb/"
