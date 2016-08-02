# -*- encoding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import os
import re
import time
import urllib

CHROME_DRIVER_PATH = os.path.join(os.path.dirname('__file__'), 'chromedriver')
TOP_PAGE = 'https://www.facebook.com/NirvanamTokyo/'
SAVE_DIR = 'download'

def list_menu_anchor(anchors):
    lst = []
    for a in anchors:
        href = a.get_attribute('href')
        if href is None: continue
        if href.find('NirvanamTokyo/photos/') <= -1: continue
        imgs = a.find_elements_by_tag_name('img')
        if len(imgs) == 0: continue
        img = imgs[0]
        w = img.get_attribute('width')
        if w is None: continue
        if int(w) < 200: continue
        lst.append(a)
    return lst

def list_src(imgs):
    return list(filter(lambda p: p is not None, map(to_src, imgs)))

def to_src(e):
    return e.get_attribute('src')

def is_jpg(p):
    return p.find('.jpg') > -1 or p.find('.jpeg') > -1

def mkdir_p(d):
    if not os.path.isdir(d):
        os.mkdir(d)
        if not os.path.isdir(d):
            raise Error("failed to make directory")

def click_later(browser):
    time.sleep(2.0)
    later = browser.find_elements_by_link_text('後で')
    if len(later) != 0:
        later[0].click()

def fetch_menu(dir, path):
    print("Opening web browser...")
    browser = webdriver.Chrome(CHROME_DRIVER_PATH)
    browser.get(TOP_PAGE)
    print("Opening web browser...done")
    
    click_later(browser)

    print("Collecting menu anchors...")
    anchors = browser.find_elements_by_tag_name('a')
    anchors = list_menu_anchor(anchors)
    print("Collecting menu anchors...done")

    for anchor in anchors[1:]:
        print("next anchor")
        
        try:
            anchor.click()
            time.sleep(3.0)
        except WebDriverException:
            print('failed to click menu anchor, retry')
            script = 'window.scrollTo({0}, {1})'.format(0, anchor.location['y'])
            browser.execute_script(script)
            click_later(browser)
    
            anchor.click()
            time.sleep(3.0)
    
        spotlight = browser.find_elements_by_class_name('spotlight')
    
        if len(spotlight) >= 0:
            src = spotlight[0].get_attribute('src')
            print("spotlight found, src=" + src)
            
            download_as(src, dir, path)
            browser.find_element_by_tag_name('body').click()
            yield os.path.join(dir, path)
    
    browser.close()

def fetch_menu_image(dir, path):
    for image in fetch_menu(dir, path):
        yield image

def download_to(url, d):
    mkdir_p(d)
    fetch_url(url, d + "/" + os.path.basename(url))

def download_as(url, d, f):
    mkdir_p(d)
    fetch_url(url, d + "/" + f)

def fetch_url(url, dest):
    print("Downloading " + url + "...")
    response = urllib.request.urlopen(url)
    with open(dest, 'wb') as out:
        while True:
            chunk = response.read(16384)
            if not chunk: break
            out.write(chunk)
    print("done")
    
# if __name__ == '__main__':
#     fetch_menu_image(SAVE_DIR, 'menu.jpg')
