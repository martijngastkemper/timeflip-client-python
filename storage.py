import pickle

FACET_DICTIONARY_FILE = "facet.dictionary"


class Repository:

    def __init__(self):
        self.facet_dictionary = {}

    def calibrate_facet(self, facet: int, icon: str):
        self.facet_dictionary[facet] = icon
        self.persist()

    def get_icon(self, facet: int) -> str:
        print(self.facet_dictionary)
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
