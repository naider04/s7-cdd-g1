# Desarrollo de un simulador interactivo en Python para visualizar el encapsulamiento y desencapsulamiento de datos en las 7 capas del Modelo OSI

**Autor:** Wilmer Patiño
**Curso:** Data Communication (4th semester)
**Fecha:** 26 de septiembre de 2026
**Entorno de desarrollo:** Python 3.14.7 sobre Linux 6.19.10-300.fc44.x86_64, interfaz gráfica con Tkinter, sin dependencias externas.

---

## Índice

1. Introducción
2. Objetivos
3. Marco teórico: el modelo OSI
4. Diccionario de funciones
5. Lógica de las siete capas en el motor
6. Manual de usuario
7. Resultados y evidencias
8. Conclusiones
9. Bibliografía
10. Declaración de uso de inteligencia artificial

---

## 1. Introducción

La teoría de las capas del modelo OSI suele resultar abstracta para quien la estudia por primera vez: resulta difícil visualizar cómo un simple texto de chat se convierte, capa por capa, en una cadena de bits que viaja por un cable y vuelve a convertirse en texto legible. Los simuladores de red habituales muestran diagramas estáticos, pero no construyen datos byte a byte ni verifican la integridad de la trama.

Este proyecto desarrolla un simulador educativo interactivo en Python que hace visible ese proceso de transformación. La aplicación combina un menú de misiones con decisiones de protocolo, un lienzo de red animado, un inspector de paquetes, un módulo de diagnóstico y reparación, y un laboratorio de cascada OSI donde el motor de red construye realmente la trama: serializa la carga en base64, agrega cabeceras TCP e IPv4, calcula el checksum de Internet, construye el marco Ethernet con preámbulo y FCS/CRC32, y finalmente convierte el marco completo en una cadena de bits. Al recibir, el simulador recorre el camino inverso validando el CRC32, retirando cada cabecera y reconstruyendo el mensaje original. De esa forma, el estudiante puede comprobar con sus propios ojos, y con datos verificables, que la información viaja intacta o es descartada cuando el medio la corrompe.

## 2. Objetivos

### Objetivo general

Desarrollar un simulador interactivo en Python que visualice, de forma práctica y verificable, el proceso de encapsulamiento y desencapsulamiento de datos a través de las siete capas del modelo OSI, aplicando los conceptos de Data Communication dentro de un entorno gráfico usable por estudiantes.

### Objetivos específicos

1. Implementar un motor OSI que construya bytes reales en cada capa: base64, cabeceras TCP e IPv4, checksum, marco Ethernet con preámbulo y FCS/CRC32, y conversión a bits.
2. Recorrer las siete capas en orden ascendente (L7 a L1) al enviar y en orden descendente (L1 a L7) al recibir, explicando la acción de cada capa.
3. Incorporar la función `transmitir()` como punto de entrada que ejecuta la transmisión completa y devuelve métricas, pasos e indicadores de integridad.
4. Detectar corrupción en el medio mediante el CRC32 y el checksum IP, y reportar en qué capa se detecta el error.
5. Ofrecer una interfaz gráfica Tkinter con menú de misiones, decisiones de protocolo, inspector de paquetes, diagnóstico y el laboratorio de cascada.
6. Validar el motor con pruebas automáticas que comprueben la ida y vuelta del mensaje, el orden de las capas, los cálculos de checksum y CRC32, y la detección de errores.
7. Documentar el sistema con evidencias gráficas reales y un análisis de resultados que sustente las conclusiones.

## 3. Marco teórico: el modelo OSI

El modelo de referencia OSI (Open Systems Interconnection), definido por la ISO, divide la comunicación en siete capas abstractas con responsabilidades bien delimitadas. Cada capa ofrece un servicio a la capa superior y usa los servicios de la capa inferior, de modo que la red se comporta como una pila donde los datos se encapsulan al descender y se desencapsulan al ascender.

| Capa | Nombre | Responsabilidad en el simulador |
|------|--------|--------------------------------|
| 7 | Aplicación | Genera los datos de usuario (el mensaje) y la petición del protocolo de aplicación. |
| 6 | Presentación | Codifica el texto a UTF-8 y serializa la carga en base64 para hacerla transportable. |
| 5 | Sesión | Abre el canal lógico y asigna un identificador de sesión (token) derivado del mensaje. |
| 4 | Transporte | Agrega la cabecera TCP (puertos, secuencia, acuse, banderas, ventana) y segmenta el flujo. |
| 3 | Red | Agrega la cabecera IPv4, direcciona el paquete con IP origen/destino y calcula el checksum. |
| 2 | Enlace de datos | Construye el marco Ethernet con direcciones MAC, EtherType, preámbulo y el FCS basado en CRC32. |
| 1 | Física | Convierte el marco entero en una cadena de bits y lo transmite por el medio físico. |

Conceptos clave aplicados:

- **Encapsulamiento:** cada capa añade su cabecera y control a los datos de la capa superior, formando una jerarquía de envoltorios.
- **Desencapsulamiento:** proceso inverso donde cada capa retira su cabecera y entrega la carga limpia a la capa superior, verificando la integridad.
- **Base64:** codificación que transforma cualquier carga binaria en texto ASCII usando un alfabeto de 64 símbolos, apta para transportar datos en entornos que solo manejan texto. Su crecimiento es de aproximadamente un 33 % (`4/3`).
- **Checksum IP:** suma de complementos de 16 bits de la cabecera IPv4, que permite detectar errores de cabecera en la capa de red.
- **CRC32 (FCS):** código de redundancia cíclica de 32 bits (polinomio `0x04C11DB7`) que la capa de enlace añade al final del marco (Frame Check Sequence) para detectar corrupción en el medio.
- **Trama, paquete, segmento y datagrama:** nombre que recibe la unidad de datos según la capa que la origina: segmento en transporte, paquete en red, trama en enlace.

## 4. Diccionario de funciones

A continuación se documenta cada función del motor `osi_engine.py` con su objetivo, parámetros, valor devuelto y la capa OSI con la que se relaciona.

### 4.1 `transmitir(mensaje, **opciones)`

- **Objetivo:** ejecutar la transmisión completa tal como ocurre entre PC-A y PC-B: encapsula en el emisor, desencapsula en el receptor, compara el mensaje recuperado con el original y devuelve todas las métricas y los 14 pasos (7 de envío y 7 de recepción).
- **Capa:** integra las siete capas (L7 a L1 y L1 a L7).
- **Parámetros:**
  - `mensaje` (str): texto que la persona usuaria escribe y que desea enviar.
  - `**opciones`: acepta opcionalmente los parámetros de `encapsular` (protocolo, recurso, IP origen/destino, puertos, MAC, número de secuencia y medio).
- **Resultado:** un objeto `ResultadoTransmision` con los pasos del emisor y del receptor, la carga en base64, los bytes (originales, base64 y de la trama), los bits totales, la trama en bytes y en bits, el CRC32, el checksum IP, las banderas de validez (`fcs_valido`, `checksum_ip_valido`) y la propiedad derivada `integridad_ok`.
- **Uso en el simulador:** es el botón `Transmitir ▶` del laboratorio de cascada.

### 4.2 `encapsular(mensaje, ...)`

- **Objetivo:** ejecutar la cascada de encapsulamiento de la capa 7 a la capa 1 y devolver la trama completa en bytes y en bits.
- **Capa:** L7 → L1.
- **Parámetros:** `mensaje`, `protocolo_app` (por defecto `HTTP/1.1`), `recurso` (`/index.html`), `ip_origen` (`192.168.1.10`), `ip_destino` (`93.184.216.34`), `puerto_origen` (`54321`), `puerto_destino` (`80`), `mac_origen` (`AA:BB:CC:11:22:33`), `mac_destino` (`AA:BB:CC:44:55:66`), `numero_secuencia` (`1001`), `medio` (`Cobre UTP (RJ45)`).
- **Resultado:** un objeto `TramaEncapsulada` con la lista de pasos (`PasoCapa`), la trama en `bytes`, la trama en `bits`, el preámbulo, la carga base64, el token de sesión, el checksum IP y el CRC32.

### 4.3 `desencapsular(trama, medio=...)`

- **Objetivo:** ejecutar la cascada de recepción de la capa 1 a la capa 7, verificando el CRC32 y el checksum IP, retirando cada cabecera y reconstruyendo el mensaje original.
- **Capa:** L1 → L7.
- **Parámetros:** `trama` (bytes) que llega del medio y `medio` (str, informativo).
- **Resultado:** un objeto `RecepcionDecapsulada` con los pasos de recepción, el mensaje recuperado, la carga base64, el token, el CRC32 y el checksum IP con sus banderas de validez. Si el CRC32 no coincide, lanza `FcsMismatchError` y la trama se descarta en la capa 2.

### 4.4 `encode_base64(texto)` y `decode_base64(codificado)`

- **Objetivo:** serializar y reconstruir la carga de la capa 6. `encode_base64` codifica un texto UTF-8 a base64; `decode_base64` revierte la operación.
- **Capa:** L6 (Presentación).
- **Parámetros:** `texto` (str) a codificar; `codificado` (str base64) a decodificar.
- **Resultado:** `encode_base64` devuelve el texto base64; `decode_base64` devuelve el texto UTF-8 original. La operación es reversible y siempre produce una salida cuyo largo es múltiplo de 4.

### 4.5 `calcular_crc32(datos)` y `crc32_hex(datos)`

- **Objetivo:** calcular el CRC32 real (polinomio `0x04C11DB7`) del contenido del marco mediante `zlib.crc32`, y formatearlo en notación hexadecimal de 8 dígitos.
- **Capa:** L2 (Enlace de datos), como FCS.
- **Parámetros:** `datos` (bytes) que representan el marco sin el FCS.
- **Resultado:** un entero de 32 bits o su cadena hexadecimal con prefijo `0x`.

### 4.6 `checksum_ip(cabecera)`

- **Objetivo:** calcular el checksum de Internet IPv4 mediante la suma de complementos de palabras de 16 bits de la cabecera, tal como define el protocolo IP.
- **Capa:** L3 (Red).
- **Parámetros:** `cabecera` (bytes) que representa la cabecera IPv4.
- **Resultado:** una cadena hexadecimal de 4 dígitos con el checksum, por ejemplo `0x7746`. Si la longitud es impar, se rellena con un byte nulo antes de sumar.

### 4.7 `bytes_a_bits(datos)`, `bits_a_bytes(bits)` y `bytes_a_hex(datos)`

- **Objetivo:** convertir la representación de los datos para la capa física y para la visualización. `bytes_a_bits` genera la cadena de bits; `bits_a_bytes` la revierte agrupando de 8 en 8; `bytes_a_hex` produce la vista hexadecimal en mayúsculas separada por espacios.
- **Capa:** L1 (Física) y apoyo a L2.
- **Parámetros:** `datos` (bytes) o `bits` (str).
- **Resultado:** la cadena correspondiente según la función.

### 4.8 `CascadePanel` (interfaz gráfica)

- **Objetivo:** presentar visualmente la transmisión calculada por el motor, con los controles (mensaje, casilla de corrupción, botón `Transmitir ▶`) y dos paneles de salida: el log de pasos y la vista de trama en hexadecimal y en bits.
- **Capa:** representa las siete capas en la interfaz.
- **Parámetros:** el widget padre `parent`.
- **Resultado:** una ventana `Toplevel` titulada `Laboratorio de cascada OSI - transmitir() / base64 / CRC32`. La casilla `Alterar 1 bit en el medio` permite provocar corrupción en la capa 2 y observar el descarte de la trama.

## 5. Lógica de las siete capas en el motor

La función `transmitir()` coordina dos recorridos. Al enviar, `encapsular()` avanza de la capa 7 a la 1 y en cada capa registra un `PasoCapa` con la acción, la entrada, la salida, los campos agregados y la técnica empleada:

- **L7 Aplicación:** produce el mensaje y la petición `HTTP/1.1 GET /index.html`. No añade cabeceras; solo genera los datos de usuario.
- **L6 Presentación:** codifica el mensaje a UTF-8 y lo serializa en base64. La capa 6 convierte la carga en texto ASCII y prepara su representación binaria.
- **L5 Sesión:** abre el canal lógico y asigna un token de sesión `tok_XXXXXXXX` derivado del SHA-256 del mensaje, sin añadir bytes a la carga.
- **L4 Transporte:** agrega la cabecera TCP con los campos `sport`, `dport`, `seq`, `ack`, `flags` y `win`, que aportan acuses y control de flujo.
- **L3 Red:** agrega la cabecera IPv4 con `version`, `ttl`, `proto`, `src`, `dst` y `checksum`, y direcciona el paquete entre subredes.
- **L2 Enlace de datos:** construye el marco Ethernet con las direcciones MAC origen/destino, el EtherType `0x0800` (IPv4), el preámbulo `55 55 55 55 55 55 55 D5` y el FCS (CRC32) al final.
- **L1 Física:** convierte el marco entero (incluyendo preámbulo y FCS) en una cadena de bits y lo transmite por el medio.

Al recibir, `desencapsular()` recorre el camino inverso (L1 a L7). Primero convierte los bits en bytes, luego en la capa 2 calcula el CRC32 y lo compara con el FCS recibido: si no coincide, lanza `FcsMismatchError` y la trama se descarta. Si el CRC32 es correcto, retira la cabecera de enlace, en la capa 3 verifica el checksum IP (un cambio de IP lo invalida), y sigue retirando las cabeceras de transporte y sesión hasta llegar a la capa 6, donde decodifica el base64, y a la capa 7, donde recupera el texto original.

## 6. Manual de usuario

### 6.1 Requisitos

- Python 3.8 o superior instalado.
- Sin dependencias externas: la aplicación solo usa la biblioteca estándar (`tkinter`, `base64`, `hashlib`, `zlib`, `dataclasses`).
- Ejecutar desde la raíz del proyecto: `python3 main.py`.

### 6.2 Pantalla principal

Al abrir la aplicación aparece el menú de misiones (`Simulador de Comunicación OSI`), que ofrece cuatro misiones principales con decisiones de protocolo en cada capa:

1. **Misión 1 — Enviar un archivo grande:** entregar un video de 500 MB a Persona B decidiendo entre TCP y UDP, estableciendo la conexión y respetando el MTU.
2. **Misión 2 — Acceder a un sitio web:** navegar a un servidor web remoto resolviendo DNS, eligiendo protocolo/puerto y configurando la puerta de enlace.
3. **Misión 3 — Hacer una videollamada:** establecer audio/video en vivo decidiendo entre baja latencia y entrega ordenada, y la compresión del códec.
4. **Misión 4 — Enviar un mensaje de texto:** transmitir texto multilingüe eligiendo la codificación de caracteres.

### 6.3 Laboratorio de cascada OSI

Desde la barra de controles de una misión se abre con el botón `🔬 Cascada OSI (base64/CRC32)`. En esta ventana:

1. Escriba un mensaje en el campo de texto (por defecto: `Hola PC-B, mensaje enviado con acentos y emoji`).
2. Si desea observar la detección de corrupción, marque la casilla `Alterar 1 bit en el medio`.
3. Pulse el botón `Transmitir ▶` (o presione Enter en el campo).

El panel superior muestra los 14 pasos: los 7 del emisor y los 7 del receptor, con la acción, lo que entra, lo que sale, los campos agregados/eliminados y la técnica de cada capa. El panel inferior muestra la trama en hexadecimal, la cadena base64 y el flujo de bits, además de un resumen con el CRC32, el checksum IP, el tamaño de la trama y el veredicto de integridad. Cuando la corrupción está activada, la interfaz informa que la trama fue descartada en la capa 2 porque el FCS/CRC32 detectó el cambio.

### 6.4 Otras herramientas

- **Inspector de paquetes:** permite seleccionar una capa y observar los datos asociados a cada una.
- **Diagnóstico y reparación:** la aplicación detecta problemas (por ejemplo, violación de MTU o error de enrutamiento) y ofrece un diálogo de reparación que explica la causa y permite aplicar la corrección.
- **Lienzo de red:** muestra visualmente los equipos y el recorrido de los datos.

## 7. Resultados y evidencias

Los resultados se obtuvieron ejecutando el motor con el mensaje de ejemplo `Hola PC-B, mensaje enviado con acentos y emoji` (46 bytes) mediante `transmitir()`, y se verificaron con las 24 pruebas automáticas de `test_osi_engine.py` y las 6 de `test_simulator.py`, todas en estado `OK`.

### 7.1 Métricas de la transmisión

| Métrica | Valor |
|---------|-------|
| Bytes del mensaje original | 46 |
| Bytes de la carga en base64 | 64 (`+39.1 %`) |
| Bytes de la trama completa | 243 |
| Bits totales transmitidos | 1944 |
| Token de sesión (SHA-256) | `tok_d66160be` |
| Checksum IPv4 | `0x7746` |
| CRC32 (FCS) | `0xA8ADF9C5` |
| Cabecera Ethernet | `AA BB CC 44 55 66` → `AA BB CC 11 22 33` → `08 00` |
| Preámbulo | `55 55 55 55 55 55 55 D5` |
| Integridad (`integridad_ok`) | `True` |

La carga en base64 resultante es `SG9sYSBQQy1CLCBtZW5zYWplIGVudmlhZG8gY29uIGFjZW50b3MgeSBlbW9qaQ==`, que al decodificarse reproduce exactamente el mensaje original. El crecimiento de base64 es del `+39.1 %` para este mensaje; en el caso ideal de bloques de tres bytes el aumento es del 33 % (`4/3`), y la prueba `test_longitud_multiplo_de_cuatro_y_crecimiento_4_3` verifica esta propiedad.

### 7.2 Detección de corrupción

Al activar `Alterar 1 bit en el medio`, la capa 2 recalcula el CRC32 y obtiene un valor distinto al FCS recibido; el motor lanza `FcsMismatchError`, la trama se descarta y la interfaz lo informa claramente. Las pruebas `test_un_bit_corrupto_es_detectado_por_el_crc32` y `test_la_corrupcion_se_reporta_en_la_capa_2` confirman este comportamiento. Asimismo, cambiar la IP de destino sin recalcular el checksum invalida el checksum de la capa 3 (`test_cambiar_la_ip_deja_el_checksum_invalido`).

### 7.3 Verificación automática

- `test_osi_engine.py`: 24 pruebas que cubren la ida y vuelta del mensaje, el orden de las siete capas, la presencia de las cabeceras, el preámbulo y el FCS, los cálculos de checksum y CRC32, la detección de corrupción y las métricas de la trama.
- `test_simulator.py`: 6 pruebas que validan la existencia de las cuatro misiones y el cambio de vista de la aplicación.
- `test_gui.py`: prueba interactiva que recorre el menú, las cuatro misiones y el diálogo de reparación, confirmando que los botones `Aplicar reparación` y `Cancelar` son visibles, tienen altura mínima de 24 píxeles y no se solapan con el contenido.
- `test_full_pipeline.py`: 4 pruebas del pipeline de decisiones de cada misión.

### 7.4 Evidencias gráficas

Las siguientes capturas fueron tomadas de la aplicación en ejecución:

| Evidencia | Descripción |
|-----------|-------------|
| `evidencias/01_menu_de_misiones.png` | Menú principal con las cuatro misiones. |
| `evidencias/02_mision_consola_capa7.png` | Consola de la misión en la capa 7. |
| `evidencias/03_cascada_osi_inicial.png` | Laboratorio de cascada antes de transmitir. |
| `evidencias/04_encapsulamiento_L7_a_L1.png` | Encapsulamiento de la capa 7 a la 1. |
| `evidencias/05_desencapsulamiento_L1_a_L7.png` | Desencapsulamiento de la capa 1 a la 7. |
| `evidencias/06_trama_base64_y_bits.png` | Trama en hexadecimal, base64 y cadena de bits. |
| `evidencias/07_deteccion_de_error_crc32.png` | Detección de corrupción mediante CRC32. |
| `evidencias/08_inspector_de_paquetes.png` | Inspector de paquetes por capa. |
| `evidencias/09_diagnostico_y_reparacion.png` | Diálogo de diagnóstico y reparación. |

## 8. Conclusiones

El desarrollo de este simulador interactivo ha permitido demostrar, con evidencia ejecutable y verificable, cómo funciona realmente el proceso de encapsulamiento y desencapsulamiento de datos a lo largo de las siete capas del modelo OSI. La principal conclusión es que un simulador que construye bytes reales, byte a byte, ofrece un valor pedagógico muy superior al de un diagrama estático. El estudiante puede observar la transformación concreta de un mensaje de texto en una trama de 243 bytes, con su carga base64 de 64 bytes, su cabecera Ethernet con direcciones MAC, su preámbulo, su checksum IP `0x7746` y su CRC32 `0xA8ADF9C5`, y comprobar después que el proceso inverso recupera exactamente el texto original cuando la trama llega intacta.

Se confirmó también la importancia de los mecanismos de control de errores. La capa de enlace de datos, mediante el FCS basado en CRC32, detecta la corrupción de un solo bit en el medio y descarta la trama completa, evitando que datos dañados lleguen a las capas superiores. De manera complementaria, el checksum de la cabecera IPv4 protege los campos de direccionamiento: modificar una dirección IP sin recalcular el checksum invalida el paquete en la capa de red. Ambas demostraciones indican que la confiabilidad no es un mecanismo único, sino el resultado de varias capas trabajando de forma coordinada, y que el descarte temprano en la capa 2 resulta más eficiente que intentar reparar el daño en las capas superiores.

El simulador también permitió cuantificar el coste real de la codificación en base64 en la capa de presentación. Para el mensaje de ejemplo, la carga creció de 46 a 64 bytes, un `+39.1 %`, lo que representa un sobrecosto medible de ancho de banda que debe considerarse al elegir una codificación. En el caso ideal de bloques de tres bytes, el crecimiento es del 33 % (`4/3`), y las pruebas automáticas verifican que la salida siempre tenga una longitud múltiplo de cuatro. Así, una noción teórica se convierte en un dato que el estudiante puede comprobar y discutir en clase.

En cuanto a la usabilidad, el proyecto permite afirmar que un buen simulador didáctico debe unir profundidad técnica y claridad visual. Los datos que el estudiante observa en pantalla no son decorativos: proceden de los mismos objetos `PasoCapa` y de la misma trama `bytes` que manipula el motor, de modo que la interfaz y la lógica nunca se contradicen. La corrección del diálogo de reparación, cuyo botón inferior quedaba oculto por el desplazamiento del contenido, ilustra que la usabilidad es en sí misma una parte del resultado: un simulador cuya teoría es correcta pero cuya interfaz impide ver los propios resultados no cumple su objetivo. Del mismo modo, el valor del CRC32 resulta más comprensible cuando la corrupción se provoca con una casilla y la trama se descarta de forma visible, en lugar de explicarse solo con palabras.

## 9. Bibliografía

- International Organization for Standardization (ISO). *ISO/IEC 7498-1:1994, Information technology — Open Systems Interconnection — Basic Reference Model — Part 1: The basic model*. ISO, 1994.
- Kurose, J. y Ross, K. *Computer Networking: A Top-Down Approach*. 8.ª edición, Pearson, 2021.
- Tanenbaum, A. S. y Wetherall, D. J. *Computer Networks*. 6.ª edición, Pearson, 2022.
- Python Software Foundation. *Python 3 Documentation — `base64`, `zlib`, `hashlib`*. https://docs.python.org/3/
- Forouzan, B. A. *Data Communications and Networking*. 5.ª edición, McGraw-Hill, 2013.
- Cisco Networking Academy. *Introduction to Networking* (curso de Data Communication).

## 10. Declaración de uso de inteligencia artificial

Durante el desarrollo de este proyecto se utilizó una herramienta de asistencia automatizada (un asistente de programación basado en modelo de lenguaje) como apoyo para la redacción del código fuente, la detección y corrección de errores de interfaz gráfica, la optimización de la distribución de los diálogos y la redacción de la documentación. Todo el código fue verificado mediante la suite de pruebas automáticas (`test_osi_engine.py`, `test_simulator.py`, `test_gui.py`, `test_full_pipeline.py`) y su ejecución en el entorno descrito, y todas las evidencias gráficas corresponden a la aplicación ejecutada localmente. La responsabilidad conceptual, la validación de los resultados y la revisión de la exactitud del modelo OSI son del autor del trabajo.
