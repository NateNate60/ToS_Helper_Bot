import datetime
import time
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