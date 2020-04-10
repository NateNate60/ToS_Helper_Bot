version = "b0.1"
print("Starting NateNate60's ToS Definition Bot version " + version)

print("Importing modules..." + end='')

import praw
import config
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

# This function fecthes the list of comments the bot has already replied to from the respective file.
def get_comment_list() :
    with open ("comments.txt", "r") as f :
        comments_replied_to = f.read()
        comments_replied_to = comments_replied_to.split("\n")
    comments_replied_to = list(filter(None, comments_replied_to))
    return comments_replied_to

# This function writes the comment ID to the list of comments replied to and the corresponding file.
# WARNING: This will overwrite everything in the file. It's expected that you've read the file's contents first with get_comment_list().
def write_comment_list(id, comments_replied_to) :
    comments_replied_to.append(id)
    with open('comments.txt','w') as f :
        f.write(comments_replied_to)
    return comments_replied_to
    
# This function fetches the current human-readable time.
def get_time() :
    st = ttime.time()
    st = datetime.datetime.fromtimestamp(st).strftime('%Y-%m-%d %H:%M:%S')
    return st

# A list of triggers for the bot.
def check_triggers(chknum, time, c, b) :
    # Here, we use the well-established and respected technique of chaining together millions of if statements to simulate artificial inteligence.
    # Seriously, we just use if statements to check if any triggers are in the comment.
    
    # b is the body text of the comment.
    # c is the comment itself.
    
    # Use if, not elif, because we want the bot to be able to trigger more than once.
    
    
    # THESE TRIGGERS IN THIS FIRST IF STATEMENT WILL GO ONLY IF SUMMONED.
    if "what is" in b or "what's" in b or "!def" in b :
        if "vfr" in b :
            print (time + ": " + c.author.name + " queried VFR.")
            
            #I've borrowed Seth's language here.
            c.reply("VFR stands for Voting For Roles. It is the act of voting someone up to the stand to get a role claim from them." +
                    "This helps narrow down the list of roles that remain in the game and generally helps the Town a lot more than evils." +
                    signature)
            crt = write_comment_list(c.id, crt)
    
    
    
    #ANYTHING BELOW THIS LINE WILL TRIGGER REGARDLESS OF WHETHER THE BOT WAS INTENTIONALLY SUMMONED OR NOT
    
    # This rather long line checks for "new" and "player" in the title, OR "noob" and something else that says the OP is the noob.
    if "new" in c.name.lower() and "player" in c.name.lower() or ("noob" in c.name.lower() and ("player" in c.name.lower() or "here" in c.name.lower() or "'m" in c.name.lower() or "im" in c.name.lower() ) ):
        print (time + ": " + c.author.name + " queried new player.")
        
        # Also borrowed from Seth
        c.reply("It seems like you're a new player to the game." + ' [Here is an extremely helpful guide made by /u/NateNate60, one of the Moderators ' +
                "for this subreddit](https://drive.google.com/file/d/1TC_hue8fEqH3xas2yMVU8KqQA-MovRZ-/view?usp=drivesdk), and another guide made "
                'by Chancell0r on the Forums; https://blankmediagames.com/phpbb/viewtopic.php?f=3&t=73489&p=2399389. You should also check the sidebar' +
                ' of the subreddit for any other useful links, such as the [Frequently Asked Questions](https://www.reddit.com/r/TownofSalemgame/wiki/faq) ' +
                'and the ["Is is against the rules?"](https://www.redd.it/fucmif?sort=qa) thread.' + signature)
        crt = write_comment_list(c.id, crt)
    if "freez" in c.name.lower() or "lag" in c.name.lower() or "disconnect" in c.name.lower() or "dc" in c.name.lower() and c.link_flair_text.strip().lower() == 'question' :
        print (time + ": " + c.author.name + "queried for freezing and lagging.")
        c.reply("If your game siezes up and stops responding, try one of the following fixes. \n\n" +
                "ON BROWSER: Try resizing the browser window a few times. Nobody is quite sure why this works, but it occassionally fixes connection issues and visual glitches. It may have to do with forcing the game to redraw." +
                "\n\n ON STEAM: Try verifying the game integrity. You can do this by going into your Steam library, then going into the game's Properties, then Local Files, then clicking the Verify Integrity button. You may also try resizing the game's window when this issue occurs." +
                "\n\n ON MOBILE: Try restarting your phone or re-installing the app." +
                "\n\n IN GENERAL: Wired connections are always going to be more stable than wireless ones. If possible, use a wired Ethernet connection where possible to prevent packet loss, which is often what causes disconnection issues." +
                "The game doesn't deal with packet loss that well. This can occassionally happen even on strong Wi-Fi or cellular connections." + signature)
        crt = write_comment_list(c.id, crt)

# And now, the meat of the bot.
def run_bot() : # Add required variables later when I need them. I can't remember them all right now.
    
    # On the first run, check 1,000 comments instead of the original chknum value.
    if tick == 0 :
        chknum = 1000 
        # I think this won't stay 1,000 because of something about local and global variables.
        # IDK man it's 10pm I can't be bothered to check to make sure at this hour
    
    for comment in r.subreddit('TownofSalemgame').comments(limit = chknum) : #Fetch comments
    
        # This makes it so that triggers are not case sensitive. We make everything in the comment lowecase.
        b = comment.body.lower()
        
        # Make sure the author isn't in the blacklist and that we haven't already replied to the comment.
        # We also don't want to try to reply to locked/archived comments because that will throw an error.
        # We will also check that the user actually wants a definition so the bot doesn't reply to everyone who mentions VFR.
        # Yes, this if statement is long, but that's to prevent the stupidly indented body of code that happened in SUEB because Python enforces indentation.
        if c.author not in config.banned and c.id not in crt and c.locked == False and c.archived == False : 
            check_triggers(chknum, time, c, b)
    
    # Same thing as above, but checks posts instead of comments.
    for post in r.subreddit('TownofSalemgame').new(limit=chknum) :
        b = comment.body.lower()
        if c.author not in config.banned and c.id not in crt and c.locked == False and c.archived == False and ("what is" in b or "what's" in b or "!def" in b): 
            check_triggers(chknum, time, c, b)
    # Check the inbox for any direct requests (people summoning the bot by pinging it).
    for message in r.inbox.mentions() :
        # Check only unread mentions. That way, we don't have to keep track of what we've already checked. Reddit will do that for us.
        if message.new :
            
            # If the user is just running the !info or !blacklist command, we don't need to check anything else.
            if "!info" in message.body.lower() :
                message.reply("**NateNate60's ToS_Definition_Bot version" + version + "**\n\n" +
                              "I give helpful definitions to certain terms used in Town of Salem. If you want me to scan another user's comments for all terms," +
                              " just ping my username at u/ToS_Definition_Bot (not case sensitive). I will then scan the comment you replied to for any keywords" +
                              ' and give definitions for each one. Additionally, if your comment contains "what is", "what' + "'s" + '", or the universal trigger' +
                              'word "!def", I will also reply with any helpful definitions. If you find this annoying and would rather not have me reply to ' +
                              "anything you say, simply comment `!blacklist` and I will ignore your comments." + signature)
            
            # The bot will not check its own comments for triggers.
            elif message.parent().author.name != r.user.me().name :
                # Check the parent comment for triggers.
                check_triggers(chknum, time, message.parent(), mesage.parent().body.lower())
            
            # REGARDLESS of whether we found any triggers or now, the message will be marked as read so we don't check it again.
            message.mark_read()
    
    # Sleep for 5 seconds. We don't really get enough traffic to need this to be continuously running and this saves my server's computing power.
    # This also mostly prevents problems with Reddit's rate limit.
    time.sleep(5)

# Run the bot forever
while True :
    time = get_time()
    crt = get_comment_list()
    run_bot()
    tick += 1
    
    # This keeps track of and reports how many cycles the bot's gone through, but with decreasing frequency because it's less likely to crash
    # the longer it's been running.
    if tick == 1 :
        print (time + ":", "The bot has successfully completed one cycle.")
    elif tick == 5 :
        print (time + ":", 'The bot has successfully completed 5 cycles.')
    elif tick%10 == 0 and tick < 100 :
        print (time + ":", 'The bot has successfully completed', tick, "cycles.")
    elif tick%100 == 0 and tick < 500 :
        print (time + ":", 'The bot has successfully completed', tick, "cycles.")
    elif tick%500 == 0 and tick < 3000:
        print (time + ":", 'The bot has successfully completed', tick, "cycles.")
    elif tick%1000 == 0 :
        print (time + ":", 'The bot has successfully completed', tick, "cycles.")