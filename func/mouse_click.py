# -*- coding: utf-8 -*-
from func.image_reader import *
from func.mouse_move import moveToWithRandomness
from src.logger import logger
import pyautogui
import time
import yaml

# Load config file.
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']

images = load_images()


def clickButtons():
    global hero_clicks
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    # print('buttons: {}'.format(len(buttons)))
    for (x, y, w, h) in buttons:
        moveToWithRandomness(x + (w / 2), y + (h / 2), 1)
        pyautogui.click()
        hero_clicks += 1
        # cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if hero_clicks > 20:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            return
    return len(buttons)


def clickBtn(img, timeout=3, threshold=ct['default']):
    """Search for img in the scree, if found moves the cursor over it and clicks.
    Parameters:
        img: The image that will be used as an template to find where to click.
        timeout (int): Time in seconds that it will keep looking for the img before returning with fail
        threshold(float): How confident the bot needs to be to click the buttons (values from 0 to 1)
    """

    # logger(None, progress_indicator=True)
    start = time.time()
    has_timed_out = False
    while not has_timed_out:
        matches = positions(img, threshold=threshold)

        if len(matches) == 0:
            has_timed_out = time.time() - start > timeout
            continue

        x, y, w, h = matches[0]
        pos_click_x = x + w / 2
        pos_click_y = y + h / 2
        # moveToWithRandomness(pos_click_x, pos_click_y, 1)
        pyautogui.moveTo(pos_click_x, pos_click_y)
        pyautogui.click()
        return True

    return False


def clickFullRest():
    while True:
        buttons = positions(images['rest'], threshold=ct['rest'])
        if len(buttons) > 0:
            clickBtn(images['rest'])
        else:
            return
