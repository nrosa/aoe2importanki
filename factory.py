import requests

class Factory(object):
    _data = None
    _strings = None

    @classmethod
    def _get_data(cls):
        if cls._data is None:
            cls._data = requests.get('https://aoe2techtree.net/data/data.json').json()
        return cls._data

    @classmethod
    def _get_strings(cls):
        if cls._strings is None:
            cls._strings = requests.get('https://aoe2techtree.net/data/locales/en/strings.json').json()
        return cls._strings

    def __init__(self):
        super(Factory, self).__init__()
        self.data = Factory._get_data()
        self.strings = Factory._get_strings()
        self.civ_names = self.data['civ_names'].keys()