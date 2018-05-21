'''
Abstraction of TinyDB table for storing config
'''
from tinydb import Query


class KeyValueTable:
    """Wrapper around a TinyDB table.

    """
    setting = Query()

    def __init__(self, tdb, name='_default'):
        self.table = tdb.table(name)

    def get(self, key, default=None):
        """Get the value of named setting or default if it doesn't exist.

        """
        result = self.table.get(self.setting.key == key)
        if result is not None:
            return result['value']
        return default

    def set(self, key, value):
        """Insert or update named setting with given value.

        """
        self.table.upsert({
            'key': key,
            'value': value
        }, self.setting.key == key)

    def __getitem__(self, key):
        result = self.table.get(self.setting.key == key)
        if result is not None:
            return result['value']
        raise KeyError(key)

    def __setitem__(self, key, value):
        return self.set(key, value)
