import tlogging as log
def getevaders(r, submitters) :
    """
    Scrapes usernames from r/evadersToS for shadowbanning
    :param r: the Reddit session.
    :return: None
    """
    for post in r.subreddit('evaderstos').new(limit = 50) :
        shadowban(post.author.name, submitters, r)
        for comment in post.comments :
            try :
                shadowban(comment.author.name, submitters, r)
            except AttributeError :
                pass
    
def shadowban(user, submitters, r) :
    """
    Shadowban a user.
    :param user: the user 
    :param submitters: the SQLITE database of submitters
    :param r: the Reddit session
    """
    with submitters:
            cursor = submitters.execute("SELECT quantity FROM submitters WHERE username=?",
                                    (user.lower(), ))
            #submitters.commit()
            result = cursor.fetchone()
            if result is None:
                q = 0
            else:
                (q, ) = result
            if (not q < 0) and user != "Official_Moonman":
                submitters.execute("INSERT INTO submitters (username, quantity) VALUES (?, -99999)"
                                    " ON CONFLICT (username) DO UPDATE SET quantity = -99999",
                                    (user.lower(), ))
                submitters.commit()
                r.subreddit('townofsalemgame').message("Shadowban notice", user + " has been shadowbanned.")
                log.log("Shadowbanned", user)
