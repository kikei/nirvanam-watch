#!/usr/bin/python3

import requests
import json
import base64

# Refer [Google Cloud Vision API](https://cloud.google.com/vision/reference/rest/)
GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
API_KEY = 'AIzaSyB1dR9bjQ-ojg-TAO8KkZAjyr79r819A14'
MENU_IMAGE_PATH = './image/menu.jpg'
SHOP_NAME = '有明店'

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
    
def detect_text(image_content):
    api_uri = GOOGLE_CLOUD_VISION_API_URL + API_KEY
    req_body = make_request_body(image_content)
    res = requests.post(api_uri, data=req_body)
    if not res.ok:
        print('Error: {0}'.format(res.status_code))
        return None        
    return res.json()

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

def is_english_name(name):
    for c in name:
        if '一' <= c and c <= '龠': return False 
        if 'ぁ' <= c and c <= 'ん': return False
        if 'ァ' <= c and c <= 'ヴ': return False
    return True

def filter_menu(menus):
    return list(filter(is_english_name, menus))

def get_menu(image_content):
    json = detect_text(image_content)
    desc = json['responses'][0]['textAnnotations'][0]['description']
    toks = split_desc(desc)
    menus = get_menu_of(toks, SHOP_NAME)
    menus = filter_menu(menus)
    return menus

def read_menu_image(imagefile):
    image_content = load_image(imagefile)
    menus = get_menu(image_content)
    return menus

def main():
    menus = read_menu_image(MENU_IMAGE_PATH)
    for menu in menus:
        print(menu)

if __name__ == '__main__':
    main()

    