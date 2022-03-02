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


def test(wallet, data, last, mode):
    """Seleciona a wallet que irá trabalhar ou descansar (STR) ex: account_1 ou account_2


    :Parametros

        :wallet Recebe a wallet  em forma de string
            que irá trabalhar. EX: account_1 ou account_2.

        :data Recebe a dabatase em forma de lista.

        :windows Recebe a janela ativa para analise.
    """

    # n para saber qual janela do chrome deve ativar.

    for list_index in data:

        # Se a janela for igual a database.
        if list_index['window'] == last['data']:
            # last['window'].activate()

            # Varrer a lista data.
            for account_list in list_index['data']:

                # Varrer a lista account com as wallets
                for data_list in account_list:

                    # Checar o status atual , se esta trabalhando ou não.
                    if data_list['rest'] == 'False':

                        # Se estiver trabalhando verificar se precisa colocar pra descansar
                        now = time.time()
                        if now - data_list["heroes_work"] > addRandomness(t['send_heroes_for_work'] * 60):
                            logger(f'Window {last["data"]} {wallet} is working.')
                            logger(f'Sending Window {last["data"]} {wallet} to rest.')

                            if data_list['wallet'] == 'account_1':
                                with open('db.json', 'r') as read:
                                    dados = json.load(read)
                                    with open('db.json', 'w') as write:
                                        dados[last['data']]['data'][0][0]['rest'] = 'True'
                                        json.dump(dados, write, indent=4)
                                select_wallet('account_2')
                                pyautogui.hotkey('ctrl', 'f5')
                                login()
                                logger('Sending current wallet to idle and rest.')

                                send_to_work(list_index, last, 'rest')
                            else:
                                with open('db.json', 'r') as read:
                                    dados = json.load(read)
                                    with open('db.json', 'w') as write:
                                        dados[last['data']]['data'][1][0]['rest'] = 'True'
                                        dados[last['data']]['data'][0][0]['rest'] = 'False'
                                        dados[last['data']]['data'][1][0]['heroes_work'] = now
                                        dados[last['data']]['data'][0][0]['heroes_work'] = now
                                        json.dump(dados, write, indent=4)
                                select_wallet('account_1')
                                pyautogui.hotkey('ctrl', 'f5')
                                logger('Sending current wallet to idle and rest.')
                                login()
                        else:
                            logger(f'Current status of Window {last["data"]}')
                            logger(f'Current Working: {wallet}')

                            next_reboot = data_list["heroes_work"] + (t["send_heroes_for_work"] * 60)
                            next_refresh = data_list["refresh_heroes"] + (t["refresh_heroes_positions"] * 60)
                            logger(
                                f'Time for next hero Work: {datetime.fromtimestamp(next_reboot).strftime("%H:%M:%S")}. Current Set: {t["send_heroes_for_work"]} minutes.')
                            logger(
                                f'Time for next hero REFRESH: {datetime.fromtimestamp(next_refresh).strftime("%H:%M:%S")}. Current Set: {t["refresh_heroes_positions"]} minutes.')