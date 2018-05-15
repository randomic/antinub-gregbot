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

    def get(self, key):
        """Get the value of named setting or None if it doesn't exist.

        """
        result = self.table.get(self.setting.key == key)
        if result:
            return result['value']
        return None

    def set(self, key, value):
        """Insert or update named setting with given value.

        """
        self.table.upsert({
            'key': key,
            'value': value
        }, self.setting.key == key)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)
