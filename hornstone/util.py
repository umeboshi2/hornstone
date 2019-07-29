from datetime import datetime, date
from configparser import ConfigParser


# https://stackoverflow.com/a/22238613
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode()
    raise TypeError("Type %s not serializable" % type(obj))


def getboolean(value):
    if value.lower() not in ConfigParser.BOOLEAN_STATES:
        raise ValueError('Not a boolean: {}'.format(value))
    return ConfigParser.BOOLEAN_STATES[value.lower()]
