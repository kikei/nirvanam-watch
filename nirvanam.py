from fetch_menu import fetch_menu_image
from read_menu import read_menu_image

MENU_IMAGE_DIR = './download'
MENU_IMAGE_NAME = 'menu.jpg'

def japanise_word(name):
    d = dict()
    d['as'] = ''
    d['aloo'] = 'アル'
    d['biryani'] = 'ビリヤニ'
    d['black'] = '黒'
    d['butter'] = 'バーター'
    d['carrot'] = '人参'
    d['chana'] = 'チャナ'
    d['chettinad'] = 'チェッティナド'
    d['chicken'] = 'チキン'
    d['chocolate'] = 'チョコレート'
    d['curry'] = 'カレー'
    d['dal'] = 'ダル'
    d['daliya'] = 'ダリヤ'
    d['daikon'] = 'ダイコン'
    d['dessert'] = 'デザート'
    d['do'] = 'ド'
    d['flavoured'] = ''
    d['fry'] = 'フライ'
    d['garlic'] = 'ガーリック'
    d['gourd'] = 'ウリ'
    d['green'] = 'グリン'
    d['hyderabadi'] = 'ハイドラバディ'
    d['jalfrezi'] = 'ジャルフレジ'
    d['kadai'] = 'カダイ'
    d['kebab'] = 'ケバブ'
    d['keema'] = 'キマ'
    d['lemon'] = 'レモン'
    d['lobiya'] = 'ロビヤ'
    d['masala'] = 'マサラ'
    d['Mushroom'] = 'マスルム'
    d['methi'] = 'メティ'
    d['mixed'] = 'ミックス'
    d['moong'] = 'モング'
    d['moussee'] = 'ムース'
    d['mutton'] = 'マトン'
    d['nan'] = 'ナン'
    d['naan'] = 'ナン'
    d['palak'] = 'パラク'
    d['peas'] = 'ピス'
    d['payasam'] = 'パヤサム'
    d['pepper'] = 'ペッパ'
    d['pineapple'] = 'バイナップル'
    d['pulao'] = 'プラウ'
    d['pyaaz'] = 'ピヤズ'
    d['raitha'] = 'ライタ'
    d['rajma'] = 'ラッマ'
    d['rice'] = 'ライス'
    d['sambar'] = 'サンバル'
    d['seafood'] = 'シーフード'
    d['snake'] = 'ヘビ'
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
        print("Reading menu text...")
        menus = read_menu_image(image)
        print("Reading menu text...done")
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
