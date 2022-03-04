import yaml
import time
import pyautogui

from src.logger import logger
from func.mouse_click import clickBtn
from func.image_reader import load_images, check_login, image_loop

stream = open('config.yaml', 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
api = c['discord_api']

images = load_images()


class Heroes:
    """Class para interaçoes com os herois."""

    def __init__(self):
        pass

    def send_work(self, mode):
        """ Envia os herois pra descansar ou trabalhar.

        :param mode: Envia todos os herois para trabalhar caso receba um valor string 'all'.
            Se o valor recebido for 'rest', envia todos os herois para descansar.


        """

        logger('Sending all heroes to {}.'.format('work' if mode == 'all' else 'resting'))
        self.go_to_heroes()
        time.sleep(2)
        clickBtn(images[mode])
        time.sleep(1)
        self.go_to_game()
        time.sleep(2)
        if mode == 'all':
            if c['send_screenshot']:
                pass
                # self.sendStashToDiscord()

    def go_to_heroes(self):
        """Go to Heroes page"""
        self.login_attempts()  # Para tirar os shits do pycharm
        if check_login(images['go-back-arrow']):
            clickBtn(images['go-back-arrow'])
            time.sleep(1)
            clickBtn(images['hero-icon'])

        elif clickBtn(images['hero-icon']):
            pass

    def go_to_game(self):
        """Go back to game."""
        self.login_attempts()  # Para tirar os shits do pycharm
        if check_login(images['x']):
            clickBtn(images['x'])
            time.sleep(2)
            if check_login(images['treasure-hunt-icon']):
                clickBtn(images['treasure-hunt-icon'])

    def refresh_heroes_positions(self):
        self.login_attempts()  # Para tirar os shits do pycharm
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

    def login_attempts(self):
        pass


heroes = Heroes()


class Login:
    def __init__(self):
        pass

    def login_again(self):
        """Loga no game se estiver deslogado. """

        # Se a wallet estiver lockada.
        if clickBtn(images['meta1']):
            if image_loop(images['unlock'], 'Unlock', False, timeout=5):

                # Se o auto_login estiver habilitado na config, o bot irá desbloquear a wallet usado o password que está na config.
                if c['auto_login']:
                    if self.unlock_wallet():
                        if check_login(images['select-wallet-2']):
                            clickBtn(images['select-wallet-2'])
                else:

                    # Caso o auto_login esteja desabilitado , irá printar uma menssagem de erro.
                    logger('\033[31mWARNING: Wallet Locked!!\033[0;0m')
                    logger('\033[31mAuto login not enabled in config.yaml\033[0;0m')

            # Caso não apareça a imagem de unlock wallet. Bot irá aguardar pelo botao de sign-in
            elif image_loop(images['select-wallet-2'], 'Sign', True, timeout=5):
                logger('Sign Button Found')

            else:

                # Caso não ache nenhum dos 2 botões irá dar um refresh na pag.
                logger("Can't log-in, resetting browser.")
                pyautogui.hotkey('ctrl', 'f5')
                self.login_again()

        else:

            logger('Metamask is logged.')
            self.unlocked_wallet()

    def unlock_wallet(self):
        """Desbloqueia a wallet da metamask caso o usuario queria essa opcão."""
        self.login_attempts()  # Para tirar os shits do pycharm
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

    def login_attempts(self):
        pass

    def is_logged(self, last):
        """Checa se todas as janelas estao logadas no game.

        :param last: Recebe um 'for' de todas as janelas do Google Chrome.

        :return: True ou False.
        """

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
                        logger('No Ok button found.')
                        if not check_login(images['connect-wallet']):
                            logger('No connect wallet button found')
                            if not check_login(images['treasure-hunt-icon']):
                                logger('No Treasure Hunt button found.')
                                if not check_login(images['go-back-arrow']):
                                    logger('No Back arrow found.')
                                    if not check_login(images['x']):
                                        logger('Black Screen Found. Resetting Browser')
                                        last["window"].activate()
                                        pyautogui.hotkey('ctrl', 'f5')
                                        image_loop(images['connect-wallet'], 'Connect wallet', click=False)
                                    else:
                                        heroes.go_to_game()
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
            logger('Game logged successfully')
