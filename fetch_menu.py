# -*- encoding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import urllib
import os
import re
import time

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

def download_to(url, d):
    mkdir_p(d)
    to = d + "/" + os.path.basename(url)
    print("Downloading " + url + "...")
    urllib.request.urlretrieve(url, to)

def download_as(url, d, f):
    mkdir_p(d)
    to = d + "/" + f
    print("Downloading " + url + "...")
    urllib.request.urlretrieve(url, to)

def click_later(browser):
    time.sleep(2.0)
    later = browser.find_elements_by_link_text('後で')
    if len(later) != 0:
        later[0].click()

def fetch_menu(dir, path):
    browser = webdriver.Chrome(CHROME_DRIVER_PATH)
    browser.get(TOP_PAGE)
    
    click_later(browser)
    
    try:
        anchors = browser.find_elements_by_tag_name('a')
        anchors = list_menu_anchor(anchors)
        anchor = anchors[1]
        anchor.click()
    except WebDriverException:
        print('failed to click anchor')
    
    time.sleep(3.0)
    spotlight = browser.find_elements_by_class_name('spotlight')
    
    if len(spotlight) == 0:
        script = 'window.scrollTo({0}, {1})'.format(0, anchor.location['y'])
        browser.execute_script(script)
        click_later(browser)
    
        anchor.click()
        time.sleep(3.0)
    
        spotlight = browser.find_elements_by_class_name('spotlight')
    
    src = spotlight[0].get_attribute('src')
    download_as(src, dir, path)
    
    browser.close()

def fetch_menu_image(dir, path):
    fetch_menu(dir, path)

if __name__ == '__main__':
    fetch_menu_image(SAVE_DIR, 'menu.jpg')
