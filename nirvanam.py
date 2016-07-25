from fetch_menu import fetch_menu_image
from read_menu import read_menu_image

MENU_IMAGE_DIR = './download'
MENU_IMAGE_NAME = 'menu.jpg'

def japanise_word(name):
    d = dict()
    d['as'] = ''
    d['aloo'] = 'アル'
    d['butter'] = 'バーター'
    d['carrot'] = '人参'
    d['chettinad'] = 'チェッティナド'
    d['chicken'] = 'チキン'
    d['curry'] = 'カレー'
    d['dal'] = 'ダル'
    d['dessert'] = 'デザート'
    d['flavoured'] = ''
    d['fry'] = 'フライ'
    d['jalfrezi'] = 'ジャルフレジ'
    d['kadai'] = 'カダイ'
    d['keema'] = 'キマ'
    d['lemon'] = 'レモン'
    d['methi'] = 'メティ'
    d['mutton'] = 'マトン'
    d['nan'] = 'ナン'
    d['naan'] = 'ナン'
    d['palak'] = 'パラク'
    d['peas'] = 'ピス'
    d['payasam'] = 'パヤサム'
    d['pepper'] = 'ペッパ'
    d['pineapple'] = 'バイナップル'
    d['pulao'] = 'プラウ'
    d['rajma'] = 'ラッマ'
    d['rice'] = 'ライス'
    d['sambar'] = 'サンバル'
    d['seafood'] = 'シーフード'
    d['tadka'] = 'タッカ'
    d['tapioca'] = 'タピオカ'
    d['vada'] = 'ワダ'
    d['vegetable'] = 'ベジタブル'
    if name in d:
        return d[name]
    else:
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

def japanise_menu(name):
    words = to_words(name)
    words = filter(lambda w: w != ' ', words)
    jpmenu = []
    for w in words:
        jp = japanise_word(w.lower())
        if jp is None:
            jpmenu.append(w)
        else:
            jpmenu.append(jp)
    return "".join(jpmenu)

def main():
    for image in fetch_menu_image(MENU_IMAGE_DIR, MENU_IMAGE_NAME):
        menus = read_menu_image(image)
        if menus is not None: break
    
    print("menu is")
    for menu in menus: print("- " + menu)
    
    result = []
    for menu in menus:
        jp = japanise_menu(menu)
        result.append(jp + ' [' + menu + ']')

    print("")
    print("== Today's Special Lunch Menu ==")
    for menu in result: print(menu)

if __name__ == '__main__':
    main()
