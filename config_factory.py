from abc import ABCMeta, abstractmethod
from .factory import Factory


class ConfigFactory(Factory, metaclass=ABCMeta):
    '''
    WIP
    '''
    def __init__(self):
        super().__init__()

    @abstractmethod
    def _find_ids(self):
        pass

    def _get_single_cfg_id(self, id):
        pass

    def _get_single_cfgs_ids(self, ids):
        return [self._get_cfg_id(x) for x in ids]
    
    def get_single_cfgs(self):
        return self._get_cfgs_ids(self.ids)
    
    def _get_series_cfg_id(self, id):
        pass

    def _get_series_cfgs_ids(self, ids):
        return [self._get_cfg_id(x) for x in ids]
    
    def get_series_cfgs(self):
        return self._get_cfgs_ids(self.ids)

class TechConfigFactory(ConfigFactory):
    '''
    WIP
    '''
    def __init__(self):
        super().__init__()

    def _find_ids(self):
        pass