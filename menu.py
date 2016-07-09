#!/usr/bin/python3

import requests
import json
import base64

# Refer [Google Cloud Vision API](https://cloud.google.com/vision/reference/rest/)
GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
API_KEY = 'Your API Key'
MENU_IMAGE_PATH = './image/menu.jpg'
SHOP_NAME = '有明店'

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

def get_menu_of(descs, shop):
    for i in range(len(descs)):
        d = descs[i]
        if d.find(shop) > -1:
            return descs[i+1:]
    return None
    
def get_menu(image_content):
    json = detect_text(image_content)
    desc = json['responses'][0]['textAnnotations'][0]['description']
    menus = get_menu_of(desc.split('\n'), SHOP_NAME)
    return menus

def main():
    image_content = load_image(MENU_IMAGE_PATH)
    menus = get_menu(image_content)
    for menu in menus:
        print(menu)

if __name__ == '__main__':
    main()
