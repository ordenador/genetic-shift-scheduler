# Genetic Shift Scheduler

## Tabla de Contenido

- [Genetic Shift Scheduler](#genetic-shift-scheduler)
  - [Tabla de Contenido](#tabla-de-contenido)
  - [Descripción General](#descripción-general)
  - [Componentes Principales:](#componentes-principales)
    - [Algoritmo Genético:](#algoritmo-genético)
    - [Interfaz de Usuario:](#interfaz-de-usuario)
  - [Guía Rápida de Uso del Sistema](#guía-rápida-de-uso-del-sistema)
    - [Instalación y Configuración:](#instalación-y-configuración)
    - [Uso del Sistema:](#uso-del-sistema)
  - [Detalles Técnicos](#detalles-técnicos)
    - [Back-end (Python con Flask):](#back-end-python-con-flask)
    - [Front-end (HTML y JavaScript):](#front-end-html-y-javascript)
  - [Diseño y Codificación del Individuo](#diseño-y-codificación-del-individuo)
    - [Estructura del Individuo:](#estructura-del-individuo)
    - [Representación Genética:](#representación-genética)
  - [Evaluación mediante Función de Aptitud (Fitness)](#evaluación-mediante-función-de-aptitud-fitness)
  - [Requerimientos del Software de Gestión de Turnos con Enfoque en Algoritmo Genético](#requerimientos-del-software-de-gestión-de-turnos-con-enfoque-en-algoritmo-genético)
    - [Definición de Turnos:](#definición-de-turnos)
    - [Directrices de Asignación:](#directrices-de-asignación)
    - [3. Evaluación y Métricas:](#3-evaluación-y-métricas)
    - [4. Equidad y Optimización:](#4-equidad-y-optimización)
  - [Contribuciones](#contribuciones)


---

## Descripción General

El **Genetic Shift Scheduler** es una herramienta innovadora que emplea algoritmos genéticos para generar horarios de trabajo óptimos para un año completo, distribuyendo de manera equitativa los turnos entre los empleados y respetando las restricciones de asignación de turnos.

## Componentes Principales:

### Algoritmo Genético:
- **Cromosoma**: Representa una asignación de turnos para todo el año.
- **Función de aptitud**: Evalúa qué tan equitativa es una solución.
- **Operadores**: Cruzamiento, mutación y selección.
- **Ejecución y Evaluación**: Ejecuta el algoritmo y evalúa los resultados.

### Interfaz de Usuario:
   Se utiliza Flask y HTML para construir una interfaz web que permite:
   - Ingresar los nombres de los trabajadores.
   - Solicitar una nueva optimización de turnos.
   - Visualizar las asignaciones.
   - Guardar y cargar programaciones previas.

---

## Guía Rápida de Uso del Sistema

### Instalación y Configuración:

1. **Configura el Entorno Virtual:** Ejecuta el comando `make dev`. Este paso instalará los requerimientos necesarios y creará un entorno virtual (virtualenv) para el sistema.

2. **Ejecuta el Servidor:** Una vez que se haya configurado el entorno, inicia el servidor Flask con el comando `make run`. Luego de ejecutarlo, el servicio estará disponible en el puerto `5000`.

### Uso del Sistema:

3. **Acceso a la Interfaz:** Abre un navegador y visita `http://localhost:5000` para acceder a la interfaz web del sistema.

4. **Registro de Trabajadores:** Ingresa los nombres de los trabajadores que deseas programar.

5. **Generación de Programación:** Haz clic en el botón "Crear Calendario". El sistema generará automáticamente una programación basada en los nombres que proporcionaste.

6. **Visualización:** Observa los turnos en el calendario y las métricas que indican cómo se distribuyeron los turnos entre los trabajadores.

7. **Guardado y Carga (Opcional):** Si lo deseas, puedes guardar la programación generada para consultarla en otro momento o cargar una programación que hayas guardado previamente.

---

## Detalles Técnicos

### Back-end (Python con Flask):

- Se usa la biblioteca `deap` para implementar el algoritmo genético.
- Se definen varias funciones auxiliares para respetar los requerimientos del turno. Por ejemplo: `is_valid`, `backtrack`, `init_individual`, `evaluate`, y `mutate_individual`.
- Se implementa una API web con Flask con endpoints para optimizar la programación (`/optimize`), guardar (`/save_schedule`), cargar (`/load_file_schedule`) y listar archivos de programaciones (`/list_schedules`).

### Front-end (HTML y JavaScript):

- Se utiliza Bootstrap para el diseño y estilización.
- Se proporciona una interfaz para ingresar nombres de trabajadores.
- Los turnos se visualizan en un calendario usando `FullCalendar`.
- Se permiten acciones para crear, guardar y cargar programaciones de turnos.

---

## Diseño y Codificación del Individuo

### Estructura del Individuo:

El individuo es una representación de un horario anual. Dado un conjunto de `T` turnos (por ejemplo, mañana, tarde, noche) y `E` empleados, un individuo visualmente se organiza de la siguiente forma:

| Semana 1 | Semana 2 | ... | Semana 52 |
|:--------:|:--------:|:---:|:---------:|
|    A    |    B    | ... |     C     |
|    B    |    C    | ... |     D     |
|    C    |    D    | ... |     A     |

En esta estructura:
- **Cada fila** representa un turno. Por ejemplo, la primera fila podría representar el turno de la mañana, la segunda fila el turno de la tarde, y así sucesivamente.
- **Cada celda** dentro de una fila señala el empleado asignado para ese turno específico durante esa semana particular. 

### Representación Genética:

La representación genética de un individuo se realiza mediante un cromosoma. En este cromosoma:
- Cada gen es un número entero que varía entre 1 y `E`, representando la identificación de un empleado.
- La posición de cada gen en el cromosoma determina a qué turno y semana se refiere. Por ejemplo, el primer gen podría referirse al turno de la mañana de la semana 1, el segundo al turno de la tarde de la semana 1, y así sucesivamente.

## Evaluación mediante Función de Aptitud (Fitness)

Para evaluar qué tan bueno es un horario propuesto (o individuo), usamos una función de aptitud definida como:

![f(i) equation](https://latex.codecogs.com/gif.latex?f(i)&space;=&space;w_1&space;\times&space;D_{anual}(i)&space;&plus;&space;w_2&space;\times&space;D_{mensual}(i))

Dónde:
- ![f(i)](https://latex.codecogs.com/gif.latex?f(i)): Representa la aptitud o calidad del horario del individuo \( i \).
- ![D_anual(i)](https://latex.codecogs.com/gif.latex?D_{anual}(i)): Mide la variabilidad o desigualdad en la distribución de turnos durante todo el año para el individuo \( i \).
- ![D_mensual(i)](https://latex.codecogs.com/gif.latex?D_{mensual}(i)): Evalúa la desviación o inconsistencia en la asignación de turnos para el individuo \( i \) en un mes específico.
- ![w_1 and w_2](https://latex.codecogs.com/gif.latex?w_1&space;and&space;w_2): Son pesos o coeficientes que determinan la importancia relativa entre la distribución de turnos anual y mensual. Por ejemplo, si se desea que la equidad en la distribución anual sea más importante que la mensual, \( w_1 \) sería mayor que \( w_2 \).

Esta función asegura que el horario no solo sea equitativo a lo largo del año, sino también mes a mes. Es esencial para garantizar que ningún empleado sea desfavorecido en la asignación de turnos.


---
## Requerimientos del Software de Gestión de Turnos con Enfoque en Algoritmo Genético

### Definición de Turnos:

**a. Turno Fin de Semana:** 
  - **Intervalo:** Desde el Viernes a las 16:01 hasta el Lunes a las 8:59.
  - **Restricción:** El mismo empleado debe estar a cargo durante toda la duración del turno, desde el inicio el Viernes hasta el final el Lunes.

**b. Turno Día:** 
  - **Intervalo:** 
    - Lunes a Jueves: 9:01 a 17:59.
    - Viernes: 9:01 a 15:59.
  - **Restricción:** Un solo empleado debe ser responsable durante toda la semana laboral, es decir, de Lunes a Viernes.

**c. Turno Nocturno:** 
  - **Intervalo:** Lunes a Jueves: 18:01 a 8:59 del día siguiente.
  - **Restricciones:** 
    - El mismo empleado cubre de Viernes a Domingo.
    - No debe ser el empleado asignado al Turno Día de la misma semana.
    - Se lleva a cabo simultáneamente con el Turno Día.

### Directrices de Asignación:

**a. Para el Empleado en Turno Día:**
  - No debe ser asignado a los turnos Nocturno ni Fin de Semana en esa misma semana.
  - Debe ser colocado en el Turno Nocturno en la semana subsiguiente.

**b. Para el Empleado en Turno Nocturno:** 
  - No debe ser asignado a los turnos Día ni Fin de Semana durante esa semana.
  - Se le garantizará un periodo de descanso la semana siguiente, sin asignaciones.

**c. Para el Empleado en Turno Fin de Semana:** 
  - No debe ser asignado a los turnos Día ni Nocturno durante la misma semana.

### 3. Evaluación y Métricas:

**a. Informes Generales:** 
  - El software debe facilitar métricas tanto mensuales como anuales, con el objetivo de evaluar la equidad en la distribución de turnos entre todos los empleados.

**b. Distribución de Turnos:** 
  - Es esencial visualizar la frecuencia con la que se asigna cada tipo de turno a cada empleado y comparar esa distribución con un reparto teóricamente equitativo.

### 4. Equidad y Optimización:

- El núcleo del software, el algoritmo genético, debe estar orientado a hallar una solución que promueva la equidad en la distribución de turnos. Esto asegura que, en el transcurso del tiempo, todos los empleados reciban una cantidad semejante de cada tipo de turno.

---

## Contribuciones

Todas las contribuciones son bienvenidas. Revisa [CONTRIBUTING.md](./CONTRIBUTING.md) para más detalles sobre cómo colaborar con este proyecto.
