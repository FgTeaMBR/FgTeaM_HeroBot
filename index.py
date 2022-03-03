# -*- coding: utf-8 -*-

from datetime import datetime
from src.logger import logger
import func.login_func
import func.heroes_func
import func.files_func

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


login_attempts = 0
db = []

if not c['save_log_to_file']:
    logger('Warning, logs files are disable.')

images = func.load_images()
windows = func.windows_pyget()

# abrir a database a adiciona-la a lista.

try:
    db = func.resetDb()

# Caso der erro de leitura ou FileNotFound criar um novo.
except Exception:
    with open('db.json', 'w') as write:
        dados = [{"window": 0, "data": [
            [{"wallet": "account_1", "rest": "True", "heroes_work": 0, "heroes_rest": 0, "refresh_heroes": 0,
              "new_map": 0, "login_attempts": 0}],
            [{"wallet": "account_2", "rest": "False", "heroes_work": 0, "heroes_rest": 0, "refresh_heroes": 0,
              "new_map": 0, "login_attempts": 0}]

        ]}]
        json.dump(dados, write, indent=4)


# main loop
def main():
    global db
    count = 0

    # Caso o numero de windows na database for menor que as a janelas ativas atuais.
    while len(windows) > len(db):
        db.append(
            [{"window": count, "data": [
                [{"wallet": "account_1", "rest": "True", "heroes_work": 0, "heroes_rest": 0, "refresh_heroes": 0,
                  "new_map": 0, "login_attempts": 0}],
                [{"wallet": "account_2", "rest": "False", "heroes_work": 0, "heroes_rest": 0, "refresh_heroes": 0,
                  "new_map": 0, "login_attempts": 0}]

            ]}]
        )
        count += 1

    # Gravar as janelas que estao faltando na database
    with open('db.json', 'w') as data:
        json.dump(db, data, indent=4)

    while True:

        # Resetar a Database
        db = resetDb()

        # Para cada janela do Google Chrome na windows list
        for last in windows:

            # Para cada item na database
            for list_index in db:

                # Para cada item na window atual da database
                for k in list_index:

                    # Se a janela atual ativa do Chrome for igual a janela da database
                    if last['data'] == k['window']:
                        last["window"].activate()

                        print()
                        logger(f'Activating Bot Window {k["window"]}')

                        # Verificar se todas as janelas estao logadas.
                        islogged(last)

                        # Varrer a lista data.
                        for account_list in k['data']:

                            # Varrer a lista account com as wallets
                            for data_list in account_list:

                                # Checar o status atual , se esta trabalhando ou não.
                                if data_list['rest'] == 'False':

                                    # Se estiver trabalhando verificar se precisa colocar pra descansar
                                    now = time.time()
                                    if now - data_list["heroes_work"] > addRandomness(t['send_heroes_for_work'] * 60):
                                        logger(
                                            f'Window {last["data"]} {data_list["wallet"]} is working.')
                                        logger(
                                            f'Sending Window {last["data"]} {data_list["wallet"]} to rest.')

                                        if data_list['wallet'] == 'account_1':
                                            with open('db.json', 'r') as read:
                                                dados = json.load(read)
                                                with open('db.json', 'w') as write:
                                                    dados[k["window"]
                                                          ][0]['data'][0][0]['rest'] = 'True'
                                                    dados[k["window"]
                                                          ][0]['data'][1][0]['rest'] = 'False'
                                                    dados[k["window"]
                                                          ][0]['data'][1][0]['heroes_work'] = now
                                                    dados[k["window"]
                                                          ][0]['data'][0][0]['heroes_work'] = now
                                                    json.dump(
                                                        dados, write, indent=4)
                                            send_to_work('rest')
                                            select_wallet('account_2')
                                            if image_loop(images['connect-wallet'], 'Connect Wallet', click=False):
                                                islogged(last)
                                            send_to_work('all')

                                        else:
                                            with open('db.json', 'r') as read:
                                                dados = json.load(read)
                                                with open('db.json', 'w') as write:
                                                    dados[k["window"]
                                                          ][0]['data'][1][0]['rest'] = 'True'
                                                    dados[k["window"]
                                                          ][0]['data'][0][0]['rest'] = 'False'
                                                    dados[k["window"]
                                                          ][0]['data'][1][0]['heroes_work'] = now
                                                    dados[k["window"]
                                                          ][0]['data'][0][0]['heroes_work'] = now
                                                    json.dump(
                                                        dados, write, indent=4)
                                            send_to_work('rest')
                                            select_wallet('account_1')
                                            if image_loop(images['connect-wallet'], 'Connect Wallet', click=False):
                                                islogged(last)

                                            send_to_work('all')
                                    else:
                                        logger(
                                            f'Current status of Window {last["data"]}')
                                        logger(
                                            f'Current Working: {data_list["wallet"]}')

                                        next_reboot = data_list["heroes_work"] + (
                                            t["send_heroes_for_work"] * 60)
                                        next_refresh = data_list["refresh_heroes"] + (
                                            t["refresh_heroes_positions"] * 60)
                                        logger(
                                            f'Time for next hero Work: {datetime.fromtimestamp(next_reboot).strftime("%H:%M:%S")}. Current Set: {t["send_heroes_for_work"]} minutes.')
                                        logger(
                                            f'Time for next hero REFRESH: {datetime.fromtimestamp(next_refresh).strftime("%H:%M:%S")}. Current Set: {t["refresh_heroes_positions"]} minutes.')
                                    now = time.time()
                                    if now - data_list["refresh_heroes"] > addRandomness(
                                            t['refresh_heroes_positions'] * 60):
                                        if data_list['wallet'] == 'account_1':
                                            with open('db.json', 'r') as read:
                                                dados = json.load(read)
                                                with open('db.json', 'w') as write:
                                                    dados[k["window"]
                                                          ][0]['data'][0][0]['refresh_heroes'] = now
                                                    json.dump(
                                                        dados, write, indent=4)
                                                    refreshHeroesPositions()
                                        else:
                                            with open('db.json', 'r') as read:
                                                dados = json.load(read)
                                                with open('db.json', 'w') as write:
                                                    dados[k["window"]
                                                          ][0]['data'][1][0]['refresh_heroes'] = now
                                                    json.dump(
                                                        dados, write, indent=4)
                                                    refreshHeroesPositions()


if __name__ == '__main__':
    main()
