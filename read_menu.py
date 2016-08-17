#!/usr/bin/python3

import logging

import requests
import json
import base64

# Refer [Google Cloud Vision API](https://cloud.google.com/vision/reference/rest/)
GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
SHOP_NAMES = [ '有明店', 'ARIAKE', 'Ariake' ]

def flatten(lst):
    flat = []
    for i in lst:
        if isinstance(i, list):
            flat.extend(i)
        else:
            flat.append(i)
    return flat

def load_image(image_path):
    bs = None
    with open(image_path, 'rb') as f:
        bs = base64.b64encode(f.read())
    return bs

def make_request_body(image_content):
    req_body = json.dumps({
        'requests': [{
            'image': {
                'content': image_content.decode('utf-8')
            },
            'features': [{
                'type': 'TEXT_DETECTION',
                'maxResults': 100
            }]
        }]
    })
    return req_body

def split_desc(desc):
    texts = desc.split('\n')
    texts = flatten([ x.split(',') for x in texts ])
    texts = flatten([ x.split('、') for x in texts ])
    texts = [ x.strip() for x in texts if len(x) > 0 ]
    return texts

def get_menu_of(descs, shop):
    for i in range(len(descs)):
        d = descs[i]
        if d.find(shop) > -1:
            return descs[i+1:]
    return None    

def is_comment(chars):
    matched = 0
    for c in chars:
        if '一' <= c and c <= '龠':
            matched += 1
            break
    for c in chars:
        if 'ぁ' <= c and c <= 'ん':
            matched += 1
            break
    for c in chars:
        if 'ァ' <= c and c <= 'ヴ':
            matched += 1
            break
    return matched > 1
    
def remove_comment(toks):
    """
    メニューに混入したコメントを除外する。
    漢字・ひらがな・カタカナの2種類以上が含まれていたらコメントとみなす。
    """
    return list(filter(lambda x: not is_comment(x), toks))

def is_japanese_char(c):
    if '一' <= c and c <= '龠': return True
    if 'ぁ' <= c and c <= 'ん': return True
    if 'ァ' <= c and c <= 'ヴ': return True
    if 'ー' <= c and c <= 'ー': return True
    return False

def is_english_name(name):
    alpha = filter(lambda c: 'A' <= c <= 'Z' or 'a' <= c <= 'z', name)
    if len(list(alpha)) < 2: return False
    return True

def only_english_name(name):
    name = filter(lambda c: not is_japanese_char(c), name)
    name = ''.join(name)
    return name.strip()

def filter_menu(menus):
    menus = map(only_english_name, menus)
    return list(filter(lambda m: m is not None and is_english_name(m), menus))

class MenuReader:
    def __init__(self, google_api_key, logger=None):
        self.google_api_key = google_api_key
        self.logger = logger or logging.getLogger(__name__)

    def detect_text(self, image_content):
        api_uri = GOOGLE_CLOUD_VISION_API_URL + self.google_api_key
        req_body = make_request_body(image_content)
        res = requests.post(api_uri, data=req_body)
        if not res.ok:
            self.logger.error('Error: {0}'.format(res.status_code))
            return None        
        return res.json()

    def get_menu(self, image_content):
        json = self.detect_text(image_content)
        desc = json['responses'][0]['textAnnotations'][0]['description']
        self.logger.debug('ocr description={}'.format(desc))
        toks = split_desc(desc)
        for tok in toks: self.logger.debug('ocr tok={}'.format(tok))
        for shop_name in SHOP_NAMES:
            menus = get_menu_of(toks, shop_name)
            if menus is not None: break
        if menus is None:
            self.logger.error("failed to get menu: json=" + str(json))
            return None
        menus = filter_menu(menus)
        return menus

    def read_menu_image(self, imagefile):
        image_content = load_image(imagefile)
        menus = self.get_menu(image_content)
        return menus

# def main():
#     menus = read_menu_image(MENU_IMAGE_PATH)
#     for menu in menus:
#         print(menu)
# 
# if __name__ == '__main__':
#     main()

    
