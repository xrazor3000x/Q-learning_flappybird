import json


class Bot(object):
    """
    La clase Bot que aplica la lógica de Q-learning al juego Flappy Bird
    Después de cada iteración (iteración = 1 juego que termina con la muerte del pájaro), actualiza los valores de Q
    Después de cada DUMPING_N iteraciones, almacena los valores de Q en un archivo JSON local
    """

    def __init__(self):
        self.gameCNT = 0   # Conteo de juegos de la corrida actual, se incrementa después de cada muerte
        self.DUMPING_N = 25  # Número de iteraciones para almacenar los valores de Q en JSON después
        self.discount = 1.0
        self.r = {0: 1, 1: -1000}  # Función de recompensa
        self.lr = 0.7
        self.load_qvalues()
        self.last_state = "420_240_0"
        self.last_action = 0
        self.moves = []

    def load_qvalues(self):
        """
        Carga los valores de Q desde un archivo JSON
        """
        self.qvalues = {}
        try:
            fil = open("data/qvalues.json", "r")
        except IOError:
            return
        self.qvalues = json.load(fil)
        fil.close()

    def act(self, xdif, ydif, vel):
        """
        Elige la mejor acción con respecto al estado actual - Elige 0 (no aletear) en caso de empate
        """
        state = self.map_state(xdif, ydif, vel)

        self.moves.append(
            (self.last_state, self.last_action, state)
        )   # Agrega la experiencia al historial

        self.last_state = state  # Actualiza el último estado con el estado actual

        if self.qvalues[state][0] >= self.qvalues[state][1]:
            self.last_action = 0
            return 0
        else:
            self.last_action = 1
            return 1

    def update_scores(self, dump_qvalues=True):
        """
        Actualiza los valores de Q iterando sobre las experiencias
        """
        history = list(reversed(self.moves))

        # Bandera si el pájaro murió en la tubería superior
        high_death_flag = True if int(history[0][2].split("_")[1]) > 120 else False

        # Actualizaciones de puntuación de Q-learning
        t = 1
        for exp in history:
            state = exp[0]
            act = exp[1]
            res_state = exp[2]

            # Seleccionar recompensa
            if t == 1 or t == 2:
                cur_reward = self.r[1]
            elif high_death_flag and act:
                cur_reward = self.r[1]
                high_death_flag = False
            else:
                cur_reward = self.r[0]

            # Actualizar
            self.qvalues[state][act] = (1-self.lr) * (self.qvalues[state][act]) + \
                                       self.lr * ( cur_reward + self.discount*max(self.qvalues[res_state]) )

            t += 1

        self.gameCNT += 1  # Aumentar el conteo de juegos
        if dump_qvalues:
            self.dump_qvalues()   # Almacena los valores de Q (si gameCNT % DUMPING_N == 0)
        self.moves = []  # Limpiar el historial después de actualizar estrategias

    def map_state(self, xdif, ydif, vel):
        """
        Asocia el (xdif, ydif, vel) al estado correspondiente, en relación a las cuadrículas
        El estado es una cadena, "xdif_ydif_vel"

        X -> [-40,-30...120] U [140, 210 ... 420]
        Y -> [-300, -290 ... 160] U [180, 240 ... 420]
        """
        if xdif < 140:
            xdif = int(xdif) - (int(xdif) % 10)
        else:
            xdif = int(xdif) - (int(xdif) % 70)

        if ydif < 180:
            ydif = int(ydif) - (int(ydif) % 10)
        else:
            ydif = int(ydif) - (int(ydif) % 60)

        return str(int(xdif)) + "_" + str(int(ydif)) + "_" + str(vel)

    def dump_qvalues(self, force=False):
        """
        Almacena los valores de Q en el archivo JSON
        """
        if self.gameCNT % self.DUMPING_N == 0 or force:
            fil = open("data/qvalues.json", "w")
            json.dump(self.qvalues, fil)
            fil.close()
            print("Valores de Q actualizados en el archivo local.")
