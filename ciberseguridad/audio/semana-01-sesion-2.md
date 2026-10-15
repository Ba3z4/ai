# Semana 1 · Sesión 2: Sistema operativo, kernel y procesos

Ya conoces las piezas físicas. Hoy hablamos del software que las coordina: el sistema operativo.

El sistema operativo, por ejemplo Windows, Linux, macOS o Android, es el gerente del restaurante. Decide qué programa usa la CPU y cuándo, reparte la RAM, y controla el acceso a archivos y dispositivos. Sin él, cada programa tendría que manejar el hardware por su cuenta, y sería un caos.

En el corazón del sistema operativo está el kernel, o núcleo. El kernel es la parte con control total sobre el hardware. Los programas normales no hablan con el hardware directamente: le piden al kernel que lo haga por ellos. Esa separación es una de las ideas más importantes de seguridad. Si un programa normal falla o es malicioso, el sistema intenta que no pueda destruir todo. Si alguien logra comprometer el kernel, controla la máquina entera.

Ahora, los procesos. Un programa es un archivo guardado, quieto. Un proceso es ese programa en ejecución. Si abres tres ventanas del navegador, puedes tener varios procesos del mismo programa. Cada proceso tiene su propia zona de memoria, aislada de las demás. Dentro de un proceso puede haber hilos: tareas que corren en paralelo, como un cocinero que corta mientras otro revuelve.

En seguridad, mirar los procesos es una habilidad básica. Un analista pregunta: ¿qué se está ejecutando? ¿Quién lo lanzó? ¿Tiene sentido que este proceso exista? Muchos programas maliciosos se esconden con nombres parecidos a los de procesos legítimos.

Para recordar: el sistema operativo coordina, el kernel manda sobre el hardware, un programa es un archivo y un proceso es ese programa vivo.

Tarea ligera para después: cuando tengas la computadora delante, abre el administrador de tareas y busca cinco procesos. Intenta averiguar para qué sirve cada uno.
