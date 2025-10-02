# Evaluador de expresiones regulares mediante autómatas finitos

Este proyecto implementa un flujo completo para transformar expresiones regulares en autómatas finitos deterministas minimizados y evaluar cadenas de entrada. Es una práctica pensada para la asignatura **Procesadores del Lenguaje**.

## Características principales

- Construcción de AFND a partir de una expresión regular (construcción de Thompson).
- Conversión de AFND a AFD (algoritmo de subconjuntos).
- Minimización del AFD resultante (Hopcroft).
- Visualización del AFD como matriz de transiciones.
- Ejecución de cadenas de prueba sobre el autómata minimizado.

## Ejecución

```bash
python main.py
```

El programa muestra un menú con las expresiones regulares de ejemplo. Tras seleccionar una opción se imprimen:

1. La matriz de transiciones del AFD minimizado.
2. Resultados de los casos de prueba incluidos para cada patrón.
3. Un modo interactivo para evaluar cadenas introducidas por teclado (deje la entrada vacía para terminar).

## Expresiones regulares de ejemplo

| Nombre | Expresión regular |
| --- | --- |
| Identificadores | `^[A-Za-z][A-Za-z0-9]*$` |
| Cadenas sobre `{a,b}` con número par de `a` | `^b*(ab*ab*)*$` |
| Números flotantes | `^[0-9]+(\.[0-9]+)?$` |
| Expresiones de suma/resta | `^[A-Za-z_][A-Za-z0-9_]*(\s*[+\-]\s*([A-Za-z_][A-Za-z0-9_]*|[0-9]+(\.[0-9]+)?))*$` |

## Ejemplo de salida

```
Sistema de evaluación de ER mediante autómatas finitos
Seleccione una expresión regular de ejemplo:

  2. Cadenas con número par de a -> ^b*(ab*ab*)*$

Opción: 2

Seleccionado: Cadenas con número par de a

Matriz de transiciones:
Estado  a   b
S0      S1  S0
S1      S0  S1

Casos de prueba:
  '': ACEPTADA
  'b': ACEPTADA
  'abba': ACEPTADA
  'aba': ACEPTADA

Ingrese cadenas a evaluar (línea vacía para terminar):
> abba
  Resultado: ACEPTADA
> aba
  Resultado: ACEPTADA
>
```

## Módulo `automata`

El módulo `automata.py` expone funciones y clases reutilizables:

- `regex_to_nfa(pattern)`
- `nfa_to_dfa(nfa)`
- `minimize_dfa(dfa)`
- `generate_transition_matrix(dfa)`
- `build_minimized_dfa(pattern)`
- `evaluate_pattern(pattern, candidates)`

Las clases `State`, `Transition`, `NFA` y `DFA` encapsulan el comportamiento de cada estructura.

## Requisitos

- Python 3.9 o superior.
- No requiere dependencias externas.

