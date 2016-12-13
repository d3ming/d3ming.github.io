#!/usr/bin/env python
from splinter import Browser
import time
import os
from selenium import webdriver
import glob
from PIL import Image


SAUCE_URL = "http://paperg:e8400cfa-5dea-401d-95a8-bad6799cca8b@ondemand.saucelabs.com:80/wd/hub"
TEST_SERVER_URL = "http://d3ming.github.io/fontcheck/"

BROWSER_CONFIGS = {
    "IE11": {
        "platform": "Windows 8.1",
        "browserName": "internet explorer",
        "version": "11.0"
    },
    "IE9": {
        "platform": "Windows 7",
        "browserName": "internet explorer",
        "version": "9.0"
    },
    "Safari": {
        "platform": "OS X 10.11",
        "browserName": "safari",
        "version": "10.0"
    }
}


def get_build():
    return "font-checker-{}".format(time.strftime("%Y%m%d-%H%M%S"))


def make_build_dirs(build_id):
    output_path = 'output'
    build_path = os.path.join(output_path, build_id)
    os.makedirs(build_path)
    return build_path


def screenshot_element(driver, element, output_path):
    """Take a screenshot of a specific webelement
    """
    size = element.size
    location = element.location

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    cropbox = (left, top, right, bottom)

    f = _screenshot(driver, output_path)
    img = crop(f, cropbox)
    return img

def crop(img_file, cropbox, backup=False):
    img = Image.open(img_file)

    if cropbox:
        img = img.crop(cropbox)

    if backup:
        # backup file before saving back
        shutil.copyfile(img_file, img_file + ".bak")
    img.save(open(img_file, 'wb'))
    return img


def _screenshot(driver, output_path):
    if not output_path.endswith('.png'):
        output_path += ".png"
    driver.get_screenshot_as_file(output_path)
    return output_path


def main():
    print("Starting font-checker...")
    build_id = get_build()
    build_path = make_build_dirs(build_id=build_id)
    font_names = glob.glob("fonts/*")

    for font_path in font_names:
        font_name = str(font_path).replace('fonts/', '')
        test_url = TEST_SERVER_URL + font_path
        print("{}".format(test_url))
        for config_name in BROWSER_CONFIGS:
            config = BROWSER_CONFIGS[config_name]
            with Browser(driver_name="remote",
                        url=SAUCE_URL,
                        browser=config['browserName'],
                        platform=config['platform'],
                        version=config['version'],
                        build=build_id,
                        name="font-checker: {}".format(config_name)) as browser:
                print("{}: https://saucelabs.com/jobs/{}".format(
                    config_name, browser.driver.session_id))
                browser.visit(test_url)

                # take screenshot!
                screenie_path = os.path.join(build_path, font_name + '_' + config_name + '.png')
                screenie_element = browser.driver.find_element_by_id("capture")
                screenshot_element(driver=browser.driver, element=screenie_element, output_path=screenie_path)

main()
