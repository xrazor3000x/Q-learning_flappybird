from itertools import cycle  # Importa la función "cycle" de la biblioteca "itertools".
import random  # Importa la biblioteca "random" que proporciona generación de números aleatorios.
import sys  # Importa el módulo "sys" que proporciona acceso a variables y funciones relacionadas con el sistema.
import os  # Importa el módulo "os" que proporciona funciones para interactuar con el sistema operativo.
import argparse  # Importa la biblioteca "argparse" para analizar argumentos de línea de comandos.
import pickle  # Importa la biblioteca "pickle" que se utiliza para serializar y deserializar objetos en Python.
import pygame  # Importa la biblioteca "pygame" que se utiliza para crear juegos y aplicaciones multimedia en Python.
from pygame.locals import *  # Importa todas las constantes y clases de "pygame.locals" para su uso en el código.

sys.path.append(os.getcwd())

from bot import Bot

# Inicializa el bot
bot = Bot()

SCREENWIDTH = 288
SCREENHEIGHT = 512
# cantidad por la cual la base puede desplazarse como máximo a la izquierda
PIPEGAPSIZE = 100  # espacio entre la parte superior e inferior de la tubería
BASEY = SCREENHEIGHT * 0.79
# diccionarios de imágenes, sonidos y hitmasks
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# lista de todos los posibles jugadores (tupla de 3 posiciones de aleteo)
PLAYERS_LIST = (
    # pájaro rojo
    (
        "data/assets/sprites/redbird-upflap.png",
        "data/assets/sprites/redbird-midflap.png",
        "data/assets/sprites/redbird-downflap.png",
    ),
    # pájaro azul
    (
        # amount by which base can maximum shift to left
        "data/assets/sprites/bluebird-upflap.png",
        "data/assets/sprites/bluebird-midflap.png",
        "data/assets/sprites/bluebird-downflap.png",
    ),
    # pájaro amarillo
    (
        "data/assets/sprites/yellowbird-upflap.png",
        "data/assets/sprites/yellowbird-midflap.png",
        "data/assets/sprites/yellowbird-downflap.png",
    ),
)

# lista de fondos
BACKGROUNDS_LIST = (
    "data/assets/sprites/background-day.png",
    "data/assets/sprites/background-night.png",
)

# lista de tuberías
PIPES_LIST = ("data/assets/sprites/pipe-green.png", "data/assets/sprites/pipe-red.png")


def main():
    global SCREEN, FPSCLOCK, FPS, bot

    parser = argparse.ArgumentParser("flappy.py")
    parser.add_argument("--fps", type=int, default=60, help="number of frames per second")
    parser.add_argument(
        "--dump_hitmasks", action="store_true", help="dump hitmasks to file and exit"
    )
    args = parser.parse_args()

    FPS = args.fps

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption("Flappy Bird")

    # imágenes de números para mostrar la puntuación
    IMAGES["numbers"] = (
        pygame.image.load("data/assets/sprites/0.png").convert_alpha(),
        pygame.image.load("data/assets/sprites/1.png").convert_alpha(),
        pygame.image.load("data/assets/sprites/2.png").convert_alpha(),
        pygame.image.load("data/assets/sprites/3.png").convert_alpha(),
        pygame.image.load("data/assets/sprites/4.png").convert_alpha(),
        pygame.image.load("data/assets/sprites/5.png").convert_alpha(),
        pygame.image.load("data/assets/sprites/6.png").convert_alpha(),
        pygame.image.load("data/assets/sprites/7.png").convert_alpha(),
        pygame.image.load("data/assets/sprites/8.png").convert_alpha(),
        pygame.image.load("data/assets/sprites/9.png").convert_alpha(),
    )

    # sprite de fin del juego
    IMAGES["gameover"] = pygame.image.load("data/assets/sprites/gameover.png").convert_alpha()
    # sprite de mensaje para la pantalla de bienvenida
    IMAGES["message"] = pygame.image.load("data/assets/sprites/message.png").convert_alpha()
    # sprite de la base (suelo)
    IMAGES["base"] = pygame.image.load("data/assets/sprites/base.png").convert_alpha()

    # sonidos
    if "win" in sys.platform:
        soundExt = ".wav"
    else:
        soundExt = ".ogg"

    SOUNDS["die"] = pygame.mixer.Sound("data/assets/audio/die" + soundExt)
    SOUNDS["hit"] = pygame.mixer.Sound("data/assets/audio/hit" + soundExt)
    SOUNDS["point"] = pygame.mixer.Sound("data/assets/audio/point" + soundExt)
    SOUNDS["swoosh"] = pygame.mixer.Sound("data/assets/audio/swoosh" + soundExt)
    SOUNDS["wing"] = pygame.mixer.Sound("data/assets/audio/wing" + soundExt)

    while True:
        # seleccionar imágenes de fondo al azar
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES["background"] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # seleccionar imágenes de jugador al azar
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES["player"] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # seleccionar imágenes de tubería al azar
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES["pipe"] = (
            pygame.transform.rotate(pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # Máscaras de colisión para las tuberías
        HITMASKS["pipe"] = (getHitmask(IMAGES["pipe"][0]), getHitmask(IMAGES["pipe"][1]))

        # Máscaras de colisión para el jugador
        HITMASKS["player"] = (
            getHitmask(IMAGES["player"][0]),
            getHitmask(IMAGES["player"][1]),
            getHitmask(IMAGES["player"][2]),
        )

        if args.dump_hitmasks:
            with open("data/hitmasks_data.pkl", "wb") as output:
                pickle.dump(HITMASKS, output, pickle.HIGHEST_PROTOCOL)
            sys.exit()

        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def showWelcomeAnimation():
    """Muestra la animación de la pantalla de bienvenida de Flappy Bird"""
    # Índice del jugador para mostrar en la pantalla
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
     # Iterador utilizado para cambiar playerIndex después de cada 5ta iteración
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES["player"][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES["message"].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # Cantidad por la cual la base puede desplazarse máximo hacia la izquierda
    baseShift = IMAGES["base"].get_width() - IMAGES["background"].get_width()

    # Valores de playerShm para el movimiento arriba-abajo en la pantalla de bienvenida
    playerShmVals = {"val": 0, "dir": 1}

    while True:
        """ Funcionalidad de presionar tecla desactivada

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for mainGame
                SOUNDS['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }
        """
        SOUNDS["wing"].play()
        return {
            "playery": playery + playerShmVals["val"],
            "basex": basex,
            "playerIndexGen": playerIndexGen,
        }

        # Ajustar playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # Dibujar los sprites
        SCREEN.blit(IMAGES["background"], (0, 0))
        SCREEN.blit(IMAGES["player"][playerIndex], (playerx, playery + playerShmVals["val"]))
        SCREEN.blit(IMAGES["message"], (messagex, messagey))
        SCREEN.blit(IMAGES["base"], (basex, BASEY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame(movementInfo):

    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo["playerIndexGen"]

    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo["playery"]

    basex = movementInfo["basex"]
    baseShift = IMAGES["base"].get_width() - IMAGES["background"].get_width()

    # Obtener 2 nuevos tubos para agregar a la lista upperPipes y lowerPipes
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # Lista de tubos superiores
    upperPipes = [
        {"x": SCREENWIDTH + 200, "y": newPipe1[0]["y"]},
        {"x": SCREENWIDTH + 200 + (SCREENWIDTH / 2), "y": newPipe2[0]["y"]},
    ]

    # Lista de tubos inferiores
    lowerPipes = [
        {"x": SCREENWIDTH + 200, "y": newPipe1[1]["y"]},
        {"x": SCREENWIDTH + 200 + (SCREENWIDTH / 2), "y": newPipe2[1]["y"]},
    ]

    pipeVelX = -4

    # Velocidad del jugador, velocidad máxima, aceleración hacia abajo, aceleración en el salto
    playerVelY = -9  # velocidad del jugador en el eje Y, por defecto es igual a playerFlapped
    playerMaxVelY = 10  # velocidad máxima en el eje Y, velocidad máxima de descenso
    playerMinVelY = -8  # velocidad mínima en el eje Y, velocidad máxima de ascenso
    playerAccY = 1  # aceleración hacia abajo del jugador
    playerFlapAcc = -9  # velocidad del jugador al aletear
    playerFlapped = False  # Verdadero cuando el jugador aletea

    while True:
        if -playerx + lowerPipes[0]["x"] > -30:
            myPipe = lowerPipes[0]
        else:
            myPipe = lowerPipes[1]

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * IMAGES["player"][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    SOUNDS["wing"].play()

        if bot.act(-playerx + myPipe["x"], -playery + myPipe["y"], playerVelY):
            if playery > -2 * IMAGES["player"][0].get_height():
                playerVelY = playerFlapAcc
                playerFlapped = True
                SOUNDS["wing"].play()

        # Verificar colisión aquí
        crashTest = checkCrash(
            {"x": playerx, "y": playery, "index": playerIndex}, upperPipes, lowerPipes
        )
        if crashTest[0]:
            # Actualizar las puntuaciones Q
            bot.update_scores()

            return {
                "y": playery,
                "groundCrash": crashTest[1],
                "basex": basex,
                "upperPipes": upperPipes,
                "lowerPipes": lowerPipes,
                "score": score,
                "playerVelY": playerVelY,
            }

        # Verificar puntuación
        playerMidPos = playerx + IMAGES["player"][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe["x"] + IMAGES["pipe"][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                SOUNDS["point"].play()

        # Cambio de índice del jugador y basex
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # Movimiento del jugador
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False
        playerHeight = IMAGES["player"][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # Mover los tubos hacia la izquierda
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe["x"] += pipeVelX
            lPipe["x"] += pipeVelX

        # Agregar nuevo tubo cuando el primer tubo está a punto de tocar la izquierda de la pantalla
        if 0 < upperPipes[0]["x"] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # Quitar el primer tubo si está fuera de la pantalla
        if upperPipes[0]["x"] < -IMAGES["pipe"][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Dibujar los sprites
        SCREEN.blit(IMAGES["background"], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES["pipe"][0], (uPipe["x"], uPipe["y"]))
            SCREEN.blit(IMAGES["pipe"][1], (lPipe["x"], lPipe["y"]))

        SCREEN.blit(IMAGES["base"], (basex, BASEY))
        # Mostrar la puntuación para que el jugador se superponga a ella
        showScore(score)
        SCREEN.blit(IMAGES["player"][playerIndex], (playerx, playery))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def showGameOverScreen(crashInfo):
    """Hace que el jugador caiga y muestra la imagen de fin de juego"""
    score = crashInfo["score"]
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo["y"]
    playerHeight = IMAGES["player"][0].get_height()
    playerVelY = crashInfo["playerVelY"]
    playerAccY = 2

    basex = crashInfo["basex"]

    upperPipes, lowerPipes = crashInfo["upperPipes"], crashInfo["lowerPipes"]

    # Reproducir sonidos de colisión y muerte
    SOUNDS["hit"].play()
    if not crashInfo["groundCrash"]:
        SOUNDS["die"].play()

    while True:
        """ Desactivar funcionalidad de tecla presionada
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return
        """
        return  ### Debe eliminarse para activar la funcionalidad de tecla presionada

        # Cambio en la posición vertical del jugador (eje Y)
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # Cambio en la velocidad del jugador
        if playerVelY < 15:
            playerVelY += playerAccY

        # Dibujar los sprites
        SCREEN.blit(IMAGES["background"], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES["pipe"][0], (uPipe["x"], uPipe["y"]))
            SCREEN.blit(IMAGES["pipe"][1], (lPipe["x"], lPipe["y"]))

        SCREEN.blit(IMAGES["base"], (basex, BASEY))
        showScore(score)
        SCREEN.blit(IMAGES["player"][1], (playerx, playery))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):
    """Oscila el valor de playerShm['val'] entre 8 y -8"""
    if abs(playerShm["val"]) == 8:
        playerShm["dir"] *= -1

    if playerShm["dir"] == 1:
        playerShm["val"] += 1
    else:
        playerShm["val"] -= 1


def getRandomPipe():
    """Devuelve un tubo generado aleatoriamente"""
    # Altura de la brecha entre el tubo superior e inferior
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES["pipe"][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {"x": pipeX, "y": gapY - pipeHeight},  # upper pipe
        {"x": pipeX, "y": gapY + PIPEGAPSIZE},  # lower pipe
    ]


def showScore(score):
    """Muestra la puntuación en el centro de la pantalla"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0   # Ancho total de todos los números que se van a imprimir

    for digit in scoreDigits:
        totalWidth += IMAGES["numbers"][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES["numbers"][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES["numbers"][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """Devuelve True si el jugador colisiona con el suelo o los tubos."""
    pi = player["index"]
    player["w"] = IMAGES["player"][0].get_width()
    player["h"] = IMAGES["player"][0].get_height()

    # Si el jugador colisiona con el suelo
    if (player["y"] + player["h"] >= BASEY - 1) or (player["y"] + player["h"] <= 0):
        return [True, True]
    else:

        playerRect = pygame.Rect(player["x"], player["y"], player["w"], player["h"])
        pipeW = IMAGES["pipe"][0].get_width()
        pipeH = IMAGES["pipe"][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # Rectángulos de tubo superior e inferior
            uPipeRect = pygame.Rect(uPipe["x"], uPipe["y"], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe["x"], lPipe["y"], pipeW, pipeH)

            # Hitmasks del jugador y los tubos superior/inferior
            pHitMask = HITMASKS["player"][pi]
            uHitmask = HITMASKS["pipe"][0]
            lHitmask = HITMASKS["pipe"][1]

            # Si el pájaro colisiona con el tubo superior o el tubo inferior
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Verifica si dos objetos colisionan y no solo sus rectángulos."""
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


def getHitmask(image):
    """Devuelve un hitmask utilizando la transparencia de una imagen."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


if __name__ == "__main__":
    main()
