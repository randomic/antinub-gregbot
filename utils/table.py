"""
Abstraction of TinyDB table for storing config
"""
from tinydb import Query


class KeyValueTable:
    """Wrapper around a TinyDB table.

    """

    def __init__(self, tdb, name='_default'):
        self.table = tdb.table(name)
        self.setting = Query()

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
        if self.table.contains(self.setting.key == key):
            self.table.update({'value': value}, self.setting.key == key)
        else:
            self.table.insert({'key': key, 'value': value})

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)
