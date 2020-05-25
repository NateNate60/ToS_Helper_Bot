import praw
from config import settings
from config import secrets
import datetime
from os import path
import sqlite3
import time

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
    crt = get_comment_list()

    for c in r.subreddit('TownofSalemgame').comments(limit=chknum):
        if c.locked or c.archived or c.id in crt:
            continue
        log("Processing comment", c.id, "by", c.author.name)
        moderate_submission(c, c.body)
        if c.author not in settings.blacklisted:
            help_submission(c, c.body)
        # Mark the comment as processed
        append_comment_list(c.id)

    for post in r.subreddit('TownofSalemgame').new(limit=chknum):
        if post.id in crt:
            continue
        log("Processing post", post.id, "by", post.author.name)
        moderate_post(post)
        body = post.name + "\n\n" + post.selftext
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
    if "what is" in b or "what's" in b or "!def" in b:
        if "vfr" in b:
            log("User", s.author.name, "asked about VFR in submission", s.id)
            if not settings.read_only:
                # I've borrowed Seth's language here.
                s.reply("VFR stands for Voting For Roles. It is the act of voting someone up to the stand to get a role"
                        " claim from them. "
                        "This helps narrow down the list of roles that remain in the game and generally helps the Town"
                        " a lot more than evils." +
                        settings.signature)

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

    if "freez" in b or "lag" in b or "disconnect" in b or "dc" in b and s.link_flair_text.strip().lower() == 'question':
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

    if "flash" in b:
        log("User", s.author.name, "appears to be asking about flash in submission", s.id)
        if not settings.read_only:
            s.reply("If you're asking about what will happen when Google Chrome and Mozilla Firefox drop support for"
                    " Adobe Flash in December 2020, the developers are working on porting the game to the Unity engine."
                    "\n\n The Unity engine is already available for the mobile and Steam versions, if you want to check"
                    " it out. Further information is available [here]"
                    "(https://www.blankmediagames.com/phpbb/viewtopic.php?f=11&t=107706)." +
                    settings.signature)


def moderate_submission(s, body):
    """
    Check whether the given submission (comment or post) requires any automated moderator action.
    :param s: the submission to check.
    :param body: the body of the submission.
    :return: None.
    """
    pass


def moderate_post(post):
    """
    Check whether the given post requires any automated moderator action.
    :param post: the post to check.
    :return: None.
    """
    check_author(post)


def process_pm(msg):
    """
    Process the given private message, taking action if necessary.
    :param msg: the PM to process.
    :return: None.
    """
    # If the user comments `!delete` and they are the OP, then delete the comment.
    if "!delete" in msg.body.lower():
        # Check if the parent comment was written by the bot and if the one asking to delete is the parent commenter
        if msg.parent().author.name == session.user.me() and msg.parent().parent().author.name == msg.author.name:
            msg.parent().delete()
            msg.reply("Successfully deleted." + settings.signature)

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
                                    (post.author.name, ))
        submitters.execute("INSERT INTO submitters (username, quantity) VALUES (?, 1)"
                           " ON CONFLICT (username) DO UPDATE SET quantity = quantity + 1",
                           (post.author.name, ))
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
    print(datetime.datetime.fromtimestamp(time.time()).strftime('[%Y-%m-%d %H:%M:%S]'), *msg, **kwargs)


if __name__ == "__main__":
    log("Starting ToS Helper Bot version", version)
    session = login()
    # Check up to the last 1000 comments to avoid missing any comments that were made during downtime.
    # Currently disabled because it would break the daily post limit check.
    tick = settings.tick
    # if tick == 0:
    #    run_bot(r, chknum=1000)
    # Run the bot forever
    while True:
        tick += 1
        run_bot(session)

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
