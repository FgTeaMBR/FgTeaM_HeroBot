# -*- coding: utf-8 -*-

import time
import yaml
import json

from datetime import datetime
from src.logger import logger
from func import Images, Heroes, Login, Mouse, Files


# Load config file.
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
ch = c['home']
api = c['discord_api']
t = c['time_intervals']

login = Login()
heroes = Heroes()
images = Images()
mouse = Mouse()
img = images.load_images()

files = Files()

login_attempts = 0
windows = files.windows_pyget()

db = []

if not c['save_log_to_file']:
    logger('Warning, logs files are disable.')

# Abrir a database, caso nao exista criar uma nova.

try:
    db = files.resetDb()

# Caso der erro de leitura ou FileNotFound criar um novo.
except Exception:
    logger('Database Not Found.')
    with open('db.json', 'w') as write:
        dados = [{"window": 0, "data": [
            [{"wallet": "account_1", "rest": "True", "heroes_work": 0, "heroes_rest": 0, "refresh_heroes": 0,
              "new_map": 0, "login_attempts": 0}],
            [{"wallet": "account_2", "rest": "False", "heroes_work": 0, "heroes_rest": 0, "refresh_heroes": 0,
              "new_map": 0, "login_attempts": 0}]

        ]}]
        json.dump(dados, write, indent=4)
    logger('Database created!!')


def main():
    global db
    count = len(db)

    # Caso o numero de windows na database for menor que as a janelas ativas atuais.
    while len(windows) > len(db):

        logger(f'Appeding window {count} to database.')
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
    files.write_data(db)

    while True:

        # Resetar a Database
        db = files.resetDb()

        # Para cada janela do Google Chrome na windows list
        for key, last in enumerate(windows):
            if last['data'] == db[key]['window']:
                
                # Ativar a janela correspondente a database.
                last["window"].activate()

                print()
                logger(f'Activating Bot Window {last["data"]}')

                # Verificar se todas as janelas estao logadas.
                login.is_logged(last)

                # Varrer a lista data.
                for account_list in db[key]['data']:

                    # Varrer a lista account com as wallets
                    for data_list in account_list:

                        # Checar o status atual , se esta trabalhando ou não.
                        if data_list['rest'] == 'False':

                            # Se estiver trabalhando verificar se precisa colocar pra descansar
                            now = time.time()
                            if now - data_list["heroes_work"] > mouse.add_randomness(t['send_heroes_for_work'] * 60):
                                logger(
                                    f'Window {last["data"]} {data_list["wallet"]} is working.')
                                logger(
                                    f'Sending Window {last["data"]} {data_list["wallet"]} to rest.')

                                if data_list['wallet'] == 'account_1':

                                    # Ler a database.
                                    dados = files.resetDb()

                                    # Setar as novas variaveis
                                    dados[key["window"]][0]['data'][0][0]['rest'] = 'True'
                                    dados[key["window"]][0]['data'][1][0]['rest'] = 'False'
                                    dados[key["window"]][0]['data'][1][0]['heroes_work'] = now
                                    dados[key["window"]][0]['data'][0][0]['heroes_work'] = now

                                    # Gravar os novos dados na database.
                                    files.write_data(dados)

                                    # Enviar os heroes para descansar.
                                    heroes.send_work('rest')

                                    # Selecionar a waller que irá trabalhar.
                                    login.select_wallet('account_2')

                                    # Aguardar aparecer o connect button para logar novamente.
                                    if images.image_loop(img['connect-wallet'], 'Connect Wallet', click=False):
                                        login.is_logged(last)

                                    # Enviar os heroes para trabalhar.
                                    heroes.send_work('all')

                                else:
                                    # Ler a database
                                    dados = files.resetDb()

                                    # Setar as novas variaveis
                                    dados[key["window"]][0]['data'][1][0]['rest'] = 'True'
                                    dados[key["window"]][0]['data'][0][0]['rest'] = 'False'
                                    dados[key["window"]][0]['data'][1][0]['heroes_work'] = now
                                    dados[key["window"]][0]['data'][0][0]['heroes_work'] = now

                                    # Gravar os novos dados na database. 
                                    files.write_data(dados)

                                    # Enviar os herois para descansar.
                                    heroes.send_work('rest')

                                    # Selecionar a nova wallet que irá trabalhar.
                                    login.select_wallet('account_1')

                                    # Esperar aparecer o botão de connect
                                    if images.image_loop(img['connect-wallet'], 'Connect Wallet', click=False):
                                        login.is_logged(last)

                                    # Enviar todos os herois para trabalhar.
                                    heroes.send_work('all')
                            else:

                                # Se não estiver na hora de enviar pra descansar , printar as mensagens de log.
                                logger(f'Current status of Window {last["data"]}')
                                logger(f'Current Working: {data_list["wallet"]}')

                                next_reboot = data_list["heroes_work"] + (t["send_heroes_for_work"] * 60)
                                next_refresh = data_list["refresh_heroes"] + (t["refresh_heroes_positions"] * 60)
                                logger(f'Time for next hero Work: {datetime.fromtimestamp(next_reboot).strftime("%H:%M:%S")}. Current Set: {t["send_heroes_for_work"]} minutes.')
                                logger(f'Time for next hero REFRESH: {datetime.fromtimestamp(next_refresh).strftime("%H:%M:%S")}. Current Set: {t["refresh_heroes_positions"]} minutes.')

                                # Fim das menssagens de log.
                            
                            # Ativar o refresh heroes.
                            now = time.time()
                            if now - data_list["refresh_heroes"] > mouse.add_randomness(t['refresh_heroes_positions'] * 60):

                                # Caso seja a o account_1.
                                if data_list['wallet'] == 'account_1':

                                    # Ler os dados da database.
                                    dados = files.resetDb()

                                    # Setar as novas variaveis.
                                    dados[key["window"]][0]['data'][0][0]['refresh_heroes'] = now

                                    # Gravar os novos dados na database.
                                    files.write_data(dados)

                                    # Fazer o refresh heroes para salvar o status atual do mapa.
                                    heroes.refresh_heroes_positions()
                                else:
                                    # Ler os dados da database.
                                    dados = files.resetDb()

                                    # Setar as novas variaveis.S
                                    dados[key["window"]][0]['data'][1][0]['refresh_heroes'] = now
                                    
                                    # Gravar os novos dados na database.
                                    files.write_data(dados)

                                    # Fazer o refresh heroes para salvar o status atual do mapa.
                                    heroes.refresh_heroes_positions()


if __name__ == '__main__':
    main()
