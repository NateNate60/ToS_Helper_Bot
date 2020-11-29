import praw
from config import settings
from config import secrets
import prawcore.exceptions as pex
import time
import datetime
from os import path
import sqlite3
import time
import json

wpath = path.dirname(settings.__file__)

version = "1.0"

# Originally, in SUEB and WPB, several settings would be changed in the actual code
# rather than in the config file, against common coding practice. Now, I'm just going to put those
# variables in the config file and give them a new name.

# We keep track of who's submitted how many posts with an SQLite 3 database
submitters = sqlite3.connect(path.join(wpath, 'submitters.sqlite3'))
with submitters:
    submitters.execute("CREATE TABLE IF NOT EXISTS submitters"
                       "(username TEXT NOT NULL PRIMARY KEY,"
                       " quantity INTEGER NOT NULL,"
                       " last_date TEXT NOT NULL DEFAULT CURRENT_DATE)")

# This exception will be raised when a post for while Rule 11 applies is encountered, but it's not time to remove it yet.
# It MUST be caught when moderate_post() is run.
#                 except RuleElevenTimer : continue # Continue to the next post
# It should not be used for any other purpose.
class RuleElevenTimer(Exception) : pass



def login():
    """
    Create the Reddit instance and authenticate the user agent using the credentials in config/secrets.py
    :return: the created Reddit instance
    """
    log("Connecting to Reddit")
    log("Authenticating...")
    r = praw.Reddit(username=secrets.username,
                    password=secrets.password,
                    client_id=secrets.client_id,
                    client_secret=secrets.client_secret,
                    user_agent="ToS_Definition_Bot" + version)
    log('Authenticated')
    r.read_only = settings.read_only
    if r.read_only:
        log("Running in read-only mode; intent will still be logged, but no action will be taken")
    return r


def run_bot(r, chknum=settings.chknum):
    """
    Process all new submissions to the subreddit and all new messages.
    :param r: the Reddit session.
    :param chknum: the maximum number of submissions of each type to check.
    :return: None.
    """
    for u in settings.no_flair:
        if next(r.subreddit("TownofSalemgame").flair(redditor=u))['flair_text'] is None :
            r.subreddit('TownofSalemgame').flair.delete(u)

    crt = get_comment_list()

    for c in r.subreddit('TownofSalemgame').comments(limit=chknum):
        if c.locked or c.archived or c.id in crt or c.author.name == "ToS_Helper_Bot":
            continue
        #log("Processing comment", c.id, "by", c.author.name)
        moderate_submission(c, c.body)
        if c.author not in settings.blacklisted and ("!def" in c.body.lower() or "what's" in c.body.lower() or "what is" in c.body.lower() or "whats" in c.body.lower() or "!rep" in c.body.lower() or "!tb" in c.body.lower() or "!rate" in c.body.lower()) and (len(c.body.lower()) < 50 or "!def" in c.body.lower()) :
            help_submission(c, c.body)
        # Mark the comment as processed
        append_comment_list(c.id)

    for post in r.subreddit('TownofSalemgame').new(limit=chknum):
        if post.id in crt:
            continue
        #log("Processing post", post.id, "by", post.author.name)
        try : moderate_post(post)
        except RuleElevenTimer : continue #If the R11 timer isn't up yet, DO NOT append_comment_list or anything else, just go to the next post.
        body = post.name.lower()
        moderate_submission(post, body)
        if post.author not in settings.blacklisted:
            help_submission(post, body)
        # Mark the post as processed
        append_comment_list(post.id)

    if settings.read_only:
        # In PRAW read-only mode, we can't even check the inbox :(
        return
    # Check the inbox for any direct requests (people summoning the bot by pinging it).
    for message in r.inbox.all():
        # Check only unread mentions. That way, we don't have to keep track of what we've already checked. Reddit will
        # do that for us.
        if message.new:
            process_pm(message)
            # Mark as read, since we don't gain anything from processing the same message multiple times.
            message.mark_read()


def help_submission(s, body):
    """
    Check whether the given submission (comment or post) requires any helpful user action to be taken.
    :param s: the submission to check.
    :param body: the body of the submission.
    :return: None.
    """
    b = body.lower()
    if b == None :
        b = ''
    try :
        f = s.link_flair_text
        if f == None :
            f = ''
        else :
            f = f.lower()
    except AttributeError :
        f = ''
    if "!def" in b or ("what is" in b or "what's" in b or "how does" in b or ("how" in b and "s" in b and "?" in b)) and len(b) < 50:
        if "vfr" in b:
            log("User", s.author.name, "asked about VFR in submission", s.id)
            if not settings.read_only:
                # I've borrowed Seth's language here.
                s.reply("VFR stands for Voting For Roles. It is the act of voting someone up to the stand to get a role"
                        " claim from them. "
                        "This helps narrow down the list of roles that remain in the game and generally helps the Town"
                        " a lot more than evils." +
                        settings.signature)

    if "!tb" in b or "!rep" in b:
        log (s.author.name + " queried reports")
        payload = b.split(' ')
        if len(payload) > 3 and len(payload) < 10 :
            s.reply("Invalid syntax. The correct syntax is `!reports [username]`, without the brackets. Please use your Town of Salem username and *not* your Reddit or Steam username. For help or general information, run `!reports`" + settings.signature)
        elif len(payload) == 1 :
            s.reply("INFORMATION ON `!reports`:\n\n`!reports` allows you to query Town of Salem users' reports. To query someone's reports, run `!reports [username]`. Your reports will be returned in a PM, unless you are a designated user (mods and prominent users), are the OP of the original post, or are commenting in the designated reports-fetching megathread, you will receive your reports in a PM. "
                    " If you are posting in the megathread and wish to receive your reports in a PM, use `!reports [username] pm`. For example, to query NateNate60's reports in a PM, run `!reports NateNate60 pm`." +
                    " The bot works by passing commands to [TurdPile](https://reddit.com/user/turdpile]'s TrialBot, which runes on the Town of Salem Trial System Discord server. Currently, the bot will only return guilty reports." +
                    ' If no guilty reports are found *or the username does not exist*, the bot will return "no results found". This does *not* mean that the user has never been reported or that all the reports against them were found' +
                    " to be not guilty. It just means that no reports were found to be guilty yet. For details on how the Trial System works, just ask " + '"how does the trial system work?"' + settings.signature)
        elif len(payload) < 10 :
            if len(payload) == 2 :
                payload.append('')
            if "[" in payload[1] or "]" in payload[1] or "/" in payload[1] :
                s.reply("Invalid syntax. Please try again without the brackets. Run `!reports` by itself for more info." + settings.signature)
                append_comment_list(s.id)
            else :
                with open ("reportsqueue.txt", 'w') as rq :
                    rq.write(payload[1])
                time.sleep(7)
                with open ("reports.json", 'r') as rj :
                    reports = json.load(rj)
                    replymessage = 'Fetched ' + str(len(reports)) + " reports " + 'against ' + payload[1] + " via [TurdPile](https://reddit.com/user/turdpile)'s TrialBot.\n\n"
                    if len(reports) == 0 :
                        replymessage = replymessage +  "No guilty reports were found. This does not mean that there were no reports, or that all pending reports were found innocent. For more information on this command, run `!reports` by itself."
                    for report in reports :
                        replymessage = replymessage + "- " + report + "\n"
                    if (s.is_submitter or payload[2] == 'here' or s.author.name in settings.approved or "access your reports here" in s.submission.title.lower()) and (payload[2] != "dm" and payload[2] != "pm" and payload[2] != "private"):
                        s.reply(replymessage + settings.signature)
                    else :
                        s.author.message("Reports request", replymessage + settings.signature + "\n\nYou are receiving this in a PM because you were not the OP or a designated user, and you weren't commenting in the reports megathread, or because you specifically requested it.")
               
    
    if "!rate" in b:
        payload = b.split(' ')
        if len(payload) == 2:
            
            log("User", s.author.name, "asked for the rate limit of user", payload[1])
            if not settings.read_only:
                s.reply(payload[1] + " has submitted " + str(get_daily_post_count(payload[1])) + " posts today."
                        "Once they post " + str(settings.max_posts) + " posts, subsequent posts will be removed."
                        "This resets at midnight UTC." + settings.signature)
        elif len(payload) == 1:
            log("User", s.author.name, "asked for their rate limit")
            if not settings.read_only:
                s.reply("You've posted " + str(get_daily_post_count(s.author.name)) + " times today. Once you post " +
                        str(settings.max_posts) + " posts, subsequent posts will be removed."
                        "This resets at midnight UTC." + settings.signature)

    if "new" in b and "player" in b or ("noob" in b and ("player" in b or "here" in b or "'m" in b or "im" in b)):
        log("User", s.author.name, "appears to be a new player in submission", s.id)
        if not settings.read_only:
            # Also borrowed from Seth
            s.reply("It seems like you're a new player to the game. "
                    '[Here is a helpful guide made by /u/NateNate60, one of the Moderators for this subreddit]'
                    "(https://drive.google.com/file/d/1TC_hue8fEqH3xas2yMVU8KqQA-MovRZ-/view?usp=drivesdk),"
                    "and [here is another guide made by Chancell0r on the Forums]"
                    "(https://blankmediagames.com/phpbb/viewtopic.php?f=3&t=73489&p=2399389). "
                    "You should also check the sidebar of the subreddit for any other useful links, such as the "
                    '[Frequently Asked Questions](https://www.reddit.com/r/TownofSalemgame/wiki/faq)'
                    'and the ["Is is against the rules?"](https://www.redd.it/fucmif?sort=qa) thread.' +
                    settings.signature)

    if "pay" in b or "cost" in b or "free " in b or "free?" in b :
        log(s.author.name + " queried for Pay to Play")
        s.reply("If you're asking about whether the game is still free to play, the developers [moved the game to Pay to Play](https://blankmediagames.com/phpbb/viewtopic.php?f=11&t=92848)" +
                " in November of 2018 to combat a flood of people spamming meaningless messages in games and making new accounts to avoid bans. You can " +
                "still play for free if you create an account before November of 2018. If you want to refer a friend, the referral code feature allows you to " +
                "give then 5 free games. However, if they break the rules and get banned, you'll get a suspension as well! Only give codes to people you" +
                " know personally. Giving or asking for codes in this subreddit is not allowed." + settings.signature)

    if "freez" in b or "lag" in b or "disconnect" in b or "dc" in b and (f == 'question' or f == '' or f == 'technical issue / bug'):
        if "abnormal" not in b:
            log("User", s.author.name, "appears to be asking about freezing in submission", s.id)
            if not settings.read_only:
                s.reply("If your game seizes and stops responding, try one of the following fixes.\n\n"
                        "* ON BROWSER: Try resizing the browser window a few times. Nobody is quite sure why this works,"
                        " but it occasionally fixes connection issues and visual glitches. It may have to do with forcing"
                        " the game to redraw."
                        "\n* ON STEAM: Try verifying the game integrity. You can do this by going into your Steam library,"
                        " then going into the game's Properties, then Local Files, then clicking the Verify Integrity"
                        " button. You may also try resizing the game's window when this issue occurs."
                        "\n* ON MOBILE: Try restarting your phone or re-installing the app."
                        "\n* IN GENERAL: Wired connections are always going to be more stable than wireless ones. If"
                        " possible, use a wired Ethernet connection where possible to prevent packet loss, which is often"
                        " what causes disconnection issues."
                        "The game doesn't deal with packet loss that well. This can occasionally happen even on strong"
                        " Wi-Fi or cellular connections." +
                        settings.signature)
        else :
            s.reply("If you're asking about the " + '"abnormal disconnect" error,' + " we aren't quite sure why this error occurs or what causes it, but the developers are " +
                    "aware of the issue and are working on a resolution." + settings.signature)
    if "crash" in b or "error" in b or "bug" in b or "glitch" in b or f == 'technical issue / bug':
        log(s.author.name + " queried for crashing.")
        s.reply("If you're talking about an error in the game, please be aware that the developers no longer check this subreddit." +
                " Please send bug reports to the developers on the official Town of Salem forums.\n\n [General bug reports](https://blankmediagames.com/phpbb/viewforum.php?f=10) \n\n [Mobile bug reports](https://blankmediagames.com/phpbb/viewforum.php?f=60)" +
                "\n\n [Steam bug reports](https://blankmediagames.com/phpbb/viewforum.php?f=78)" + settings.signature)

    if 'log in' in b or 'login' in b or 'logging in' in b or 'password' in b :
        log(s.author.name + " queried for login issues")
        s.reply("Are you having trouble logging into the game? Consider reading [this thread](https://www.blankmediagames.com/phpbb/viewtopic.php?f=11&t=105415&p=3342479#p3342479) on the Official Forums for help if your account was made" +
                " before 2019. A password reset was required by BlankMediaGames for security reasons.\n\nHave you forgotten your password? You can [request a password reset here](https://www.blankmediagames.com/help/requestpasswordreset.php)." +
                "\n\nNeed more help? If we can't solve your problem, you should [send an email to the developers](mailto:support@blankmediagames.zendesk.com)" + settings.signature)

    if "trial" in b and 'sys' in b :
        log(s.author.name + " queried for the Trial System.")
        s.reply("If you're asking how the Trial System works, the Trial System is BlankMediaGame's system where regular Town of Salem players can help sort through reports and judge whether they are guilty or not. Anyone with more than "+
                " 150 games played can vote on reports in the Trial System. [Click here to get to the Trial System](https://blankmediagames.com/Trial). If a majority of Jurors decide that a report is guilty, it will be refered to a Judge "+
                "for final approval. If the judge decides that a penalty will be issued, then they can do so. For more questions, you can contact the Trial System administrator, [TurdPile](https://reddit.com/user/turdpile)." + settings.signature)


def moderate_submission(s, body):
    """
    Check whether the given submission (comment or post) requires any automated moderator action.
    :param s: the submission to check.
    :param body: the body of the submission.
    :return: None.
    """
    
    # It is easier to work with non-case sensitive body texts than with ones with mixed case.
    body = body.lower()

    if s.author.comment_karma < 100 and ("sey" in body or "church" in body or "saint" in body) :
        session.subreddit('TownofSalemgame').banned.add(s.user.name, ban_reason='Potential spam account', 
                                                  ban_message="Your account has been banned as an anti-spam measure. All accounts less than 100 Karma may be automatically banned for saying things in a list of blacklisted words." +
                                                  " We had to put this rule in place due to rampant trolling and ban evasion. If you believe this is a mistake and you **are not** a spammer or troll, " +
                                                  "then we apologise for wrongfully banning you.\n\n[IF YOU WERE WRONGLY BANNED CLICK HERE](https://www.reddit.com/message/compose?to=r/townofsalemgame&subject=Wrongful%20automatic%20ban)")
        s.mod.remove()


def moderate_post(post):
    """
    Check whether the given post requires any automated moderator action.
    :param post: the post to check.
    :return: None.
    """

    if post.link_flair_text == "Win Screen" and len(post.title) < 50:
        if post.created_utc < int(time.time()) - 1800 :
            ok = False
            for comment in post.comments :
                if comment.author.name == post.author.name :
                    ok = True; break
            if not ok:
                post.mod.remove()
                log("Removed post by", post.author.name, "for rule 11 violation.")
                post.reply("Unfortunately, your post has been removed because we require all winscreens to be accompanied by an interesting backstory. If you've added a backstory, please send modmail" +
                             " or mention u/NateNate60 to get your post restored." + settings.signature).mod.distinguish(sticky=True)
        else : raise RuleElevenTimer

    if "among us" in post.title.lower() :
        post.mod.remove()
        post.reply('Unfortunately, your post has been removed because Among Us memes and discussion are only allowed in the [Among Us megathread]' +
                   "(https://reddit.com/r/TownofSalemgame/comments/j0ua5a/among_us_megathread/). If your post isn't about Among Us, please contact the moderators" +
                   " to get your post restored." + settings.signature).mod.distinguish(sticky=True)
    try : check_author(post)
    except AttributeError : pass #This error occasionally gets thrown when the post.author ends up being None. I don't know why this happens but we "handle" it here.


def process_pm(msg):
    """
    Process the given private message, taking action if necessary.
    :param msg: the PM to process.
    :return: None.
    """
    # If the user comments `!delete` and they are the OP, then delete the comment.
    if "!del" in msg.body.lower():
        try:
            # Check if the parent comment was written by the bot and if the one asking to delete is the parent commenter
            if msg.parent().author.name == session.user.me() and msg.parent().parent().author.name == msg.author.name and "because" not in msg.parent().body.lower():
                msg.parent().mod.remove(spam=False, mod_note="User requested removal")
                msg.reply("Successfully deleted." + settings.signature)
        except AttributeError as err:
            print("Error: caught AttributeError")
            print(err)

    # If the user is just running the !info or !blacklist command, we don't need to check anything else.
    if "!info" in msg.body.lower():
        msg.reply("**NateNate60's ToS_Helper_Bot version" + version + "**\n\n"
                  "I give helpful definitions to certain terms used in Town of Salem. If you want me to"
                  " scan another user's comments for all terms, just ping me. I will then scan the"
                  " comment you replied to for any keywords and give definitions for each one."
                  " Additionally, if your comment contains \"what is\", \"what's\", or the universal"
                  " trigger word `!def`, I will also reply with any helpful definitions. If you find"
                  " this annoying and would rather not have me reply to anything you say, simply comment"
                  "`!blacklist` and I will ignore your comments." +
                  settings.signature)
        log(msg.author.name, "ran !info")
    try:
        # The bot will not check its own comments for triggers.
        if msg.parent().author.name != session.user.me().name:
            if msg.parent().id in get_comment_list():
                log("User", msg.author.name, "asked for an already processed submission to be processed")
            # We don't need to check for moderation triggers, since submissions to the subreddit we moderate have
            # already been checked before this function is used in the run_bot function.
            # A race condition might exist, but it would be extremely difficult to intentionally exploit.
            help_submission(msg.parent(), msg.parent().body)
            append_comment_list(msg.parent().id)
    except AttributeError:
        pass


def check_author(post):
    """
    Check that the author of the given post hasn't exceeded the post limit and increment their daily post counter.
    :param post: the post whose author to check.
    :return: None.
    """
    with submitters:
        cursor = submitters.execute("SELECT CASE WHEN date('now') == last_date THEN quantity ELSE 0 END FROM submitters"
                                    " WHERE username=? LIMIT 1",
                                    (post.author.name.lower(), ))
        submitters.execute("INSERT INTO submitters (username, quantity) VALUES (?, 1)"
                           " ON CONFLICT (username) DO UPDATE SET quantity = quantity + 1",
                           (post.author.name.lower(), ))
        submitters.commit()
        result = cursor.fetchone()
        if result is None:
            quantity = 0
        else:
            (quantity, ) = result
        if quantity >= settings.max_posts:
            log("Removing post", post.id, "by", post.author.name, "since they have exceeded the daily post limit")
            if not settings.read_only:
                post.mod.remove()
                post.reply("Unfortunately, your post has been removed because to prevent queue-flooding, we only allow "
                           + str(settings.max_posts) + " posts per person per day." + settings.signature) \
                    .mod.distinguish(sticky=True)


def get_daily_post_count(user):
    """
    Fetch the number of posts a certain user has made today.
    :param user: The username of the user.
    :return: The integer number of posts the user has made today.
    """
    user = user.lower()
    with submitters:
        cursor = submitters.execute("SELECT CASE WHEN date('now') == last_date THEN quantity ELSE 0 END FROM submitters"
                                    " WHERE username=? LIMIT 1",
                                    (user, ))
        result = cursor.fetchone()
        if result is None:
            quantity = 0
        else:
            (quantity, ) = result
        return quantity


def get_comment_list():
    """
    Load the list of comments the bot has already replied to.
    This is to avoid replying to the same comment multiple times.
    :return: the list of comments already replied to.
    """
    try:
        with open(path.join(wpath, "comments.txt"), "r") as f:
            comments_replied_to = f.read().split("\n")
        return list(filter(None, comments_replied_to))
    except FileNotFoundError:
        # The file doesn't yet exist, but it will be written as soon as we append an ID
        return []


def append_comment_list(s_id):
    """
    Save the given submission ID as a comment that has already been replied to.
    :param s_id: the ID of the submission to save.
    :return: None.
    """
    with open(path.join(wpath, 'comments.txt'), 'a') as f:
        f.write('\n' + s_id)


def log(*msg, **kwargs):
    """
    Log the given message.
    :param msg: The message to log.
    :return: None.
    """
    """
    logoutput = datetime.datetime.fromtimestamp(time.time()).strftime('[%Y-%m-%d %H:%M:%S]') + ' ' + *msg + ' ' + **kwargs
    print(logoutput)
    if settings.logtofile :
        with open ('log.txt', 'a') as l :
            l.write('\n' + logoutput)
    """
    print (datetime.datetime.fromtimestamp(time.time()).strftime('[%Y-%m-%d %H:%M:%S]'), *msg, **kwargs)

if not path.exists ('log.txt') :
    with open ('log.txt','w') as l :
        l.write("This is where output from the bot will be logged, if settings.logtofile is set to true.\n\n")

if __name__ == "__main__":
    log("Starting ToS Helper Bot version", version)
    session = login()
    # Check up to the last 1000 comments to avoid missing any comments that were made during downtime.
    # Currently disabled because it would break the daily post limit check.
    tick = settings.tick
    # if tick == 0:
    #    run_bot(r, chknum=1000)

    while True:
        tick += 1
        try :
            run_bot(session)
        except pex.ServerError:
            pass
        except pex.RequestException :
            pass
        # This keeps track of and reports how many cycles the bot's gone through, but with decreasing frequency because
        # it's less likely to crash the longer it's been running.
        if tick == 1:
            log("The bot has successfully completed one cycle.")
        elif tick == 5:
            log('The bot has successfully completed 5 cycles.')
        elif tick % 10 == 0 and tick < 100:
            log('The bot has successfully completed', tick, "cycles.")
        elif tick % 100 == 0 and tick < 500:
            log('The bot has successfully completed', tick, "cycles.")
        elif tick % 500 == 0 and tick < 3000:
            log('The bot has successfully completed', tick, "cycles.")
        elif tick % 1000 == 0:
            log('The bot has successfully completed', tick, "cycles.")

        # Sleep for 5 seconds. We don't really get enough traffic to need this to be continuously running and this saves
        # my server's computing power.
        # This also mostly prevents problems with Reddit's rate limit.
        time.sleep(5)
