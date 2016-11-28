import ass
from .utility import *

@property
def dialog(self):
    return [e for e in self.events if type(e) is ass.document.Dialogue]

@property
def text(self):
    dialog_events = [e.text for e in self.dialog]
    document_text = u"\n".join(dialog_events)
    return document_text

def doc_len(self):
    return len(self.dialog)

ass.document.Document.dialog = dialog
ass.document.Document.text = text
ass.document.Document.__len__ = doc_len
