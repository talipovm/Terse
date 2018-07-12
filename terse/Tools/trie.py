from Top import Top

# nearly a carbon-copy of https://stackoverflow.com/a/11016430/1898580
class Trie(Top):
    def __init__(self, v):
        super().__init__()
        self._end = '_end_'
        self.trie = self.make_trie(v)

    def make_trie(self,words):
        root = dict()
        for word in words:
            current_dict = root
            for letter in word:
                current_dict = current_dict.setdefault(letter, {})
            current_dict[self._end] = self._end
        return root

    def find(self, word):
        current_dict = self.trie
        match = ''
        for letter in word:
            if letter in current_dict:
                current_dict = current_dict[letter]
                match += letter
                if self._end in current_dict:
                    return match
            else:
                return None