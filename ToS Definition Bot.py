version = "b0.1"
print("Starting NateNate60's ToS Definition Bot version " + version)

print("Importing modules..." + end='')

import praw
import config3 as config
import time
import datetime
import os.path

print('done')

# Originally, in SUEB and WPB, several settings would be changed in the actual code
# rather than in the config file, against common coding practice. Now, I'm just going to put those
# variables in the config file and give them a new name.

chknum = config.chknum
tick = config.tick
sign = config.signature
 
 # This creates the Reddit instance and authenticates the user agent with Reddit.
def login() :
    print ("Connecting to Reddit")
    print ("Authenticating...", end='')
    r = praw.Reddit(username = config.username,
                    password = config.password,
                    client_id = config.client_id,
                    client_secret = config.client_secret,
                    user_agent = "ToS_Definition_Bot" + version)
    print ('done')
    return r

# This function fecthes the list of comments the bot has already replied to.
def get_comment_list() :
    with open ("comments3.txt", "r") as f :
        comments_replied_to = f.read()
        comments_replied_to = comments_replied_to.split("\n")
    comments_replied_to = list(filter(None, comments_replied_to))
    return comments_replied_to

# This function fetches the current human-readable time.
def get_time() :
    st = ttime.time()
    st = datetime.datetime.fromtimestamp(st).strftime('%Y-%m-%d %H:%M:%S')
    return st

# And now, the meat of the bot.
def run_bot(tick, chknum, time) : # Add required variables later when I need them. I can't remember them all right now.
    
    # On the first run, check 1,000 comments instead of the original chknum value.
    if tick == 0 :
        chknum = 1000 
        # I think this won't stay 1,000 because of something about local and global variables.
        # IDK man it's 10pm I can't be bothered to check to make sure at this hour
    
    for comments in r.subreddit('TownofSalemgame').comments(limit = chknum) : #Fetch comments
    
        # This makes it so that triggers are not case sensitive. We make everything in the comment lowecase.
        b = comments.body.lower()
        
        # Make sure the author isn't in the blacklist and that we haven't already replied to the comment.
        # We also don't want to try to reply to locked/archived comments because that will throw an error.
        # We will also check that the user actually wants a definition so the bot doesn't reply to everyone who mentions VFR.
        # Yes, this if statement is long, but that's to prevent the stupidly indented body of code that happened in SUEB because Python enforces indentation.
        if c.author not in config.banned and c.id not in crt and c.locked == False and c.archived == False and ("what is" in b or "what's" in b or "!def" in b): 
            
            # Here, we use the well-established and respected technique of chaining together millions of if statements to simulate artificial inteligence.
            # Seriously, we just use if statements to check if any triggers are in the comment.
            
            # b is the body text of the comment.
            # c is the comment itself.
            
            if "VFR" in b :
                print (time + ": " + c.author.name + " queried VFR.")
                
                #I've borrowed Seth's language here.
                c.reply("VFR stands for Voting For Roles. It is the act of voting someone up to the stand to get a role claim from them." +
                        "This helps narrow down the list of roles that remain in the game and generally helps the Town a lot more than evils." +
                        signature)
