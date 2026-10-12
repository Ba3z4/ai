# Semana 1 · Sesión 4: La memoria de un programa

Esta lección es un poco más abstracta, pero te da una base que más adelante se vuelve muy valiosa. Vamos a ver cómo un programa usa la memoria, solo a nivel de concepto.

Cuando un proceso corre, el sistema le da un espacio de memoria virtual. Es una ilusión útil: cada programa cree que tiene toda la memoria para él solo, y el sistema se encarga de traducir esas direcciones a la RAM real. Gracias a esto, un proceso no puede leer la memoria de otro sin permiso.

Dentro de ese espacio hay zonas principales. Una es el código, las instrucciones del programa. Otra es el stack o pila, donde se guardan las variables temporales y el recuerdo de a dónde volver cuando termina una función. La pila funciona como una pila de platos: lo último que pones es lo primero que sacas. La otra zona es el heap o montón, para datos que necesitan vivir más tiempo y cuyo tamaño puede cambiar.

¿Por qué importa en seguridad? Porque muchos errores famosos nacen aquí. Si un programa reserva un espacio pequeño y luego intenta meter más datos de los que caben, esos datos se desbordan hacia memoria vecina. A eso se le llama desbordamiento de búfer. Si lo que se sobrescribe es algo importante, como la dirección de retorno de la pila, un atacante podría desviar el programa. Hoy hay defensas para reducir ese riesgo, y los lenguajes modernos evitan buena parte del problema, pero entenderlo explica por qué hay tanto énfasis en validar los datos de entrada.

No tienes que dominar esto ahora. Solo quédate con la idea: la memoria está dividida en zonas, y los errores al manejarla son una fuente clásica de vulnerabilidades.

Para recordar: memoria virtual aísla procesos, stack guarda lo temporal, heap guarda lo dinámico, y un desbordamiento ocurre cuando entra más de lo que cabe.
