from enum import Enum
from productive import TimeEntry
from typing import Union
import pickle

FACET_DICTIONARY_FILE = "facet.dictionary"


class Actions(Enum):
    START = 'start'
    STOP = 'stop'


class FacetAction:

    def __init__(self, action: Actions, time_entry: Union[None, TimeEntry]):
        self.time_entry = time_entry
        self.action = action


class Storage:

    def __init__(self):
        self.facet_dictionary = {}

    def add_facet_action(self, facet: int, facet_action: FacetAction):
        self.facet_dictionary[facet] = facet_action
        self.persist()

    def get_facet_action(self, facet: int) -> FacetAction:
        return self.facet_dictionary.get(facet)

    def load(self):
        try:
            with open(FACET_DICTIONARY_FILE, 'r+b') as handler:
                try:
                    self.facet_dictionary = pickle.load(handler)
                except EOFError:
                    self.facet_dictionary = {}
        except FileNotFoundError:
            self.facet_dictionary = {}
            self.persist()

    def persist(self):
        with open(FACET_DICTIONARY_FILE, 'w+b') as handler:
            pickle.dump(self.facet_dictionary, handler)

    def reset(self):
        self.facet_dictionary = {}
        self.persist()
