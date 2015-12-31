import ass
from .utility import *

@property
def text(self):
    dialog_events = [e.text for e in self.events if type(e) is ass.document.Dialogue]
    document_text = u"\n".join(dialog_events)
    return document_text


ass.document.Document.text = text
