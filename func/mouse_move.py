from random import random
from func.image_reader import positions, load_images


import pyautogui
import yaml

images = load_images()
# Load config file.
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']


def addRandomness(n, random_factor_size=None):
    """Returns n with randomness
    Parameters:
        n (int): A decimal integer
        random_factor_size (int): The maximum value+- of randomness that will be
            added to n

    Returns:
        int: n with randomness
    """

    if random_factor_size is None:
        randomness_percentage = 0.1
        random_factor_size = randomness_percentage * n

    random_factor = 2 * random() * random_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - random_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)


def moveToWithRandomness(x, y, t):
    pyautogui.moveTo(addRandomness(x, 10), addRandomness(y, 10), t + random() / 2)


def scroll():
    com = positions(images['commom-text'], threshold=ct['commom'])
    if len(com) == 0:
        com = positions(images['rare-text'], threshold=ct['rare'])
        if len(com) == 0:
            com = positions(images['super_rare-text'], threshold=ct['super_rare'])
            if len(com) == 0:
                com = positions(images['epic-text'], threshold=ct['epic'])
                if len(com) == 0:
                    return

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0, -c['click_and_drag_amount'], duration=1, button='left')
