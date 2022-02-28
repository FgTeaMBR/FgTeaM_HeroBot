# -*- coding: utf-8 -*-
import pygetwindow
from datetime import datetime
from src.logger import logger
from func.login_func import *
from func.image_reader import *
from func.heroes_func import *

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
t = c['time_intervals']
pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause

login_attempts = 0
db = []
windows = []

if not c['save_log_to_file']:
    logger('Warning, logs files are disable.')

images = load_images()


def select_wallet(wallet):
    """
    -> Seleiona a wallet para colocar o heroi para trabalhar.
    :wallet: STR. nome da account a ser selecionada.

    :return:
    """
    if image_loop(images['meta3'], 'Metamask Icon', click=False):
        clickBtn(images['meta3'], timeout=3, threshold=0.8)
        if image_loop(images['meta'], 'Wallet Change', click=False):

            # Calcular a posicao do botao de mudar a wallet na metamask
            data = positions(images['meta'])
            x = []
            count = 0

            # Loop para saber a posicao atual no data.
            for n in data[0]:

                if count == 2:

                    # Adicionar +60 no valor para mover o mouse para o centro da imagem.
                    x.append(n + 60)
                else:
                    x.append(n)
                count += 1

            # Mover o mouse ate o wallet change da metamask
            pyautogui.moveTo(x)

            # Clicar no botao wallet change da metamask
            pyautogui.click()

            # Aguardar a imagem aparecer na tela  para selecionar a wallet que irá trabalhar.
            if image_loop(images[wallet], wallet, click=False):
                clickBtn(images[wallet], timeout=3, threshold=0.8)

            time.sleep(50)


def test(wallet):
    with open('db.json', 'r') as read:
        data = json.load(read)

    # n para saber qual janela do chrome deve ativar.
    for n in data:

        # Se a janela for igual a database.
        if n['window'] == 0:

            # Varrer a lista data.
            for account in n['data']:

                # Varrer a lista account com as wallets
                for data in account:

                    # Se a wallet  for igual a wallet inserida.
                    if data['wallet'] == wallet:

                        # Checar o status atual , se esta trabalhando ou não.

                        if data['rest'] == 'True':


                            # Wallet atual esta trabalhando ou esgotou o tempo de trabalhar
                            # Deve ir descansar.
                            # TODO Se estiver trabalhando colocar para descansar e mudar para a outra account
                            # TODO #Gravar os dados na database e depois de colocar para descansar
                            if wallet == 'account_1':

                                # Mudar da wallet 1 para wallet 2
                                select_wallet('account_2')
                                logger('Sending current wallet to idle and rest.')
                            else:

                                # Mudar da wallet 2 para wallet 1
                                select_wallet('account_1')


                """# Saber se a account é igual a selecionada
                if account[0]['wallet'] == wallet:
                    print(account[0]['wallet'])
                    print(account[0]['rest'])"""




def main():
    global clickBtn, db
    #

    count = 0
    for w in pygetwindow.getWindowsWithTitle('Bombcrypto - Google Chrome'):
        windows.append(
            {
                "data": count,
                "window": w,
            })
        count += 1

    # Open as read db.json.
    resetDb(db)
    count = len(db)

    while len(windows) > count:
        db.append(
            [{"window": 0, "data": [
                [{"wallet": "account_1", "rest": "True", "heroes_work": 0, "heroes_rest": 0, "refresh_heroes": 0, "new_map":0}],
                [{"wallet": "account_2", "rest": "False", "heroes_work": 0, "heroes_rest": 0, "refresh_heroes": 0, "new_map": 0}]

            ]}]
        )
        count += 1

        with open('db.json', 'w') as data:
            json.dump(db, data)

    while True:

        # Reset Database
        resetDb(db)

        count = total = 0
        for last in windows:
            last["window"].activate()
            for n in enumerate(windows):
                total += 1
            print()
            logger(f'Activating Bot Window {count + 1}')
            if count > total:
                count = 0
            count += 1
            islogged(last)
            # Mostrar o status atual do game, se esta trabalhando ou descansado.
            for n in db:
                if last["window"] == db[n][0]['data']:
                    logger('Current Status: {}'.format('Working.' if db[n][0]["rest"] == 'False' else 'Resting.'))

            # Checar se todas as janelas estao logadas na tela do jogo.
            islogged(last)

        for n in range(0, len(db)):
            now = time.time()

            # Se estiver descansando
            if db[n][0]['rest'] == 'True':

                # Resetar a database
                resetDb(db)

                # Se for o primeiro loop com o hero work 0, colocar para trabalhar.
                if db[n][0]["heroes_work"] == 0:

                    # Send Heroes to work
                    send_to_work(db, n, windows, 'all')

                else:
                    # Reset Database
                    resetDb(db)

                    # Se for o primeiro rest loop.
                    if db[n][0]["heroes_rest"] == 0:

                        logger('💪 Sending heroes to rest, first loop')

                        # Send heroes to rest.
                        send_to_work(db, n, windows, 'rest')

                        # Se estiver no range do rest

                    # Se nao for o primeiro loop.
                    else:
                        resetDb(db)
                        # Se estiver descansando e tiver no range, printar os status do proximo reset. .
                        if now - db[n][0]["heroes_rest"] < addRandomness(t['send_heroes_to_rest'] * 60):
                            print()

                            logger(f'Current status of Window {db[n][0]["data"] + 1}')
                            logger(f'Current Rest: {db[n][0]["rest"]}')
                            logger('Range Resting')

                            next_reboot = db[n][0]["heroes_rest"] + (t["send_heroes_to_rest"] * 60)
                            next_refresh = db[n][0]["refresh_heroes"] + (t["refresh_heroes_positions"] * 60)
                            logger(
                                f'Time for next hero Work: {datetime.fromtimestamp(next_reboot).strftime("%H:%M:%S")}. Current Set: {t["send_heroes_to_rest"]} minutes.')
                            logger(
                                f'Time for next hero REFRESH: {datetime.fromtimestamp(next_refresh).strftime("%H:%M:%S")}. Current Set: {t["refresh_heroes_positions"]} minutes.')
                        else:
                            # Se estiver descansando e o timer for maior que o send_heroes_to_rest. Colocar para trabalhar.
                            if now - db[n][0]["heroes_rest"] > addRandomness(t['send_heroes_to_rest'] * 60):
                                logger('Sending heroes to work after rest.')

                                # Send heroes to rest
                                send_to_work(db, n, windows, 'rest')

            # Se estiver Trabalhando
            else:
                resetDb(db)

                # Se estiver no range e estiver trabalhando
                if db[n][0]["heroes_work"] != 0:
                    if now - db[n][0]["heroes_work"] < addRandomness(
                            t['send_heroes_to_work'] * 60):
                        print()
                        logger(f'Current status of Window {db[n][0]["data"] + 1}')
                        logger(f'Current Rest: {db[n][0]["rest"]}')
                        logger('Range Trabalhando')
                        next_reboot = db[n][0]["heroes_work"] + (t["send_heroes_to_work"] * 60)
                        next_refresh = db[n][0]["refresh_heroes"] + (t["refresh_heroes_positions"] * 60)
                        logger(
                            f'Time for next hero REST: {datetime.fromtimestamp(next_reboot).strftime("%H:%M:%S")}. Current Set: {t["send_heroes_to_work"]} minutes.')
                        logger(
                            f'Time for next hero REFRESH: {datetime.fromtimestamp(next_refresh).strftime("%H:%M:%S")}. Current Set: {t["refresh_heroes_positions"]} minutes.')

                    else:
                        # Ja que nao é igual a 0 e nem menor que o timer, colocar para descansar.
                        if now - db[n][0]["heroes_work"] > addRandomness(
                                t['send_heroes_to_work'] * 60):
                            logger('💪 Sending heroes to rest (01)')
                            logger(f'Current status of Window {db[n][0]["data"] + 1}')
                            logger(f'Current Rest: {db[n][0]["rest"]}')

                            # Sending heroes to rest
                            send_to_work(db, n, windows, 'rest')

            # Refresh Heroes loop
            if now - db[n][0]["refresh_heroes"] > addRandomness(t['refresh_heroes_positions'] * 60):
                for k in windows:
                    if db[n][0]['data'] == k['data']:
                        k["window"].activate()
                with open('db.json', 'r') as read:
                    dados = json.load(read)
                    with open('db.json', 'w') as data:
                        dados[n][0]['refresh_heroes'] = now
                        json.dump(dados, data)
                        read.close()
                resetDb(db)
                refreshHeroesPositions()

        # sys.stdout.flush()


if __name__ == '__main__':
    main()
