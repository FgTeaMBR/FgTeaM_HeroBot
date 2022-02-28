# -*- coding: utf-8 -*-
from cv2 import cv2
from os import listdir
from src.logger import logger
from func.login_func import *
import time
import numpy as np
import mss
import yaml

# Load config file.
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
login_attempts = 0


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



def check_login(img, name=None, timeout=1, threshold=ct['default']):
    if not name is None:
        pass
        # print('waiting for "{}" button, timeout of {}s'.format(name, timeout))
    start = time.time()
    while True:
        matches = positions(img, threshold=threshold)
        if len(matches) == 0:
            hast_timed_out = time.time() - start > timeout
            if hast_timed_out:
                if not name is None:
                    pass
                return False
            continue

        x, y, w, h = matches[0]
        pos_click_x = x + w / 2
        pos_click_y = y + h / 2
        return True


def image_loop(img, name, click, timeout=15):
    global login_attempts
    found = False

    while not found:
        logger(f'Waiting for {name} image. Timeout {timeout}')
        time.sleep(0.8)
        if check_login(img):
            if click:
                clickBtn(img)
                found = True
                logger(f'{name} found! Processing..')
            else:
                found = True
        if timeout == 0:
            login_attempts += 1
            logger(f'{name} not found!')
            break
        timeout -= 1
    return found


def printScreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        return sct_img[:, :, :3]


def remove_suffix(input_string, suffix):
    """Returns the input_string without the suffix"""

    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def load_images(dir_path='./targets_67/'):
    """ Programmatically loads all images of dir_path as a key:value where the
        key is the file name without the .png suffix

    Returns:
        dict: dictionary containing the loaded images as key:value pairs.
    """

    file_names = listdir(dir_path)
    targets_67 = {}
    for file in file_names:
        path = 'targets_67/' + file
        targets_67[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets_67


def show(rectangles, img=None):
    """ Show an popup with rectangles showing the rectangles[(x, y, w, h),...]
        over img or a printScreen if no img provided. Useful for debugging"""

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255, 255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)


def positions(targets_67, threshold=ct['default'], img=None):
    if img is None:
        img = printScreen()
    result = cv2.matchTemplate(img, targets_67, cv2.TM_CCOEFF_NORMED)
    w = targets_67.shape[1]
    h = targets_67.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

    return rectangles


def checkArrows():
    list_arrow = []
    count = 0
    images = load_images()
    while True:
        # logger('Search for arrows in the screen')

        arrow = positions(images['back_mini'], threshold=ct['default'])
        if arrow not in list_arrow:
            list_arrow.append({count: arrow})
        else:
            break
        clickBtn(images['back_mini'])
        print(arrow)
