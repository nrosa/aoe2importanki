import requests
import json
# import anki
from anki import collection, notes, models, importing, exporting

from aqt.utils import showInfo
from aqt import mw

from .const import *

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
        

class NoteFactory(Factory):
    """
    """
    def __init__(self):
        super().__init__()

        self.init_decks()
        self.init_notetypes()

    def init_decks(self):
        """
        Check to see if the aoe2 and techtree decks exist and create if they do not
        """
        self.base_deck_id = mw.col.decks.add_normal_deck_with_name(BASE_DECK).id
        self.techtree_deck_id = mw.col.decks.add_normal_deck_with_name(TECH_TREE_DECK).id

    def init_notetypes(self):
        # TODO create the aoe2 notetypes rather than relying on them already existing
        models = mw.col.models.all_names_and_ids()
        self.cloze_model_id = None
        self.reg_model_id = None
        for model in models:
            model
            if model.name == AOE2_CLOZE_NOTE:
                self.cloze_model_id = model.id
            if model.name == AOE2_REG_NOTE:
                self.reg_model_id = model.id

        if self.cloze_model_id is None or self.reg_model_id is None:
            raise Exception("Aoe2 note types can not be found.")
        

class RegNoteFactory(NoteFactory):
    def __init__(self):
        super().__init__()

    def get_notes(self):
        new_notes = []
        updated_notes = []
        for civ in self.civ_names:
            note, new_flag = self.get_note_civ(civ)
            if new_flag:
                new_notes.append(note)
            else:
                updated_notes.append(note)
        return new_notes, updated_notes
    
    def get_note_civ(self, civ):
        # Check for existing note
        note_str_id = ' '.join([AOE2_IMPORT_TAG, self.tag, civ])
        nids = mw.col.find_notes(
            mw.col.build_search_string(note_str_id, collection.SearchNode(field_name=AOE2_REG_ID))
        )
        new_flag = False
        note = None
        if len(nids) == 0:
            note = mw.col.new_note(notetype=mw.col.models.get(self.reg_model_id))
            new_flag = True
        elif len(nids) == 1:
            note = mw.col.get_note(nids[0])
        else:
            raise Exception('Muiltiple existing notes for ID {note_str_id} found.')
        
        note[AOE2_REG_QUESTION] = self._get_question_str(civ)
        note[AOE2_REG_ID] = ' '.join([AOE2_IMPORT_TAG, self.tag, civ])
        note[AOE2_REG_ANSWER] = self._get_neg_str()
        
        # Add tags
        note.add_tag(AOE2_IMPORT_TAG)
        note.add_tag(self.tag)
        note.add_tag(civ)

        return note, new_flag
    
    def _get_question_str(self, civ):
        return ''
    
    def _get_pos_str(self, **kwargs):
        return ''
    
    def _get_neg_str(self, **kwargs):
        return ''


class TechTreeRegNoteFactory(RegNoteFactory):
    def __init__(self) -> None:
        super(TechTreeRegNoteFactory, self).__init__()
        self.deck_id = self.techtree_deck_id


class TechNoteFactory(TechTreeRegNoteFactory):
    """e"""
    def __init__(self,
            ids: list[int],
            question: str,
            tag: str,
        ):
        super(TechNoteFactory, self).__init__()
        self.ids = ids
        self.question = question
        self.tag = tag

    def get_note_civ(self, civ):
        note, new_flag = super().get_note_civ(civ) 
        for tech_id in self.ids:
            # Check if the civ receives tech
            if tech_id in self.data['techtrees'][civ]['techs']:
                # note[AOE2_REG_ANSWER] = ['internal_name']
                note[AOE2_REG_ANSWER] = self._get_pos_str(tech_id=str(tech_id))
                help_lang_id = self.data['data']['techs'][str(tech_id)]['LanguageHelpId']
                note[AOE2_REG_DESC] = self.strings[str(help_lang_id)]
                break
        return note, new_flag
            

class TechNoteSeriesFactory(TechNoteFactory):
    def __init__(self, ids: list[int], question: str, tag: str):
        super().__init__(ids, question, tag) 

    def _get_question_str(self, civ):
        return self.question.format(civ)

    def _get_pos_str(self, **kwargs):
        lang_id = self.data['data']['techs'][kwargs['tech_id']]['LanguageNameId']
        return self.strings[str(lang_id)]
    
    def _get_neg_str(self, **kwargs):
        return 'Not Available'
    

class TechNoteSingleFactory(TechNoteFactory):
    def __init__(self, ids: list[int], tag: str):
        question = 'Do {0} get {1}?'
        super().__init__(ids, question, tag) 

    def _get_question_str(self, civ):
        tech_lang_id = self.data['data']['techs'][str(self.ids[0])]['LanguageNameId']
        return self.question.format(
            civ,
            self.strings[str(tech_lang_id)],
        )

    def _get_pos_str(self, **kwargs):
        return 'Yes'
    
    def _get_neg_str(self, **kwargs):
        return 'No'    
        

        
if __name__ == '__main__':
   pass
