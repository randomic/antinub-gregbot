"""
Abstraction of TinyDB table for storing config
"""
from tinydb import Query


class Config:
    """Wrapper around a TinyDB table called 'config'.

    """
    def __init__(self, tdb):
        self.table = tdb.table('config')
        self.setting = Query()

    def get(self, name):
        """Get the value of named setting or None if it doesn't exist.

        """
        result = self.table.get(self.setting.name == name)
        if result:
            return result['value']
        else:
            return None

    def set(self, name, value):
        """Insert or update named setting with given value.

        """
        if self.table.contains(self.setting.name == name):
            self.table.update({'value': value}, self.setting.name == name)
        else:
            self.table.insert({'name': name, 'value': value})
