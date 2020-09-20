# ToS Helper Bot

The Town of Salem Helper Bot is a Reddit bot for [/r/TownofSalemgame](https://reddit.com/r/TownofSalemgame) whose purpose is twofold:

1. To automatically respond to common queries.
2. To automate some of the subreddit moderation.

This bot was created due to the limitations of AutoModerator, which is impractical for any tasks that don't rely on solely trigger words.

## Features

Currently, the bot implements the following list of moderation tasks:

* Remove any posts users submit beyond the fixed daily post limit (per users).
    > Unfortunately, your post has been removed because to prevent queue-flooding, we only allow $MAX_POSTS posts per person per day.

* Explain what VFR is to any submission that resembles a question about VFR.
    > VFR stands for Voting For Roles. It is the act of voting someone up to the stand to get a role claim from them.
    This helps narrow down the list of roles that remain in the game and generally helps the Town a lot more than evils.

* Provide links to guides and other useful information when a user comments or posts about being new to the game.
    > It seems like you're a new player to the game.
    [Here is an extremely helpful guide made by /u/NateNate60, one of the Moderators for this subreddit](https://drive.google.com/file/d/1TC_hue8fEqH3xas2yMVU8KqQA-MovRZ-/view?usp=drivesdk),
    and [here is another guide made by Chancell0r on the Forums](https://blankmediagames.com/phpbb/viewtopic.php?f=3&t=73489&p=2399389).
    You should also check the sidebar of the subreddit for any other useful links, such as the [Frequently Asked Questions](https://www.reddit.com/r/TownofSalemgame/wiki/faq)
    and the ["Is is against the rules?"](https://www.redd.it/fucmif?sort=qa) thread.

* Provide advice when a user comments or posts about the game freezing, lagging, or disconnecting.
    > If your game seizes and stops responding, try one of the following fixes.
    >
    > * ON BROWSER: Try resizing the browser window a few times.
        Nobody is quite sure why this works, but it occasionally fixes connection issues and visual glitches.
        It may have to do with forcing the game to redraw.
    > * ON STEAM: Try verifying the game integrity.
        You can do this by going into your Steam library, then going into the game's Properties, then Local Files, then clicking the Verify Integrity button.
        You may also try resizing the game's window when this issue occurs.
    > * ON MOBILE: Try restarting your phone or re-installing the app.
    > * IN GENERAL: Wired connections are always going to be more stable than wireless ones.
        If possible, use a wired Ethernet connection where possible to prevent packet loss, which is often what causes disconnection issues.
        The game doesn't deal with packet loss that well.
        This can occasionally happen even on strong Wi-Fi or cellular connections.

* Provide information about the Unity port when a user comments or posts about Flash.
    > If you're asking about what will happen when Google Chrome and Mozilla Firefox drop support for Adobe Flash in December 2020, the developers are working on porting the game to the Unity engine.
    >
    > The Unity engine is already available for the mobile and Steam versions, if you want to check it out.
    Further information is available [here](https://www.blankmediagames.com/phpbb/viewtopic.php?f=11&t=107706).

In addition to these, the bot has additional functionality with regards to summons, replies, and private messages.

* Delete its reply if the author of the parent comment responds with `!delete`.

* Provide information about the bot when a user queries for `!info`.
    > **NateNate60's ToS_Helper_Bot version $VERSION**
    >
    > I give helpful definitions to certain terms used in Town of Salem.
    If you want me to scan another user's comments for all terms, just ping me.
    I will then scan the comment you replied to for any keywords and give definitions for each one.
    Additionally, if your comment contains "what is", "what's", or the universal trigger word `!def`, I will also reply with any helpful definitions.
    If you find this annoying and would rather not have me reply to anything you say, simply comment `!blacklist` and I will ignore your comments.

* Attempt to perform tasks on the parent comment if it was submitted by any user other than the bot itself.

## Usage

To run this bot, you will need to have Python 3 installed.
First, clone this repository.
Then, install the bot's dependencies.

    pip install -r requirements.txt

Now, you need to configure the bot's authentication.
All authentication configuration is loaded from `config/secrets.py`, which you must create and populate with the following variables:

* `username`
* `password`
* `client_id`
* `client_secret`

Please refer to the [PRAW documentation](https://praw.readthedocs.io/en/latest/getting_started/authentication.html#password-flow) on how to set each variable.

Once that is done, running the `ToS_Helper_Bot.py` script will run the bot as the configured user.

```shell
python3 ToS_Helper_Bot.py
```
