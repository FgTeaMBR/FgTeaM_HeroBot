import PySimpleGUI as sg
from random import randint

sg.change_look_and_feel('Dark Blue 3')

layout = [[sg.Text('SpotGrid Watcher')],
          [sg.Text('Best Bid:')],
          [sg.Text(size=(60, 1), key='-LAZY-', font='Courier 14')],
          [sg.Button('Exit')]
          ]

window = sg.Window('Update Data', layout)

while True:  # Event Loop
    event, values = window.read(timeout=1000)  # Time in Milliseconds before returning

    #ticker = kucoin.market.get_ticker('ETN-USDT')
    best_bid = randint(1, 254)
    if event in (None, 'Exit'):
        break
    window['-LAZY-'].update(f'{best_bid}')
window.close()