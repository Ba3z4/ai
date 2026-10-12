# Semana 1 · Sesión 3: Archivos y almacenamiento

Hoy hablamos de cómo se guardan las cosas.

Un disco, por sí solo, es un espacio vacío. Para usarlo se divide en particiones, que son como habitaciones separadas del mismo edificio. Cada partición se organiza con un sistema de archivos, que es el método de catalogación: cómo se nombran los archivos, dónde se guardan y qué información extra llevan, como la fecha de modificación o los permisos. Ejemplos comunes son NTFS en Windows, ext4 en Linux y APFS en macOS.

Un archivo tiene dos partes: el contenido y los metadatos. Los metadatos son datos sobre el archivo: su tamaño, quién lo creó, cuándo se modificó y quién puede leerlo. En investigación forense los metadatos cuentan historias enteras.

Algo muy importante: cuando borras un archivo normalmente, el sistema no destruye el contenido; solo marca ese espacio como disponible. Hasta que otro dato lo sobrescriba, el contenido sigue ahí. Por eso existen herramientas de recuperación, y por eso borrar de forma segura requiere sobrescribir o cifrar el disco.

También conviene saber que las carpetas del sistema tienen un propósito. En Linux, por ejemplo, la carpeta etc guarda configuración, var/log guarda los registros de lo que pasa, y home guarda los archivos de los usuarios. Conocer dónde mira un atacante, y dónde mira un defensor, empieza por conocer este mapa.

Para recordar: partición es una división del disco, sistema de archivos es el método de organización, metadatos son datos sobre los datos, y borrar no es destruir.
