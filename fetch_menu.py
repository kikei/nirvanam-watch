# -*- encoding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import os
import re
import time
import urllib

CHROME_DRIVER_PATH = os.path.join(os.path.dirname('__file__'), 'chromedriver')
TOP_PAGE = 'https://www.facebook.com/NirvanamTokyo/'
CHROME_EXTENSION_FILENAME = 'proxy.zip'

def try_to_get(browser, getter, retry=3, sleep=1.0):
    for i in range(0, retry):
        try:
            x = getter(browser)
        except Exception as e:
            print('Error in try_to_get: ' + str(e))
        if x is not None:
            return x
        time.sleep(sleep)
    return None

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

def menu_anchors(browser):
    for a in browser.find_elements_by_tag_name('a'):
        href = a.get_attribute('href')
        if href is None: continue
        if href.find('NirvanamTokyo/photos/') <= -1: continue
        imgs = a.find_elements_by_tag_name('img')
        if len(imgs) == 0: continue
        img = imgs[0]
        w = img.get_attribute('width')
        if w is None: continue
        if int(w) < 200: continue
        yield a

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

def scroll_to(browser, element):
    script = 'window.scrollTo({0}, {1})'.format(0, element.location['y'])
    browser.execute_script(script)

def fetch_menu(dir, path, options=None):
    print("Opening web browser...")
    browser = webdriver.Chrome(CHROME_DRIVER_PATH, chrome_options=options)
    browser.get(TOP_PAGE)
    print("Opening web browser...done")
    
    click_later(browser)

    print("Searching menu anchors...")
    for anchor in menu_anchors(browser):
        print("next anchor")
        
        try:
            anchor.click()
            time.sleep(3.0)
        except WebDriverException:
            print('failed to click menu anchor, retry')
            scroll_to(browser, anchor)
            click_later(browser)
    
            anchor.click()
            time.sleep(3.0)

        def get_spotlight(browser):
            spotlights = browser.find_elements_by_class_name('spotlight')
            if len(spotlights) == 0:
                return None
            return spotlights[0]
        
        spotlight = try_to_get(browser, get_spotlight)

        if spotlight is not None:
            src = spotlight.get_attribute('src')
            print("spotlight found, src=" + src)
            
            download_as(src, dir, path)
            browser.find_element_by_tag_name('body').click()
            yield os.path.join(dir, path)
    
    browser.close()

from selenium.webdriver.chrome.options import Options

def fetch_menu_image(dir, path, proxy=None):
    options = None
    if proxy is not None:
        extpath = os.path.join(dir, CHROME_EXTENSION_FILENAME)
        proxy.generate_extension(extpath)
        options = Options()
        options.add_extension(extpath)
    for image in fetch_menu(dir, path, options):
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
