from difflib import SequenceMatcher

from fetch_menu import fetch_menu_image
from read_menu import read_menu_image

MENU_IMAGE_DIR = './download'
MENU_IMAGE_NAME = 'menu.jpg'
WORD_DICTIONARY = 'res/en-jp_dictionary.csv'

def word_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

class WordDictionary:

    def __init__(self, filename):        
        d = dict()
        with open(filename, encoding='utf-8') as file:
            lines = file.readlines()
            lines = map(lambda a: a.split(','), lines)
            lines = filter(lambda a: len(a) >= 1 and len(a[0]) >= 1, lines)
            for line in lines:
                d[line[0]] = line[1].strip()
        self.dictionary = d
    
    def lookup(self, word, allow_similarity=1.0):
        if word in self.dictionary:
            return self.dictionary[word]
        for key in self.dictionary.keys():
            similarity = word_similarity(key, word)
            if similarity >= allow_similarity:
                return self.dictionary[key]
        return None

def to_words(name):
    words = []
    i = 0
    while i < len(name):
        if name[i].isalpha():
            b = i
            while i < len(name) and name[i].isalpha(): i += 1
            words.append(name[b:i])
        else:
            words.append(name[i])
            i += 1
    return words

def japanise_menu(name, word_dict):
    words = to_words(name)
    words = filter(lambda w: w != ' ', words)
    jpmenu = []
    for w in words:
        jp = word_dict.lookup(w.lower(), allow_similarity=0.8)
        if jp is None:
            jpmenu.append(w)
        else:
            jpmenu.append(jp)
    return "".join(jpmenu)

def main():
    for image in fetch_menu_image(MENU_IMAGE_DIR, MENU_IMAGE_NAME):
        print("Reading menu text...")
        menus = read_menu_image(image)
        print("Reading menu text...done")
        if menus is not None: break
    
    print("menu is")
    for menu in menus: print("- " + menu)

    en_jp = WordDictionary(WORD_DICTIONARY)
    result = []
    for menu in menus:
        jp = japanise_menu(menu, en_jp)
        result.append(jp + ' [' + menu + ']')

    print("")
    print("== Today's Special Lunch Menu ==")
    for menu in result: print(menu)

if __name__ == '__main__':
    main()
