# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *

from .factory.notes import *
from .configs import *

from anki.collection import AddNoteRequest
from aqt.operations import CollectionOp


def aoe2_ui_action() -> None:
    CollectionOp(
        mw,
        op=aoe2_run,
    ).success(lambda x: showInfo('Finished')).run_in_background()
   

def aoe2_on_success(args) -> None:
    showInfo(f"my_background_op returned")

def add_notes(factory_class, cfg, col):
    factory = factory_class(
        path=__path__[0],
        **cfg
    )
    new_notes, updated_notes = factory.get_notes()
    col.add_notes([AddNoteRequest(note, factory.get_deck_id()) for note in new_notes])
    col.update_notes(updated_notes)

def aoe2_run(col) -> None:
    pos = col.add_custom_undo_entry("import aoe2")

    for cfg in tech_note_series_cfgs:
        add_notes(TechSeriesNoteFactory, cfg, col)
        col.merge_undo_entries(pos)
    for cfg in tech_note_single_cfgs:
        add_notes(TechSingleNoteFactory, cfg, col)
        col.merge_undo_entries(pos)
    for cfg in unit_series_note_cfgs:
        add_notes(UnitSeriesNoteFactory, cfg, col)
        col.merge_undo_entries(pos)
    for cfg in unit_single_note_cfgs:
        add_notes(UnitSingleNoteFactory, cfg, col)
        col.merge_undo_entries(pos)

    add_notes(CivBonusNoteFactory, {}, col)

    return  col.merge_undo_entries(pos)


# create a new menu item, "test"
action = QAction("Import aoe2", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, aoe2_ui_action)
# and add it to the tools menu
mw.form.menuTools.addAction(action)