import praw
import prawcore.exceptions as pex
import config
import time
import datetime
import json

wpath = config.workingdir

version = "1.0"

# Originally, in SUEB and WPB, several settings would be changed in the actual code
# rather than in the config file, against common coding practice. Now, I'm just going to put those
# variables in the config file and give them a new name.

# We keep track of who's submitted how many posts with a dictionary.
# The key is the user and the value is the number of posts they've submitted.
submitters = {'testuser': '0'}

 
# This creates the Reddit instance and authenticates the user agent with Reddit.
def login():
    print ("Connecting to Reddit")
    print ("Authenticating...", end='')
    r = praw.Reddit(username=config.username,
                    password=config.password,
                    client_id=config.client_id,
                    client_secret=config.client_secret,
                    user_agent="ToS_Definition_Bot" + version)
    print ('done')
    return r


# This function fecthes the list of comments the bot has already replied to from the respective file.
def get_comment_list():
    with open (wpath + "comments.txt", "r") as f :
        comments_replied_to = f.read()
        comments_replied_to = comments_replied_to.split("\n")
    comments_replied_to = list(filter(None, comments_replied_to))
    return comments_replied_to


# This function writes the comment ID to the list of comments replied to and the corresponding file.
# WARNING: This will overwrite everything in the file. It's expected that you've read the file's contents first with
# get_comment_list().
def write_comment_list(id, comments_replied_to):
    comments_replied_to.append(id)
    with open(wpath + 'comments.txt','w') as f :
        for i in comments_replied_to :
            f.write(i + '\n')
    return comments_replied_to


# This function fetches the current human-readable time.
def get_time() :
    st = time.time()
    st = datetime.datetime.fromtimestamp(st).strftime('%Y-%m-%d %H:%M:%S')
    return st


# Check to make sure the author isn't posting too many posts per day
def check_author(crt, now, post):
    global submitters
    
    # We keep track of submitters with a dictionary stored in a JSON file.
    with open(wpath + 'submitters.json') as s:
        submitters = json.load(s)
    
    # If the author is in the dictionary (they've posted something already today), increment their value by 1
    if post.author.name in submitters:
        submitters[post.author.name] += 1
        
    # If the author is NOT in the dictionary (they have NOT posted today), add them to the dictionary and set their
    # value to 1.
    else:
        submitters[post.author.name] = 1
    
    # If they've posted MORE than the max posts per day, remove their post.
    if submitters[post.author.name] > config.max_posts:
        post.mod.remove()
        print (now + ": Removed post " + post.id + " by " + post.author.name + ". They posted " + str(submitters[post.author.name]) + " times today.")
        post.reply("Unfortunately, your post has been removed because to prevent queue-flooding, we only allow " +
                   str(config.max_posts) + " posts per person per day." + config.signature).mod.distinguish(sticky=True)
        
    
    # Write the dictionary of submitters back into the JSON file
    with open(wpath + 'submitters.json', 'w') as s:
        json.dump(submitters, s)

    write_comment_list(post.id, crt)


# A list of triggers for the bot.
def check_triggers(crt, time, c, b):

    # This catches the exception we get for trying to fetch the title of a comment
    try :
        t = c.title.lower()
    except AttributeError :
        t = ''
    check_author(crt, time, c)
    #print("Checking triggers for " + c.name)
    
    # Here, we use the well-established and respected technique of chaining together millions of if statements to
    # simulate artificial intelligence.
    # Seriously, we just use if statements to check if any triggers are in the comment.
    
    # b is the body text of the comment.
    # c is the comment itself.
    
    # Use if, not elif, because we want the bot to be able to trigger more than once.

    # THESE TRIGGERS IN THIS FIRST IF STATEMENT WILL GO ONLY IF SUMMONED.
    
    if "what is" in b or "what's" in b or "!def" in b :
        if "vfr" in b :
            print (time + ": " + c.author.name + " queried VFR.")
            
            # I've borrowed Seth's language here.
            c.reply("VFR stands for Voting For Roles. It is the act of voting someone up to the stand to get a role"
                    + " claim from them." +
                    "This helps narrow down the list of roles that remain in the game and generally helps the Town a"
                    + " lot more than evils." +
                    config.signature)
            crt = write_comment_list(c.id, crt)
    
    # ANYTHING BELOW THIS LINE WILL TRIGGER REGARDLESS OF WHETHER THE BOT WAS INTENTIONALLY SUMMONED OR NOT
    if "!rate" in b :
        payload = b.split(' ')
        
        if len(payload) == 2 :
            print (time + ": " + c.author.name + " queried " + payload[1] + "'s rate limit.")
            c.reply(payload[1] + " has submitted " + submitters[payload[1]] + " posts today. Once they post " + str(config.max_posts) + 
                    " posts, subsequent posts will be removed. This resets at midnight UTC." + config.signature)
        if len(payload) == 1 :
            print (time + ": " + c.author.name + " queried their rate limit.")
            c.reply("You've posted " + submitters[c.author.name] + " times today. Once you post " + str(config.max_posts) + 
                    " posts, subsequent posts will be removed. This resets at midnight UTC." + config.signature)
    if ("elo" in t and (('+' in t or '-' in t) or 'in ' in t) :
        print(time + ":", c.author.name, "queried ELO")
        c.reply("It seems like you might be asking how ELO gain or loss is calculated. \n\n The game calculates ELO based on the following factors:\n\n" +
                "*Your ELO in comparison to the average ELO of your opponents\n*Your role's winrate\n*Whether or not you won\n\nNothing else is taken into consideration" +
                ". If you got a rather low ELO gain, it was probably because your role's winrate is high or because you were matched with opponents that weren't as high rank as you." +
                " If you got a lot of ELO from a game, you were either playing a role with a low winrate, or you were matched with players that were much higher rank than you." + config.signature)
    # This rather long line checks for "new" and "player" in the title, OR "noob" and something else that says the OP
    # is the noob.
    if "new" in t and "player" in t\
            or ("noob" in c.name.lower() and ("player" in t
                                              or "here" in t
                                              or "'m" in t
                                              or "im" in t)):
        print(time + ":", c.author.name, "queried new player.")
        
        # Also borrowed from Seth
        c.reply("It seems like you're a new player to the game. " +
                '[Here is an extremely helpful guide made by /u/NateNate60, one of the Moderators for this subreddit]' +
                "(https://drive.google.com/file/d/1TC_hue8fEqH3xas2yMVU8KqQA-MovRZ-/view?usp=drivesdk)," +
                "and [here is another guide made by Chancell0r on the Forums]" +
                "(https://blankmediagames.com/phpbb/viewtopic.php?f=3&t=73489&p=2399389)." +
                "You should also check the sidebar of the subreddit for any other useful links, such as the " +
                '[Frequently Asked Questions](https://www.reddit.com/r/TownofSalemgame/wiki/faq)' +
                'and the ["Is is against the rules?"](https://www.redd.it/fucmif?sort=qa) thread.' +
                config.signature)
    if "pay" in t or "cost" in t or "free " in t or "free?" in t :
        print(time + ": " + c.author.name + " queried for Pay to Play")
        c.reply("If you're asking about whether the game is still free to play, the developers [moved the game to Pay to Play](https://blankmediagames.com/phpbb/viewtopic.php?f=11&t=92848)" +
                " in November of 2018 to combat a flood of people spamming meaningless messages in games and making new accounts to avoid bans. You can " +
                "still play for free if you create an account before November of 2018. If you want to refer a friend, the referral code feature allows you to " +
                "give then 5 free games. However, if they break the rules and get banned, you'll get a suspension as well! Only give codes to people you" +
                " know personally. Giving or asking for codes in this subreddit is not allowed." + config.signature)
    if ("freez" in t\
            or "lag" in t\
            or "disconnect" in t\
            or "dc" in t) and c.link_flair_text == 'Question':
        print(time + ": " + c.author.name + " queried for freezing and lagging.")
        c.reply("If your game seizes and stops responding, try one of the following fixes. \n\n" +
                "* ON BROWSER: Try resizing the browser window a few times. Nobody is quite sure why this works, but"
                + " it occasionally fixes connection issues and visual glitches. It may have to do with forcing"
                + " the game to redraw." +
                "\n* ON STEAM: Try verifying the game integrity. You can do this by going into your Steam library,"
                + " then going into the game's Properties, then Local Files, then clicking the Verify Integrity"
                + " button. You may also try resizing the game's window when this issue occurs." +
                "\n* ON MOBILE: Try restarting your phone or re-installing the app." +
                "\n* IN GENERAL: Wired connections are always going to be more stable than wireless ones. If"
                + " possible, use a wired Ethernet connection where possible to prevent packet loss, which is often"
                + " what causes disconnection issues." +
                "The game doesn't deal with packet loss that well. This can occasionally happen even on strong Wi-Fi"
                + " or cellular connections." +
                config.signature)
    if "crash" in t or "error" in t or "bug" in t or "glitch" in t :
        print(time + ": " + c.author.name + " queried for crashing.")
        c.reply("If you're talking about an error in the game, please be aware that the developers no longer check this subreddit." +
                " Please send bug reports to the developers on the official Town of Salem forums.\n\n [General bug reports](https://blankmediagames.com/phpbb/viewforum.php?f=10) \n\n [Mobile bug reports](https://blankmediagames.com/phpbb/viewforum.php?f=60)" +
                "\n\n [Steam bug reports](https://blankmediagames.com/phpbb/viewforum.php?f=78)" + config.signature)
    crt = write_comment_list(c.id, crt)


# And now, the meat of the bot.
def run_bot(r, chknum, tick=config.tick):
    #print ("Running bot") #Left over from debugging
    now = get_time()
    crt = get_comment_list()
    
    # Checking comments will likely fail because the bot will try to read the title of a comment, which raises an
    # exception. Might be doable with try/except statements
    '''
    for comment in r.subreddit('TownofSalemgame').comments(limit = chknum) : #Fetch comments
    
        # This makes it so that triggers are not case sensitive. We make everything in the comment lowecase.
        b = comment.body.lower()
        
        # Make sure the author isn't in the blacklist and that we haven't already replied to the comment.
        # We also don't want to try to reply to locked/archived comments because that will throw an error.
        # We will also check that the user actually wants a definition so the bot doesn't reply to everyone who mentions
        # VFR. Yes, this if statement is long, but that's to prevent the stupidly indented body of code that happened in
        # SUEB because Python enforces indentation.
        if c.author not in config.banned and c.id not in crt and c.locked == False and c.archived == False : 
            check_triggers(chknum, time, c, b)
    '''
    #print ("Checking " + str(chknum) + " comments")
    for c in r.subreddit('TownofSalemgame').comments(limit=chknum):
        b = c.body.lower()
        if c.author not in config.blacklisted \
                and c.id not in crt \
                and not c.locked \
                and not c.archived \
                and ("what is" in b or "what's" in b or "!def" in b):
            crt = get_comment_list()
            check_triggers(crt, now, c, b)

    # Same thing as above, but checks posts instead of comments.
    for post in r.subreddit('TownofSalemgame').new(limit=chknum):
        #print(post.title) #Leftover from debugging
        # BESIDES the first time when it checks 1000 posts, check if the poster is posting too much
        if post.id not in crt :
            crt = get_comment_list()
            check_triggers(crt,now,post,post.selftext.lower())
    
    # Check the inbox for any direct requests (people summoning the bot by pinging it).
    for message in r.inbox.all() :
        # Check only unread mentions. That way, we don't have to keep track of what we've already checked. Reddit will
        # do that for us.
        if message.new:
            
            # If the user comments `!delete` and they are the OP, then delete the comment.
            if "!del" in message.body.lower():
                # Check if the parent comment was written by the bot and if the one asking to delete is the parent
                # commenter
                if message.parent().author.name == r.user.me()\
                        and message.parent().parent().author.name == message.author.name :
                    message.parent().delete()
                    message.reply("Successfully deleted." + config.signature)

            # If the user is just running the !info or !blacklist command, we don't need to check anything else.
            if "!info" in message.body.lower() :
                message.reply("**NateNate60's ToS_Helper_Bot version" + version + "**\n\n" +
                              "I give helpful definitions to certain terms used in Town of Salem. If you want me to" +
                              " scan another user's comments for all terms, just ping me. I will then scan the" +
                              " comment you replied to for any keywords and give definitions for each one. " +
                              " Additionally, if your comment contains \"what is\", \"what's\", or the universal" +
                              " trigger word `!def`, I will also reply with any helpful definitions. If you find" +
                              " this annoying and would rather not have me reply to anything you say, simply comment" +
                              "`!blacklist` and I will ignore your comments." +
                              config.signature)
                print(now + ": " + message.author.name + " ran !info")
            # The bot will not check its own comments for triggers.
            try :
                if message.parent().author.name != r.user.me().name :
                    # Check the parent comment for triggers.
                    check_triggers(chknum, now, message.parent(), message.parent().body.lower())
            except AttributeError :
                pass
            # REGARDLESS of whether we found any triggers or now, the message will be marked as read so we don't check
            # it again.
            message.mark_read()
    
    # Sleep for 5 seconds. We don't really get enough traffic to need this to be continuously running and this saves my
    # server's computing power.
    # This also mostly prevents problems with Reddit's rate limit.
    time.sleep(5)


print("Starting ToS Helper Bot version " + version)
r = login()
# Check up to the last 1000 comments to avoid missing any comments that were made during downtime.
tick = config.tick
#if tick == 0:
#    run_bot(r, chknum=10)
# Run the bot forever
while True:
    tick += 1
    now = get_time()
    crt = get_comment_list()
    try :
        run_bot(r, config.chknum, tick)
    except pex.ServerError:
        print (now + ": The bot received an HTTP 503 response and will now restart.")
    except pex.RequestException :
    # In case it ever does encounter issues with Reddit's rate limit
        time.sleep(60)
    '''
    I don't like that this doesn't tell me where the exception is. I prefer it to just halt because that has saved me from spam so many times

    except Exception as ex:
        print(now + ":", "Exception when running tick", tick)
        print(ex)
    '''
    if int(time.time())%86400 > 5 :
        # Empty the dictionary every 24 hours
        submitters = {}
        with open(wpath + 'submitters.json', 'w') as s:
            json.dump(submitters, s)
    
    # This keeps track of and reports how many cycles the bot's gone through, but with decreasing frequency because
    # it's less likely to crash the longer it's been running.
    if tick == 1:
        print(now + ":", "The bot has successfully completed one cycle.")
    elif tick == 5:
        print(now + ":", 'The bot has successfully completed 5 cycles.')
    elif tick%10 == 0 and tick < 100:
        print(now + ":", 'The bot has successfully completed', tick, "cycles.")
    elif tick%100 == 0 and tick < 500:
        print(now + ":", 'The bot has successfully completed', tick, "cycles.")
    elif tick%500 == 0 and tick < 3000:
        print(now + ":", 'The bot has successfully completed', tick, "cycles.")
    elif tick%1000 == 0:
        print(now + ":", 'The bot has successfully completed', tick, "cycles.")
