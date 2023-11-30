from abc import ABCMeta, abstractmethod
import re

from anki import collection, notes, models, importing, exporting

from aqt.utils import showInfo
from aqt import mw

from .const import *
from .factory import Factory
        

class NoteFactory(Factory, metaclass=ABCMeta):
    """
    """
    def __init__(self):
        super().__init__()

        self.init_decks()
        self.init_notetypes()

        self.data_key = ''

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
    
    def _get_data_object(self, data_id):
        return self.data['data'][f'{self.data_key}s'][str(data_id)]
    
    def _get_available_ids_for_civ(self, civ):
        return self.data['techtrees'][civ][f'{self.data_key}s']
    
    def _get_string(self, str_id):
        return self.strings[str(str_id)]
    
    def _get_data_help_str(self, data_id):
        return self._get_string(self._get_data_object(data_id)[AOE2_LANG_HELP_ID])
    
    def _get_data_name_str(self, data_id):
        return self._get_string(self._get_data_object(data_id)[AOE2_LANG_NAME_ID])
    
    def _update_note_field(self, note, field, value, note_state):
        current_value = note[field]
        if current_value != value:
            note[field] = value
            if note_state > AOE2_NOTE_STATE_MODIFIED:
                note_state = AOE2_NOTE_STATE_MODIFIED
        return note_state
    
    def get_notes(self):
        new_notes = []
        updated_notes = []
        for civ in self.civ_names:
            note, note_state = self.get_note_civ(civ)
            if note_state == AOE2_NOTE_STATE_NEW:
                new_notes.append(note)
            elif note_state == AOE2_NOTE_STATE_MODIFIED:
                updated_notes.append(note)
            elif note_state == AOE2_NOTE_STATE_UNCHANGED:
                pass
            else:
                raise Exception('Undefined behaviour')
        return new_notes, updated_notes
    
    @abstractmethod
    def get_note_civ(self, civ):
        pass

    def _get_id_str(self, civ):
        return ' '.join([AOE2_IMPORT_TAG, self.tag, civ])
    
    def _get_note(self, civ, model_id):
        note = None
        note_state = AOE2_NOTE_STATE_UNCHANGED
        id_str = self._get_id_str(civ)
        nids = mw.col.find_notes(
            mw.col.build_search_string(f'"{id_str}"', collection.SearchNode(field_name=AOE2_ID))
        )
        if len(nids) == 0:
            note = mw.col.new_note(notetype=mw.col.models.get(model_id))
            note_state = AOE2_NOTE_STATE_NEW
        elif len(nids) == 1:
            note = mw.col.get_note(nids[0])
        else:
            raise Exception(f'Muiltiple existing notes for ID {id_str} found.')
        
        note_state = self._update_note_field(
            note,
            AOE2_ID,
            id_str,
            note_state,
        )

        # Add tags
        note.add_tag(AOE2_IMPORT_TAG)
        note.add_tag(civ)
        note.add_tag(self.tag)
        
        return note, note_state

class RegNoteFactory(NoteFactory, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
    
    def get_note_civ(self, civ):
        note, note_state = self._get_note(self._get_id_str(civ), self.reg_model_id)
        note_state = self._update_note_field(
            note,
            AOE2_REG_QUESTION,
            self._get_question_str(civ),
            note_state,
        )

        return note, note_state
    
    @abstractmethod
    def _get_question_str(self, civ):
        return ''
    
    @abstractmethod
    def _get_pos_str(self, **kwargs):
        return ''
    
    @abstractmethod
    def _get_neg_str(self, **kwargs):
        return ''


class TechTreeRegNoteFactory(RegNoteFactory):
    def __init__(self,
            ids: list[int],
            question: str,
            tag: str,
        ):
        super(TechTreeRegNoteFactory, self).__init__()
        self.deck_id = self.techtree_deck_id
        self.ids = ids
        self.question = question
        self.tag = tag

    def get_note_civ(self, civ):
        note, note_state = super().get_note_civ(civ)
        answer_set = False
        for data_id in self.ids:
            # Check if the civ receives tech
            if data_id in self._get_available_ids_for_civ(civ):
                note_state = self._update_note_field(
                    note,
                    AOE2_REG_ANSWER,
                    self._get_pos_str(data_id=str(data_id)),
                    note_state,
                )
                note_state = self._update_note_field(
                    note,
                    AOE2_REG_DESC,
                    self._get_data_help_str(data_id),
                    note_state,
                )
                answer_set = True
                break
        
        if not answer_set:
            note_state = self._update_note_field(
                note,
                AOE2_REG_ANSWER,
                self._get_neg_str(),
                note_state,
            )
        return note, note_state


class TechNoteFactory(TechTreeRegNoteFactory):
    """e"""
    def __init__(self,
            ids: list[int],
            question: str,
            tag: str,
        ):
        super(TechNoteFactory, self).__init__(ids, question, tag)
        self.data_key = 'tech'

class TechSeriesNoteFactory(TechNoteFactory):
    def __init__(self, ids: list[int], question: str, tag: str):
        super().__init__(ids, question, tag) 

    def _get_question_str(self, civ):
        return self.question.format(civ)

    def _get_pos_str(self, **kwargs):
        return self._get_data_name_str(kwargs['data_id'])
    
    def _get_neg_str(self, **kwargs):
        return 'Not Available'
    

class TechSingleNoteFactory(TechNoteFactory):
    def __init__(self, ids: list[int], tag: str):
        question = 'Do {0} get {1}?'
        super().__init__(ids, question, tag) 

    def _get_question_str(self, civ):
        return self.question.format(
            civ,
            self._get_data_name_str(self.ids[0]),
        )

    def _get_pos_str(self, **kwargs):
        return 'Yes'
    
    def _get_neg_str(self, **kwargs):
        return 'No'    
    

class UnitNoteFactory(TechTreeRegNoteFactory):
    def __init__(self,
            ids: list[int],
            question: str,
            tag: str,
        ):
        super(UnitNoteFactory, self).__init__(ids, question, tag)
        self.data_key = 'unit'


class UnitSeriesNoteFactory(UnitNoteFactory):
    def __init__(self,
            ids: list[int],
            question: str,
            tag: str,
        ):
        super().__init__(ids, question, tag)

    def _get_question_str(self, civ):
        return self.question.format(civ)

    def _get_pos_str(self, **kwargs):
        return self._get_data_name_str(kwargs['data_id'])
    
    def _get_neg_str(self, **kwargs):
        return 'Not Available'
    
class ClozeNoteFactory(NoteFactory, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()

    def get_note_civ(self, civ):
        note, note_state = super()._get_note(civ, self.cloze_model_id)
            
        note_state = self._update_note_field(
            note,
            AOE2_CLOZE_TEXT,
            self._get_text_str(civ),
            note_state,
        )
        return note, note_state
        
    
    @abstractmethod
    def _get_text_str(self, civ):
        return ''
    
    
class CivBonusNoteFactory(ClozeNoteFactory):
    def __init__(self):
        super().__init__()
        self.deck_id = self.techtree_deck_id
        self.tag = 'civbonus'

    def _get_civ_bonuses(self, bonus_str):
        bonus_strs = [x.strip() for x in bonus_str.replace('\n','').replace(u'\u2022', ' ').split('<br>') if len(x) > 0]
        uu_idx, ut_idx, tb_idx = None, None, None
        for i in range(len(bonus_strs)):
            if 'Unique Unit' in bonus_strs[i]: uu_idx = i
            if 'Unique Techs' in bonus_strs[i]: ut_idx = i
            if 'Team Bonus' in bonus_strs[i]: tb_idx = i

        assert(uu_idx is not None and ut_idx is not None and tb_idx is not None)

        return bonus_strs[1:uu_idx], bonus_strs[tb_idx+1:]

    def _get_text_str(self, civ):
        civ_help_id = self.data[AOE2_CIV_HELP][str(civ)]
        bonuses, team_bonuses = self._get_civ_bonuses(self._get_string(civ_help_id))
        print(bonuses)
        
        return ''
    
