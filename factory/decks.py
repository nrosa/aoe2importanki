from abc import ABCMeta, abstractmethod

from aqt import mw

class DeckNameEnum(object):
    BASE = 'Age of Empires 2 (import tool)'
    TECHTREE = 'Tech trees'

class NoteDeck(object, metaclass=ABCMeta):
    @abstractmethod
    def _get_deck_name(self) -> str:
        return ''
    
    def get_deck_id(self) -> int:
        if self.deck_id is None:
            self.deck_id = mw.col.decks.id_for_name(self._get_deck_name())
            if not self.deck_id:
                deck = mw.col.decks.new_deck()
                deck.name = self._get_deck_name()
                self.deck_id = mw.col.decks.add_deck(deck).id
            
        return self.deck_id
    
    def _join(self, *args: list[DeckNameEnum]):
        return '::'.join(args)
    
    
class TechTreeDeck(NoteDeck):
    deck_id = None

    def _get_deck_name(self) -> int:
        return self._join(DeckNameEnum.BASE, DeckNameEnum.TECHTREE)