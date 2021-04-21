import datetime
import time
def log(*msg, **kwargs):
    """
    Log the given message.
    :param msg: The message to log.
    :return: None.
    """
    print (datetime.datetime.fromtimestamp(time.time()).strftime('[%Y-%m-%d %H:%M:%S]'), *msg, **kwargs)
