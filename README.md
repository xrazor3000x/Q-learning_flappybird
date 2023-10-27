Flappy Bird Bot utilizando Aprendizaje por Refuerzo en Python
===================
Integrantes de presentacion-Ingenieria en Ciencias de la Computacion
-**Párraga Ortuste Diego Armando**
-**Miranda Gutierrez Cesar Alvaro**
-**Navia Condori Eddy**
===================
![4000+ scored](http://i.imgur.com/00Mf320.png)

Un bot de Flappy Bird en Python que aprende de cada partida a través del Aprendizaje por Refuerzo con Q-Learning.

----------
### Ejecución

La única dependencia del proyecto es `pygame`.

- `src/flappy.py` - Ejecutar para ver la jugabilidad visual real.
- `src/learn.py` - Ejecutar para un aprendizaje/entrenamiento más rápido. Esto se ejecuta sin ninguna visualización de pygame, por lo que es mucho más rápido.
  - Los siguientes argumentos de línea de comandos están disponibles:
    - `--verbose`  para ver la impresión de pares `iteration | score`  en cada iteración. (Iteración = una partida de un pájaro desde el principio hasta la muerte)
    - `--iter` número de iteraciones a ejecutar.
- `src/initialize_qvalues.py` - Ejecutar si deseas restablecer los valores Q, para que puedas observar cómo el pájaro aprende a jugar con el tiempo.
- `src/bot.py` - Este archivo contiene la clase `Bot` que aplica la lógica de Q-Learning al juego.
----------
### Cómo funciona

Con cada partida jugada, el pájaro observa los estados en los que ha estado y las acciones que tomó. Con respecto a sus resultados, castiga o recompensa los pares estado-acción. Después de jugar el juego numerosas veces, el pájaro puede obtener consistentemente puntuaciones altas.

Se utiliza un algoritmo de aprendizaje por refuerzo llamado [Q-learning](https://en.wikipedia.org/wiki/Q-learning) Este proyecto está fuertemente influenciado por el [awesome work of sarvagyavaish](http://sarvagyavaish.github.io/FlappyBirdRL/), pero cambié el espacio de estados y el algoritmo hasta cierto punto. El bot está diseñado para funcionar en una versión modificada del [Flappy Bird pygame clone of sourabhv](https://github.com/sourabhv/FlapPyBird).


**Creditos**

https://github.com/sourabhv/FlapPyBird

http://sarvagyavaish.github.io/FlappyBirdRL/

https://github.com/mihaibivol/Q-learning-tic-tac-toe
