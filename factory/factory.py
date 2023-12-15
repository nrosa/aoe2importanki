import json, os

class DataPath(object):
    data = 'aoe2techtree/data/data.json'
    strings = 'aoe2techtree/data/locales/en/strings.json'



class Factory(object):
    _data = None
    _strings = None

    @classmethod
    def _get_data(cls, path):
        if cls._data is None:
            with open(os.path.join(path, DataPath.data)) as fp:
                cls._data = json.load(fp)
        return cls._data

    @classmethod
    def _get_strings(cls, path):
        if cls._strings is None:
            with open(os.path.join(path, DataPath.strings)) as fp:
                cls._strings = json.load(fp)
        return cls._strings

    def __init__(self, path):
        super(Factory, self).__init__()
        self.data = Factory._get_data(path)
        self.strings = Factory._get_strings(path)
        # TODO remove hc string
        self.civ_names = self.data['civ_names'].keys()