from typing import List
import yaml
import time
import pyautogui
import pygetwindow
import json
import numpy as np
import mss

from os import listdir
from cv2 import cv2
from src.logger import logger
from random import random

stream = open('config.yaml', 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
api = c['discord_api']


class Images:
    def __init__(self) -> None:
        pass

    def positions(self, targets_67, threshold=ct['default'], img=None):
        """Calcula a posicao da imagem na tela e retorna uma lista com os numeros da posicao.


        :param targets_67: Imagem a ser procurada na tela.
        :param threshold: (FLOAT) 0 a 1. Tunning para procurar a imagem na tela.
        :param self.img: None
        :return: Lista com a posição da imagem.
        """
        if self.img is None:
            self.img = self.print_screen()
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

    def print_screen(self):
        """Printa a tela"""
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            sct_img = np.array(sct.grab(monitor))
            return sct_img[:, :, :3]

    def click_button(self, img, timeout=3, threshold=ct['default']):
        """Procura a imagem na tela, se encontrar move o mouse ate a imagem e clica.
        :param self.img: Imagem a ser analisada.
        :param timeout: (int) Tempo em segundos que o bot vai continuar procurando ate achar a imagem.
        :param threshold: (float) O quão confiante o bot precisa estar pra clicar na image, valor entre 0 e 1.
        Sendo 1 o mais confiante.
        :return True ou False.
        """
        start = time.time()
        has_timed_out = False
        while not has_timed_out:
            matches = self.positions(img, threshold=threshold)

            if len(matches) == 0:
                has_timed_out = time.time() - start > timeout
                continue

            x, y, w, h = matches[0]
            pos_click_x = x + w / 2
            pos_click_y = y + h / 2
            pyautogui.moveTo(pos_click_x, pos_click_y)
            pyautogui.click()
            return True

        return False

    def check_login(self, img, name=None, timeout=1, threshold=ct['default']):
        """ Analisa se a imagem esta na tela.

        :param self.img: Recebe a imagem a ser procurada.
        :param name: Nome da imagem (opcional).
        :param timeout: Tempo maximo de espera caso a imagem não seja encontrda.
        :param threshold: (float) 0 a 1. Tunning para imagem analisada.
        :return: True ou False
        """
        if not name is None:
            pass
        start = time.time()
        while True:
            matches = self.positions(img, threshold=threshold)
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

    def image_loop(self, img, name, click, timeout=15):
        """ Aguarda a imagem aparecer na tela e mostra  uma menssagem de logger. Caso desejar clica na imagem.

        :param self.img: Recebe o nome da imagem a ser analisada.

        :param name: Nome a ser mostrado na menssagem de logger.

        :param click: True ou False. Clica ou não na imagem selecionada.

        :param timeout: Tempo de espera ate a imagem aparecer na tela.

        :return: True ou False
        """
        found = False

        while not found:
            logger(f'Waiting for {name} image. Timeout {timeout}')
            time.sleep(0.8)
            if self.check_login(self.img):
                if click:
                    Images.click_button(img)
                    found = True
                else:
                    found = True
            if timeout == 0:
                logger(f'{name} Not Found!')
                return False
            timeout -= 1
        return True

    def remove_suffix(self, input_string, suffix):
        """Returns the input_string without the suffix"""

        if suffix and input_string.endswith(suffix):
            return input_string[:-len(suffix)]
        return input_string

    def load_Images(self, dir_path='./targets_67/'):
        """ Scaneia o diretorio inserido e retona um dicionario com o nome de todas as imagens encontradas
        sem o sufixo .png

        Returns:
            dict: Dicionario com o nome das imagens encontradas no diretorio sem o sufixo .png.
        """

        file_names = listdir(dir_path)
        targets_67 = {}
        for file in file_names:
            path = 'targets_67/' + file
            targets_67[self.remove_suffix(file, '.png')] = cv2.imread(path)

        return targets_67


class Heroes:
    """Class para interaçoes com os herois."""

    def __init__(self):
        pass

    def send_work(self, mode):  # Type: List[int]
        """ Envia os herois pra descansar ou trabalhar.

        :param mode: Envia todos os herois para trabalhar caso receba um valor string 'all'.
            Se o valor recebido for 'rest', envia todos os herois para descansar.
        """

        logger('Sending all Heroes to {}.'.format(
            'work' if mode == 'all' else 'resting'))
        self.go_to_Heroes()
        time.sleep(2)
        Images.click_button(self.img[mode])
        time.sleep(1)
        self.go_to_game()
        time.sleep(2)
        if mode == 'all':
            if c['send_screenshot']:
                pass
                # self.sendStashToDiscord()

    def go_to_Heroes(self):
        """Go to Heroes page"""
        self.login_attempts()  # Para tirar os shits do pycharm
        if Images.check_login(self.img['go-back-arrow']):
            Images.click_button(self.img['go-back-arrow'])
            time.sleep(1)
            Images.click_button(self.img['hero-icon'])

        elif Images.click_button(self.img['hero-icon']):
            pass

    def go_to_game(self):
        """Go back to game."""
        self.login_attempts()  # Para tirar os shits do pycharm
        if Images.check_login(self.img['x']):
            Images.click_button(self.img['x'])
            time.sleep(2)
            if Images.check_login(self.img['treasure-hunt-icon']):
                Images.click_button(self.img['treasure-hunt-icon'])

    def refresh_Heroes_positions(self):
        self.login_attempts()  # Para tirar os shits do pycharm
        logger('🔃 Refreshing Heroes Positions')
        if Images.click_button(self.img['go-back-arrow']):
            Images.click_button(self.img['treasure-hunt-icon'])

        elif Images.click_button(self.img['treasure-hunt-icon']):
            pass

        elif Images.click_button(self.img['x']):
            time.sleep(2)
            if Images.click_button(self.img['go-back-arrow']):
                Images.click_button(self.img['treasure-hunt-icon'])
            else:
                Images.click_button(self.img['treasure-hunt-icon'])

    def login_attempts(self):
        pass



class Login:
    def __init__(self):
        self.img = Images.load_Images()
        

    def login_again(self) -> None:
        """Loga no game se estiver deslogado. """

        # Se a wallet estiver lockada.
        if Images.click_button(self.img['meta1']):
            if Images.image_loop(self.img['unlock'], 'Unlock', False, timeout=5):

                # Se o auto_login estiver habilitado na config, o bot irá desbloquear a wallet usado o password que está na config.
                if c['auto_login']:
                    if self.unlock_wallet():
                        if Images.check_login(self.img['select-wallet-2']):
                            Images.click_button(self.img['select-wallet-2'])
                else:

                    # Caso o auto_login esteja desabilitado , irá printar uma menssagem de erro.
                    logger('\033[31mWARNING: Wallet Locked!!\033[0;0m')
                    logger(
                        '\033[31mAuto login not enabled in config.yaml\033[0;0m')

            # Caso não apareça a imagem de unlock wallet. Bot irá aguardar pelo botao de sign-in
            elif Images.image_loop(self.img['select-wallet-2'], 'Sign', True, timeout=5):
                logger('Sign Button Found')

            else:

                # Caso não ache nenhum dos 2 botões irá dar um refresh na pag.
                logger("Can't log-in, resetting browser.")
                pyautogui.hotkey('ctrl', 'f5')
                self.login_again()

        else:

            logger('Metamask is logged.')
            self.unlocked_wallet()

    def unlock_wallet(self) -> bool:
        """Desbloqueia a wallet da metamask caso o usuario queria essa opcão."""
        self.login_attempts()  # Para tirar os shits do pycharm
        logger('Metamask Locked, log in.')
        for n in c['metamask_password']:
            pyautogui.hotkey(n)
        Images.click_button(self.img['unlock'])
        logger('Wallet Unlocked Successfully')
        return True

    def unlocked_wallet(self) -> None:
        """ Caso a wallet não tenha erro de sign ou não logada. """
        if Images.image_loop(self.img['connect-wallet'], 'Connect Wallet Button', True, timeout=10):
            logger('🎉 Connect wallet button detected, logging in!')
            if Images.image_loop(self.img['connect-wallet2'], 'New Connect Wallet', True, timeout=10):
                logger('🎉 New Connect wallet button detected!')
                if Images.image_loop(self.img['select-wallet-2'], 'Sign', True, timeout=10):
                    logger('Sign Button Found.')
                    if Images.image_loop(self.img['treasure-hunt-icon'], 'Treasure Hunt', True):
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

    def is_logged(self, last) -> bool:
        """Checa se todas as janelas estao logadas no game.

        :param last: Recebe um 'ciclo for' de todas as janelas do Google Chrome.

        :return: True ou False.
        """

        logged = False

        while not logged:
            logger('Checking game status')
            if Images.check_login(self.img['error']):
                Images.click_button(self.img['error'])
                pyautogui.hotkey('ctrl', 'f5')

            if Images.check_login(self.img['new-map']):
                dados = Files.resetDb()
                print(f' dados {dados}')
                time.sleep(50)
                logged = True
                break

            if not Images.check_login(self.img['meta1']):
                if not Images.check_login(self.img['network']):
                    logger('No Network error.')
                    if not Images.check_login(self.img['ok']):
                        logger('No Ok button found.')
                        if not Images.check_login(self.img['connect-wallet']):
                            logger('No connect wallet button found')
                            if not Images.check_login(self.img['treasure-hunt-icon']):
                                logger('No Treasure Hunt button found.')
                                if not Images.check_login(self.img['go-back-arrow']):
                                    logger('No Back arrow found.')
                                    if not Images.check_login(self.img['x']):
                                        logger(
                                            'Black Screen Found. Resetting Browser')
                                        last["window"].activate()
                                        pyautogui.hotkey('ctrl', 'f5')
                                        Images.image_loop(
                                            self.img['connect-wallet'], 'Connect wallet', click=False)
                                    else:
                                        Heroes.go_to_game()
                                        logged = True

                                else:
                                    logged = True
                            else:
                                Images.click_button(self.img['treasure-hunt-icon'])
                                logged = True
                        else:
                            self.login_again()
                    else:
                        logger(
                            'Ok button Found, refreshing page and trying to login again.')
                        pyautogui.hotkey('ctrl', 'f5')

                        self.login_again()
                else:
                    logger(
                        'Network error found. Check if metamask is connected to Binance Smart Chain.')
                    self.login_again()
            else:
                self.login_again()
        if logged:
            logger('Game logged successfully')

        return logged

    def select_wallet(self, wallet):

        """Seleiona a wallet para colocar o heroi para trabalhar.


        :param wallet: (STR). nome da account a ser selecionada.
        """
        if Images.image_loop(self.img['meta3'], 'Metamask Icon', click=True):
            if Images.image_loop(self.img['meta'], 'Wallet Change', click=False):

                # Calcular a posicao do botao de mudar a wallet na metamask
                data = Images.positions(self.img['meta'])
                change_wallet_pos = []

                # Loop para saber a posicao atual no data.
                for k, v in enumerate(data[0]):

                    if k == 2:

                        # Adicionar +60 no valor para mover o mouse para o centro da imagem.
                        change_wallet_pos.append(v + 60)
                    else:
                        change_wallet_pos.append(v)

                # Mover o mouse ate o wallet change da metamask
                pyautogui.moveTo(change_wallet_pos)

                # Clicar no botao wallet change da metamask
                pyautogui.click()

                # Aguardar a imagem aparecer na tela  para selecionar a wallet que irá trabalhar.
                if Images.image_loop(self.img[wallet], wallet, click=True):
                    Images.click_button(self.img[wallet], timeout=3, threshold=0.8)
                    time.sleep(3)
                    pyautogui.hotkey('ctrl', 'f5')


class Files:
    def __init__(self):

        pass

    def windows_pyget(self) -> List:
        """Retorna uma lista com todas as janelas do Google Chrome ativas
            com o Jogo Bombcrypto.

        """
        windows = []
        for k, w in enumerate(pygetwindow.getWindowsWithTitle('Bombcrypto - Google Chrome')):
            windows.append(
                {
                    "data": k,
                    "window": w,
                })

        return windows

    def resetDb(self) -> List:
        """ Reseta a Database

        :return List
        """
        with open('db.json', 'r') as reset:
            data = json.load(reset)
        return data

    def write_data(self, data) -> None:
        """Grava os novos dados na database."""
        with open('db.json', 'w') as write:
            json.dump(data, write, indent=4)


class Mouse:

    def __init__(self):
        pass

    def add_randomness(self, n, random_factor_size=None) -> int:
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
        return int(randomized_n)
