from itertools import cycle
import random
import sys
import os
import argparse
import pickle

import pygame
from pygame.locals import *

sys.path.append(os.getcwd())

from bot import Bot


# Inicializar el bot
bot = Bot()

SCREENWIDTH = 288
SCREENHEIGHT = 512
# Cantidad por la cual la base puede desplazarse máximo hacia la izquierda
PIPEGAPSIZE = 100  # Brecha entre la parte superior e inferior de la tubería
BASEY = SCREENHEIGHT * 0.79

# Índices de ancho y alto de imagen para facilitar su uso
IM_WIDTH = 0
IM_HEIGTH = 1
# Imagen, Ancho, Alto
PIPE = [52, 320]
PLAYER = [34, 24]
BASE = [336, 112]
BACKGROUND = [288, 512]


def main():
    global HITMASKS, ITERATIONS, VERBOSE, bot

    parser = argparse.ArgumentParser("learn.py")
    parser.add_argument("--iter", type=int, default=1000, help="número de iteraciones a ejecutar")
    parser.add_argument(
        "--verbose", action="store_true", help="output [iteration | score] to stdout"
    )
    args = parser.parse_args()
    ITERATIONS = args.iter
    VERBOSE = args.verbose

    # cargar HITMASKS volcados
    with open("data/hitmasks_data.pkl", "rb") as input:
        HITMASKS = pickle.load(input)

    while True:
        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def showWelcomeAnimation():
    """Muestra la animación de la pantalla de bienvenida de Flappy Bird"""
    # Índice del jugador a mostrar en la pantalla
    playerIndexGen = cycle([0, 1, 2, 1])

    playery = int((SCREENHEIGHT - PLAYER[IM_HEIGTH]) / 2)

    basex = 0

    # Valores de movimiento arriba-abajo del jugador en la pantalla de bienvenida
    playerShmVals = {"val": 0, "dir": 1}

    return {
        "playery": playery + playerShmVals["val"],
        "basex": basex,
        "playerIndexGen": playerIndexGen,
    }


def mainGame(movementInfo):

    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo["playerIndexGen"]

    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo["playery"]

    basex = movementInfo["basex"]
    baseShift = BASE[IM_WIDTH] - BACKGROUND[IM_WIDTH]

    # Obtener 2 nuevas tuberías para agregar a las listas upperPipes y lowerPipes
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # Lista de tuberías superiores
    upperPipes = [
        {"x": SCREENWIDTH + 200, "y": newPipe1[0]["y"]},
        {"x": SCREENWIDTH + 200 + (SCREENWIDTH / 2), "y": newPipe2[0]["y"]},
    ]

    # Lista de tuberías inferiores
    lowerPipes = [
        {"x": SCREENWIDTH + 200, "y": newPipe1[1]["y"]},
        {"x": SCREENWIDTH + 200 + (SCREENWIDTH / 2), "y": newPipe2[1]["y"]},
    ]

    pipeVelX = -4

    # Velocidad del jugador, velocidad máxima, aceleración hacia abajo, aceleración al aletear
    playerVelY = -9  # Velocidad del jugador en el eje Y, igual a la velocidad al aletear
    playerMaxVelY = 10  # Velocidad máxima en el eje Y, máxima velocidad de descenso
    playerMinVelY = -8  # Velocidad mínima en el eje Y, máxima velocidad de ascenso
    playerAccY = 1  # Aceleración hacia abajo del jugador
    playerFlapAcc = -9  # Velocidad del jugador al aletear
    playerFlapped = False  # Verdadero cuando el jugador aletea

    while True:
        if -playerx + lowerPipes[0]["x"] > -30:
            myPipe = lowerPipes[0]
        else:
            myPipe = lowerPipes[1]

        if bot.act(-playerx + myPipe["x"], -playery + myPipe["y"], playerVelY):
            if playery > -2 * PLAYER[IM_HEIGTH]:
                playerVelY = playerFlapAcc
                playerFlapped = True

        # Comprobar colisiones aquí
        crashTest = checkCrash(
            {"x": playerx, "y": playery, "index": playerIndex}, upperPipes, lowerPipes
        )
        if crashTest[0]:
            # Actualizar las puntuaciones Q
            bot.update_scores(dump_qvalues=False)

            return {
                "y": playery,
                "groundCrash": crashTest[1],
                "basex": basex,
                "upperPipes": upperPipes,
                "lowerPipes": lowerPipes,
                "score": score,
                "playerVelY": playerVelY,
            }

        # Comprobar puntuación
        playerMidPos = playerx + PLAYER[IM_WIDTH] / 2
        for pipe in upperPipes:
            pipeMidPos = pipe["x"] + PIPE[IM_WIDTH] / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1

        # Cambio de índice de jugador y basex
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # Movimiento del jugador
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False
        playerHeight = PLAYER[IM_HEIGTH]
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # Mover las tuberías hacia la izquierda
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe["x"] += pipeVelX
            lPipe["x"] += pipeVelX

        # Agregar una nueva tubería cuando la primera está a punto de tocar el borde izquierdo de la pantalla
        if 0 < upperPipes[0]["x"] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # Eliminar la primera tubería si está fuera de la pantalla
        if upperPipes[0]["x"] < -PIPE[IM_WIDTH]:
            upperPipes.pop(0)
            lowerPipes.pop(0)


def showGameOverScreen(crashInfo):
    if VERBOSE:
        score = crashInfo["score"]
        print(str(bot.gameCNT - 1) + " | " + str(score))

    if bot.gameCNT == (ITERATIONS):
        bot.dump_qvalues(force=True)
        sys.exit()


def playerShm(playerShm):
    """oscila el valor de playerShm['val'] entre 8 y -8"""
    if abs(playerShm["val"]) == 8:
        playerShm["dir"] *= -1

    if playerShm["dir"] == 1:
        playerShm["val"] += 1
    else:
        playerShm["val"] -= 1


def getRandomPipe():
    """devuelve una tubería generada al azar"""
    # Altura de la brecha entre la parte superior e inferior de la tubería
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = PIPE[IM_HEIGTH]
    pipeX = SCREENWIDTH + 10

    return [
        {"x": pipeX, "y": gapY - pipeHeight},  # tuberia superior
        {"x": pipeX, "y": gapY + PIPEGAPSIZE},  # tuberi inferior
    ]


def checkCrash(player, upperPipes, lowerPipes):
    """devuelve True si el jugador colisiona con el suelo o las tuberías."""
    pi = player["index"]
    player["w"] = PLAYER[IM_WIDTH]
    player["h"] = PLAYER[IM_HEIGTH]

    # si el jugador colisiona con el suelo
    if (player["y"] + player["h"] >= BASEY - 1) or (player["y"] + player["h"] <= 0):
        return [True, True]
    else:

        playerRect = pygame.Rect(player["x"], player["y"], player["w"], player["h"])
        pipeW = PIPE[IM_WIDTH]
        pipeH = PIPE[IM_HEIGTH]

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # rectángulos de la tubería superior e inferior
            uPipeRect = pygame.Rect(uPipe["x"], uPipe["y"], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe["x"], lPipe["y"], pipeW, pipeH)

            # máscaras de colisión del jugador y las tuberías superior/inferior
            pHitMask = HITMASKS["player"][pi]
            uHitmask = HITMASKS["pipe"][0]
            lHitmask = HITMASKS["pipe"][1]

            # si el pájaro colisiona con la tubería superior o inferior
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Comprueba si dos objetos colisionan y no solo sus rectángulos."""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False


if __name__ == "__main__":
    main()
