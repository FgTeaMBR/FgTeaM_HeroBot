import pygetwindow
from func.mouse_move import *
import time


def windows_pyget():
    """:retorna uma lista com todas as janelas do Google Chrome ativas
        com o jogo Bombcrypto.
    """
    windows = []
    count = 0
    for w in pygetwindow.getWindowsWithTitle('Bombcrypto - Google Chrome'):
        windows.append(
            {
                "data": count,
                "window": w,
            })
        count += 1
    return windows


