import pyautogui
import yaml
import time

from func.mouse_click import clickBtn
from src.logger import logger
from func.mouse_click import *

stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
login_attempts = 0

images = load_images()

#def unlock_wallet():



def login():
    global login_attempts

    logger('😿 Game disconnected , logging again')

    if login_attempts > 3:
        logger('🔃 Too many login attempts, refreshing')
        login_attempts = 0
        pyautogui.hotkey('ctrl', 'f5')
        return

    if check_login(images['meta1']):
        logger('Metamask Locked, log in.')
        clickBtn(images['meta1'])
        if image_loop(images['unlock'], 'Unlock', False, timeout=5):
            for n in c['metamask_password']:
                pyautogui.hotkey(n)
            clickBtn(images['unlock'])
            logger('Wallet Unlocked, restarting login process')
            login()
        elif image_loop(images['select-wallet-2'], 'Sign', True, timeout=5):
            logger('Sign Found, restarting login process')
            pyautogui.hotkey('ctrl', 'f5')
            login()
    else:
        logger('Metamask is logged.')
        if check_login(images['connect-wallet']):
            image_loop(images['connect-wallet'], 'Connect Wallet Button', True, timeout=5)
            logger('🎉 Connect wallet button detected, logging in!')

            logger('Waiting for New Connect Wallet')
            image_loop(images['connect-wallet2'], 'New Connect Wallet', True, timeout=5)
            image_loop(images['select-wallet-2'], 'Sign', True, timeout=5)
            image_loop(images['treasure-hunt-icon'], 'Treasure Hunt', True)
            login_attempts += 0


def check_login(img, name=None, timeout=0, threshold=ct['default']):
    if not name is None:
        pass
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


def islogged(last):
    import json

    logged = False

    while not logged:
        time.sleep(5)
        logger('Checking game status.')
        logger(f'Loggin Attempts: {login_attempts}')
        if check_login(images['new-map']):
            logger('New Map Found!')
            with open('db.json', 'r') as read:
                data = json.load(read)

            for n in data:
                print(n)
                # Se a janela do Chrome for igual a database.
                if n[0]['window'] == last['data']:

                    logger('Window Found. Window = Data')
                    # Varrer a lista data
                    for account in n[0]['data']:

                        # Varrer a lista account com as wallets.
                        for data in account:
                            if data['rest'] == 'False':
                                new_map = data['new_map']

                                with open('db.json', 'w') as data_dump:
                                    new_map += 1
                                    data['new_map'] = new_map
                                    json.dump(data, data_dump)
                                    read.close()
            logged = True
            break
        else:
            logger('No New Map found')
        # check for Blackscreen in login screen when we don't have any button.
        if not check_login(images['meta1']):
            if not check_login(images['network']):
                logger('No Network error.')
                if not check_login(images['ok']):
                    logger('No Ok buttoun found.', 'green')
                    if not check_login(images['connect-wallet']):
                        logger('No connect wallet buttoun found')
                        if not check_login(images['treasure-hunt-icon']):
                            logger('No Treasure Hunt buttoun found.')
                            if not check_login(images['go-back-arrow']):
                                logger('No Back arrow found.')
                                if not check_login(images['x']):
                                    logger('Black Screen Found. Reseting Browser')
                                    last["window"].activate()
                                    pyautogui.hotkey('ctrl', 'f5')
                                    image_loop(images['connect-wallet'], 'Conect wallet', click=False)
                                else:
                                    clickBtn(images['x'])
                                    if check_login(images['treasure-hunt-icon']):
                                        clickBtn(images['treasure-hunt-icon'])
                                        clickBtn(images['treasure-hunt-icon'])
                                    logged = True

                            else:

                                logged = True
                        else:
                            clickBtn(images['treasure-hunt-icon'])
                            logged = True
                    else:
                        login()
                else:
                    logger('Ok button Found, refreshing page and trying to login again.')
                    pyautogui.hotkey('ctrl', 'f5')
                    image_loop(images['connect-wallet'], 'Conect wallet', click=False)
            else:
                logger('Network error found. Check if metamask is connected to Binance Smart Chain.')
                if c['auto_login']:
                    logger('Auto-Login Enabled. Loggin.')
                    clickBtn(images['meta3'])
                    image_loop(images['unlock'], 'Unlock', False)
                    for n in c['metamask_password']:
                        pyautogui.hotkey(n)
                    clickBtn(images['unlock'])
                    login()
                else:
                    logger('Auto-Login is not enable.')
                    clickBtn(images['ok'])
                    pyautogui.hotkey('ctrl', 'f5')
                    image_loop(images['connect-wallet'], 'Conect wallet', click=False)
        else:
            login()
    if logged:
        logger('Game logged sucessfully')
