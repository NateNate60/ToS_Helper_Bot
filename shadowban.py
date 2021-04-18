import tlogging as log
def getevaders(r, submitters) :
    """
    Scrapes usernames from r/evadersToS for shadowbanning
    :param r: the Reddit session.
    :return: None
    """
    for post in r.subreddit('evaderstos').new(limit = 50) :
        shadowban(post.author.name, submitters)
        for comment in post.comments :
            if comment is None :
                pass
            shadowban(comment.author.name, submitters)
    
def shadowban(user, submitters) :
    """
    Shadowban a user.
    :param user: the user 
    :param submitters: the SQLITE database of submitters
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

                log.log("Shadowbanned", user)
