import yaml
import time
import pyautogui
import json

from src.logger import logger
from func.mouse_click import clickBtn
from func.image_reader import load_images, check_login, image_loop

stream = open('config.yaml', 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
api = c['discord_api']

images = load_images()


class Heroes:
    '''Class para interaçoes com os herois.'''
    def __init__(self):
        pass

    def send_work(self, mode):
        ''' Envia os herois pra descansar ou trabalhar.
        all: Envia todos os herois para trabalhar.
        rest: Envia todos os herois para descansar.

        '''        
        self.mode = mode
        logger('Sending all heroes to {}.'.format('work' if self.mode == 'all' else 'resting'))
        self.go_to_heroes()
        time.sleep(2)
        clickBtn(images[self.mode])
        time.sleep(1)
        self.go_to_game()
        time.sleep(2)        
        if self.mode == 'all':
            if c['send_screenshot']:
                self.sendStashToDiscord()        

    def go_to_heroes(self):
        """Go to Heroes page"""

        if check_login(images['go-back-arrow']):
            clickBtn(images['go-back-arrow'])
            time.sleep(1)
            clickBtn(images['hero-icon'])

        elif clickBtn(images['hero-icon']):
            pass
            
    def go_to_game(self):
        """Go back to game."""
        if check_login(images['x']):
            clickBtn(images['x'])
            time.sleep(2)
            if check_login(images['treasure-hunt-icon']):
                clickBtn(images['treasure-hunt-icon'])        
    
    def refresh_heroes_positions(self):
        logger('🔃 Refreshing Heroes Positions')
        if clickBtn(images['go-back-arrow']):
            clickBtn(images['treasure-hunt-icon'])

        elif clickBtn(images['treasure-hunt-icon']):
            pass

        elif clickBtn(images['x']):
            time.sleep(2)
            if clickBtn(images['go-back-arrow']):
                clickBtn(images['treasure-hunt-icon'])
            else:
                clickBtn(images['treasure-hunt-icon'])

class Login():
    def __init__(self):
        pass

    def login_again(self):
        """Loga no game se estiver deslogado."""
        if clickBtn(images['meta1']):
            if image_loop(images['unlock'], 'Unlock', False, timeout=5):           
            
                if c['auto_login']:
                    if self.unlock_wallet():
                        if check_login(images['select-wallet-2']):
                            clickBtn(images['select-wallet-2'])
                else:
                    logger('\033[31mWARNING: Wallet Locked!!\033[0;0m')
                    logger('\033[31mAuto login not enabled in config.yaml\033[0;0m')                   
            
            elif image_loop(images['select-wallet-2'], 'Sign', True, timeout=5):
                logger('Sign Button Found')
                #clickBtn(images['meta3'])
            
            else:
                logger("Can't log-in, reseting browser.")
                pyautogui.hotkey('ctrl', 'f5')
                self.login_again()

            
        else:
            logger('Metamask is logged.')
            self.unlocked_wallet()               

    def unlock_wallet(self):
        """Desbloqueia a wallet da metamask caso o usuario queria essa opcão."""
        
        logger('Metamask Locked, log in.')
        for n in c['metamask_password']:
                pyautogui.hotkey(n)
        clickBtn(images['unlock'])            
        logger('Wallet Unlocked Successfully')
        return True
    
    def unlocked_wallet(self):
        """ Caso a wallet não tenha erro de sign ou não logada. """                    
        if image_loop(images['connect-wallet'], 'Connect Wallet Button', True, timeout=10):    
            logger('🎉 Connect wallet button detected, logging in!')
            if image_loop(images['connect-wallet2'], 'New Connect Wallet', True, timeout=10):
                logger('🎉 New Connect wallet button detected!')
                if image_loop(images['select-wallet-2'], 'Sign', True, timeout=10):
                    logger('Sign Button Found.')
                    if image_loop(images['treasure-hunt-icon'], 'Treasure Hunt', True):
                        logger('Game Logged.')
                    else:
                        pyautogui.hotkey('ctrl', 'f5')
                        self.login_again()
                else:
                    pyautogui.hotkey('ctrl', 'f5')
                    self.login_again()
            else:
                pyautogui.hotkey('ctrl', 'f5')
                self.login_again()
        
        else:
            pyautogui.hotkey('ctrl', 'f5')
            self.login_again()

    def loggin_attempts():
        pass

    def is_logged(self,last):

        logged = False

        while not logged:
            logger('Checking game status')
            if check_login(images['new-map']):
                logged = True
                break
            if not check_login(images['meta1']):
                if not check_login(images['network']):
                    logger('No Network error.')
                    if not check_login(images['ok']):
                        logger('No Ok buttoun found.')
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
                                        Heroes.go_to_game()
                                        logged = True

                                else:
                                    logged = True
                            else:
                                clickBtn(images['treasure-hunt-icon'])
                                logged = True
                        else:
                            self.login_again()
                    else:
                        logger('Ok button Found, refreshing page and trying to login again.')
                        pyautogui.hotkey('ctrl', 'f5')
                        self.login_again()
                else:
                    logger('Network error found. Check if metamask is connected to Binance Smart Chain.')
                    self.login_again()
            else:
                self.login_again()
        if logged:
            logger('Game logged sucessfully')

