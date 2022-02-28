import yaml

from src.logger import logger
from func.image_reader import positions, load_images

# Load config file.
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']


def checkbaus():
    images = load_images()
    logger('🏢 Search for baus to map')

    bausroxo = positions(images['bau-roxo'], threshold=ct['bau_roxo'])
    bausroxomeio = positions(images['bau-roxo-50'], threshold=ct['bau_roxo_50'])

    bausGold = positions(images['bau-gold'], threshold=ct['bau_gold'])
    bausGoldMeio = positions(images['bau-gold-50'], threshold=ct['bau_gold_50'])

    bausBlue = positions(images['bau-blue'], threshold=ct['bau_blue'])
    bausBlueMeio = positions(images['bau-blue-50'], threshold=ct['bau_blue_50'])

    logger('🆗 %d baus roxo detected' % len(bausroxo))
    logger('🆗 %d baus roxo meia vida detected' % len(bausroxomeio))

    logger('🆗 %d baus gold detected' % len(bausGold))
    logger('🆗 %d baus gold meia vida detected' % len(bausGoldMeio))

    logger('🆗 %d baus blue detected' % len(bausBlue))
    logger('🆗 %d baus blue meia vida detected' % len(bausBlueMeio))

    global response
    if len(bausroxomeio) > 0 or len(bausGoldMeio) > 0 or len(bausBlueMeio) > 0:
        response = (
                           (len(bausroxomeio) + len(bausGoldMeio) + len(bausBlueMeio))
                           * 100
                   ) / (len(bausroxo) + len(bausGold) + len(bausBlue))
    else:
        response = 0

    return response