from abc import ABCMeta, abstractmethod

from aqt import mw

class ModelName(object):
    regular = 'Age of Empires 2 Regular'
    double = 'Age of Empires 2 Double'
    cloze = 'Age of Empires 2 Cloze'

class NoteModel(object, metaclass=ABCMeta):
    @abstractmethod
    def _create_new_model(self):
        return None
    
    def _get_model_id(self) -> int:
        if self.model_id is None:
            self.model_id = mw.col.models.id_for_name(self._get_deck_name())
            if self.model_id is None:
                self.model_id = self._create_new_model()   
        return self.model_id
    

class RegNoteModel(NoteModel):
    model_id = None

    def _create_new_model(self):
        pass
        # model = mw.col.models.new(ModelNameEnum.regular)
    

