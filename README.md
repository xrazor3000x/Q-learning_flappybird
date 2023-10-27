Flappy Bird Bot utilizando Aprendizaje por Refuerzo en Python
===================
Integrantes de presentacion-Ingenieria en Ciencias de la Computacion
-**Párraga Ortuste Diego Armando**
-**Miranda Gutierrez Cesar Alvaro**
-**Navia Condori Eddy**
===================
![4000+ scored](http://i.imgur.com/00Mf320.png)

Un bot de Flappy Bird en Python que aprende de cada partida a través del Aprendizaje por Refuerzo con Q-Learning.

[Youtube Link](https://www.youtube.com/watch?v=79BWQUN_Njc) 

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

----------
Definimos el espacio de estados y el conjunto de acciones, y el pájaro utiliza sus experiencias para recompensar diferentes pares estado-acción.

Definí los estados de manera un poco diferente a sarvagyavaish. En su versión, **las distancias horizontales y verticales desde la siguiente tubería** definen el estado del pájaro. Cuando escribí el programa para que funcionara de esta manera, descubrí que la convergencia lleva mucho tiempo. Entonces, en su lugar, discreticé las distancias a  **cuadrículas de 10x10**, lo que reduce significativamente el espacio de estados. Además, agregué la **velocidad vertical del pájaro** al espacio de estados.

También cambié un poco el algoritmo. En lugar de actualizar los valores Q con cada experiencia observada, fui hacia atrás después de cada juego jugado. Entonces, **los valores Q se calculan retrocediendo desde la última experiencia hasta la primera**. Supuse que esto ayudaría a propagar la información sobre los "estados malos" más rápido. Además, si el pájaro muere al **chocar con la parte superior de una tubería,**, la **acción en la que el pájaro saltó** se marca y se castiga adicionalmente. Esto funciona bien, ya que morir en la parte superior de la tubería es casi siempre el resultado de un mal salto. El marcado ayuda a propagar la información a este par [s, a] "malo" rápidamente.

![Learning Graph](http://i.imgur.com/Xm8WPYk.png)

As it can be seen, after around 1500 game iterations, the bot learns to play quite well, averaging about 150 score, and also occasionally hitting very good max scores.

----------
### Update

With **5x5 grids** instead of 10x10 (and also **y velocity** still in the state space), the convergence takes longer, but it converges to around 675 score, significantly beating the 150 score of the previous run. Also, the bird is able reach very high scores (3000+) quite many times.

![Learning Graph II](http://i.imgur.com/E3Vy0OR.png)


**Creditos**

https://github.com/sourabhv/FlapPyBird

http://sarvagyavaish.github.io/FlappyBirdRL/

https://github.com/mihaibivol/Q-learning-tic-tac-toe
