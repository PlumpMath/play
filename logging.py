import datetime
import time


def micro_time():
    """
    Returns the current time since epoch, accurate to the
    value returned by gettimeofday(), usually ~1microsecond.
    """
    now = datetime.datetime.now()
    return long(time.mktime(now.timetuple()) * 1000000 + now.microsecond)


