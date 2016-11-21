#!/usr/bin/python3

import logging

import requests
import json
import base64

# Refer [Google Cloud Vision API](https://cloud.google.com/vision/reference/rest/)
GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
SHOP_NAMES = [ '有明店', 'ARIAKE', 'Ariake' ]

# Priority coefficient for clustering words
CLUSTERING_HORIZONTAL_PRIORITY = 2.0

# Line height to determine if two words are on same line.
LINE_BREAKING_HEIGHT = 10

def flatten(lst):
    flat = []
    for i in lst:
        if isinstance(i, list):
            flat.extend(i)
        else:
            flat.append(i)
    return flat

def split_by(lst, d):
    """
    Split list by d as delimiter.
    list<a> -> list<list<a>>
    """
    xs = []
    while d in lst:
        idx = lst.index(d)
        if (idx > 0): xs.append(lst[:idx])
        lst = lst[idx+1:]
    if len(lst) > 0: xs.append(lst)
    return xs

def load_image(image_path):
    bs = None
    with open(image_path, 'rb') as f:
        bs = base64.b64encode(f.read())
    return bs

def is_shop_name(text):
    for word in SHOP_NAMES:
        if word in text: return True
    return False

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
    
def is_symbol(c):
    return not c.isalnum() or is_japanese_word(c)

def is_japanese_char(c):
    if '一' <= c and c <= '龠': return True
    if 'ぁ' <= c and c <= 'ん': return True
    if 'ァ' <= c and c <= 'ヴ': return True
    if 'ー' <= c and c <= 'ー': return True
    return False

def is_japanese_word(w):
    for c in w:
        if is_japanese_char(c): return True
    return False

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

    def cancel_noise(self, annotations):
        from scipy.spatial.distance import pdist
        from scipy.cluster.hierarchy import ward, dendrogram
        # from matplotlib.pyplot import show
        
        def calc_center(annotation):
            vs = annotation['boundingPoly']['vertices']
            return [ (vs[0]['x'] + vs[2]['x']) / 2.0 /
                     CLUSTERING_HORIZONTAL_PRIORITY,
                     (vs[0]['y'] + vs[2]['y']) / 2.0]
        descs = list(map(calc_center, annotations))

        dists = pdist(descs)
        clusters = ward(dists)
        
        # print('drawing dendrogram')
        # dendrogram(clusters)
        # show()

        def get_label(t):
            if is_shop_name(t):
                return +1
            elif 'Indicated' in t:
                return -1
            else:
                return 0

        result = []
        for i in range(0, len(annotations)):
            self.logger.debug('{0} {1}'.format(annotations[i]['description'],
                                               get_label(annotations[i]['description'])))
            result.append((get_label(annotations[i]['description']), [i]))

        indexes = None
        # Get only menu
        for i in range(0, len(clusters)):
            cl = clusters[i]
            i0 = int(cl[0])
            i1 = int(cl[1])

            a = None
            if result[i0][0] == 0:
                if result[i1][0] == -1:
                    a = (-1, [])
                else:
                    a = (result[i1][0], result[i0][1] + result[i1][1])
            elif result[i0][0] == -1:
                if result[i1][0] == +1:
                    indexes = result[i1][1]; break
                else:
                    a = (-1, [])
            else: # result[i0][0] == +1
                if result[i1][0] == -1:
                    indexes = result[i0][1]; break
                else:
                    a = (result[i0][0], result[i0][1] + result[i1][1])
            result.append(a)

        self.logger.debug('indexes={0}'.format(indexes))

        if indexes is None:
            self.logger.error('cannot find menu')
            return []
        
        indexes.sort()
        annotations = list(map(lambda i: annotations[i], indexes))
        return annotations

    def group_by_line(self, annotations):
        def position_y(annotation):
            vs = annotation['boundingPoly']['vertices']
            return (vs[0]['y'] + vs[2]['y']) / 2.0

        def group_by_line(annotations):
            lines = []
            line = []
            last_y = 0.0
            for annotation in annotations:
                y = position_y(annotation)
                if abs(last_y - y) < LINE_BREAKING_HEIGHT:
                    line.append(annotation)
                else:
                    if len(line) > 0: lines.append(line)
                    line = [annotation]
                    last_y = y
            if len(line) > 0: lines.append(line)
            return lines
        
        annotations = group_by_line(annotations)
        return annotations

    def get_descriptions(self, annotations):
        def get_description(annotation):
            return annotation['description']
        lines = map(lambda line: list(map(get_description, line)), annotations)
        return lines
        
    def get_menu(self, image_content):
        data = self.detect_text(image_content)
        
        # For development
        # with open('ocr.json') as file:
        #     data = json.load(file)
        
        annotations = data['responses'][0]['textAnnotations']

        # Skip totaled annotation
        annotations = annotations[1:]

        # Noice canceling
        annotations = self.cancel_noise(annotations)
        self.logger.debug('annotations(noise_canceled)={0}'.format(annotations))

        # Group annotations by line
        annotations = self.group_by_line(annotations)
        self.logger.debug('annotations(grouped by line)={0}'.format(annotations))

        # Get descriptions
        lines = self.get_descriptions(annotations)
        
        menus = []
        for line in lines:
            # ['rice', ',', 'Vada', '&', 'Payasam']
            # -> [['rice'], ['Vada', '&', 'Payasam']]
            for ws in split_by(line, ','):
                t = ''.join(ws)
                self.logger.debug('ws={0} jp={1} shop={2}'
                                  .format(ws,
                                          is_japanese_word(t),
                                          is_shop_name(t)))
                if is_shop_name(t): continue
                if is_japanese_word(t): continue
                menus.append(' '.join(ws))

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

    
