# -*- coding: utf-8 -*-
from func.mouse_click import *
from random import randint
from func.mouse_move import *
from func.image_reader import *
import pyautogui
import time

import yaml
import json

# Load config file.
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
ch = c['home']
api = c['discord_api']


def resetDb():
    # Resetar a Database
    with open('db.json', 'r') as reset:
        data = json.load(reset)
    return data


def isWorking(bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True


def descobreRaridade(bar):
    commoms = positions(images['commom-text'], threshold=ct['commom'])
    rares = positions(images['rare-text'], threshold=ct['rare'])
    super_rares = positions(images['super_rare-text'], threshold=ct['super_rare'])
    epics = positions(images['epic-text'], threshold=ct['epic'])
    legend = positions(images['legend-text'], threshold=ct['legend'])

    y = bar[1]

    for (_, button_y, _, button_h) in commoms:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return 'commom'

    for (_, button_y, _, button_h) in rares:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return 'rare'

    for (_, button_y, _, button_h) in super_rares:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return 'super_rare'

    for (_, button_y, _, button_h) in epics:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return 'epic'

    for (_, button_y, _, button_h) in legend:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return 'legend'

    return 'null'


def clickGreenBarButtons(baus):
    # ele clicka nos q tao trabaiano mas axo q n importa
    offset = 140

    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    logger('🟩 %d green bars detected' % len(green_bars))
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger('🆗 %d buttons detected' % len(buttons))

    not_working_green_bars = []
    for bar in green_bars:
        global deveTrabalhar
        global raridade
        raridade = descobreRaridade(bar)
        deveTrabalhar = 1

        if raridade != 'commom' and (baus >= 60 or baus == 0):
            deveTrabalhar = 0

        if (not isWorking(bar, buttons)) and deveTrabalhar == 1:
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('🆗 %d buttons with green bar detected' % len(not_working_green_bars))
        logger('👆 Clicking in %d heroes' % len(not_working_green_bars))

    # se tiver botao com y maior que bar y-10 e menor que y+10
    hero_clicks_cnt = 0
    for (x, y, w, h) in not_working_green_bars:
        # isWorking(y, buttons)
        # moveToWithRandomness(x + offset + (w / 2), y + (h / 2), 1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        hero_clicks_cnt = hero_clicks_cnt + 1
        if hero_clicks_cnt > 20:
            logger('⚠️ Too many hero clicks, try to increase the go_to_work_btn threshold')
            return
        # cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
    return len(not_working_green_bars)


def clickFullBarButtons():
    offset = 100
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('👆 Clicking in %d heroes' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
        # moveToWithRandomness(x + offset + (w / 2), y + (h / 2), 1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1

    return len(not_working_full_bars)


def goToHeroes():
    if clickBtn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0

    time.sleep(1)
    clickBtn(images['hero-icon'])
    time.sleep(randint(1, 3))


def goToGame():
    # in case of server overload popup
    clickBtn(images['x'])
    # time.sleep(3)
    clickBtn(images['x'])

    clickBtn(images['treasure-hunt-icon'])


def refreshHeroesPositions():
    logger('🔃 Refreshing Heroes Positions')
    clickBtn(images['go-back-arrow'])
    clickBtn(images['treasure-hunt-icon'])

    # time.sleep(3)
    clickBtn(images['treasure-hunt-icon'])


def send_work():
    if c['select_heroes_mode'] == 'all':
        logger('⚒️ Sending all heroes to work', 'green')
        goToHeroes()
        time.sleep(2)
        clickBtn(images['all'])
        time.sleep(1)
        goToGame()
    else:
        refreshHeroes()


def refreshHeroes():
    logger('🏢 Search for heroes to work')

    global baus
    #baus = checkBaus()

    goToHeroes()

    if c['select_heroes_mode'] != "full":
        clickFullRest()

    if c['select_heroes_mode'] == "full":
        logger('⚒️ Sending heroes with full stamina bar to work', 'green')
    elif c['select_heroes_mode'] == "green":
        logger('⚒️ Sending heroes with green stamina bar to work', 'green')
    else:
        logger('⚒️ Sending all heroes to work', 'green')

    buttonsClicked = 1
    empty_scrolls_attempts = c['scroll_attemps']

    while empty_scrolls_attempts > 0:
        if c['select_heroes_mode'] == 'full':
            buttonsClicked = clickFullBarButtons()
        elif c['select_heroes_mode'] == 'green':
            buttonsClicked = clickGreenBarButtons(baus)
        else:
            buttonsClicked = clickButtons()

        if buttonsClicked == 0:
            empty_scrolls_attempts = empty_scrolls_attempts - 1
        scroll()
        time.sleep(2)
    logger('💪 {} heroes sent to work'.format(hero_clicks))
    goToGame()


def send_to_work(mode):
    """:db
    database recebe o data_list

    :cvar
    """
    # Dados Default Colocar pra trabalhar para iniciar o loop
    goToHeroes()
    time.sleep(2)
    clickBtn(images[mode])
    time.sleep(1)
    goToGame()
    time.sleep(2)
    if c['send_screenshot']:
        if mode == 'all':
            sendStashToDiscord()


def sendStashToDiscord():
    import discord
    import pyautogui
    import os
    import datetime
    if clickBtn(images['stash']):
        time.sleep(2)

        q = datetime.datetime.now()
        d = q.strftime("%d%m%Y%H%M")
        image_file = os.path.join('screenshots', d + '.png')
        pic = pyautogui.screenshot(image_file)

        time.sleep(1)
        webhook = discord.Webhook.from_url(api, adapter=discord.RequestsWebhookAdapter())
        webhook.send(file=discord.File(image_file))
        clickBtn(images['x'])

