import logging
import sys
from difflib import SequenceMatcher

from fetch_menu import fetch_menu_image
from read_menu import MenuReader
from chrome_proxy import ChromeProxy
import settings

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

def getLogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    
    file_handler = logging.FileHandler('nirvanam.log', 'a+')
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    return logger

def main():
    logger = getLogger()
    menu_reader = MenuReader(settings.GOOGLE_API_KEY, logger=logger)

    proxy = None
    if settings.PROXY_HOST is not None:
        proxy = ChromeProxy(settings.PROXY_HOST,
                            settings.PROXY_PORT,
                            settings.PROXY_USERNAME,
                            settings.PROXY_PASSWORD)
    
    for image in fetch_menu_image(settings.DATA_DIR,
                                  settings.MENU_IMAGE_NAME,
                                  proxy=proxy):
        logger.debug("Reading menu text...")
        menus = menu_reader.read_menu_image(image)
        logger.debug("Reading menu text...done")
        if menus is not None and len(menus) > 5: break
    
    logger.debug("menu is")
    for menu in menus: logger.debug("- " + menu)

    en_jp = WordDictionary(settings.WORD_DICTIONARY)
    result = []
    for menu in menus:
        jp = japanise_menu(menu, en_jp)
        result.append(jp + ' [' + menu + ']')

    print("")
    print("== Today's Special Lunch Menu ==")
    for menu in result: print(menu)

if __name__ == '__main__':
    main()
