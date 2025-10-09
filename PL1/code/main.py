"""
PL1 – Procesadores del Lenguaje
Versión con matrices de transición usando estados nombrados (q0, q1, q2...).
Cada apartado (A–D) implementa su propio autómata determinista.
"""


# Función genérica para procesar cadenas con un DFA
def procesar_cadena(transiciones, estado_inicial, estados_finales, cadena):
    """Simula un DFA: devuelve True si la cadena es aceptada"""
    estado_actual = estado_inicial

    if not cadena:
        return estado_inicial in estados_finales

    for simbolo in cadena:
        if simbolo not in transiciones.get(estado_actual, {}):
            return False
        estado_actual = transiciones[estado_actual][simbolo]

    return estado_actual in estados_finales


# A) Identificadores [a-zA-Z][a-zA-Z0-9]*
def ejercicio_a():
    letras = [chr(i) for i in range(ord('a'), ord('z') + 1)] + \
              [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    numeros = [str(i) for i in range(10)]

    transiciones = {
        'q0': {c: 'q1' for c in letras},
        'q1': {c: 'q1' for c in letras + numeros}
    }

    estado_inicial = 'q0'
    estados_finales = ['q1']

    cadena = input("[A] Introduce un identificador: ")
    if procesar_cadena(transiciones, estado_inicial, estados_finales, cadena):
        print("Cadena válida")
    else:
        print("Cadena no válida")


# B) Cadenas con número par de 'a' → b*(ab*ab*)*
def ejercicio_b():
    transiciones = {
        'q0': {'a': 'q1', 'b': 'q0'},
        'q1': {'a': 'q0', 'b': 'q1'}
    }

    estado_inicial = 'q0'
    estados_finales = ['q0']

    cadena = input("[B] Introduce una cadena (alfabeto {a,b}): ")
    if procesar_cadena(transiciones, estado_inicial, estados_finales, cadena):
        print("Cadena válida")
    else:
        print("Cadena no válida")


# C) Números en coma flotante [0-9]+(\.[0-9]+)?
def ejercicio_c():
    numeros = [str(i) for i in range(10)]

    transiciones = {
        'q0': {c: 'q2' for c in numeros},
        'q1': {c: 'q3' for c in numeros},
        'q2': {c: 'q2' for c in numeros},
        'q3': {**{c: 'q3' for c in numeros}, '.': 'q0'}
    }

    estado_inicial = 'q1'
    estados_finales = ['q2', 'q3']

    cadena = input("[C] Introduce un número (entero o flotante): ")
    if procesar_cadena(transiciones, estado_inicial, estados_finales, cadena):
        print("Cadena válida")
    else:
        print("Cadena no válida")


# D) Expresiones aritméticas con + o -
# ((l+L)(l+L+d)* + d+(.d+)?)([+-]((l+L)(l+L+d)* + d+(.d+)?))*
def ejercicio_d():
    letras = [chr(i) for i in range(ord('a'), ord('z') + 1)] + \
              [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    numeros = [str(i) for i in range(10)]

    transiciones = {
        'q0': {**{c: 'q2' for c in numeros}, **{c: 'q4' for c in letras}},
        'q1': {**{c: 'q4' for c in letras}, **{c: 'q3' for c in numeros}},
        'q2': {'+': 'q1', '-': 'q1'},
        'q3': {**{c: 'q3' for c in numeros}, '+': 'q1', '-': 'q1', '.': 'q0'},
        'q4': {**{c: 'q4' for c in letras + numeros}, '+': 'q1', '-': 'q1'}
    }

    estado_inicial = 'q1'
    estados_finales = ['q2', 'q3', 'q4']

    cadena = input("[D] Introduce una expresión aritmética: ")
    if procesar_cadena(transiciones, estado_inicial, estados_finales, cadena):
        print("Cadena válida")
    else:
        print("Cadena no válida")


# Menú principal
def main():
    print("=== PROCESADORES DEL LENGUAJE - PL1 ===")
    print("Selecciona el ejercicio (A, B, C o D):")
    opcion = input("Ejercicio: ").strip().upper()

    ejercicios = {
        'A': ejercicio_a,
        'B': ejercicio_b,
        'C': ejercicio_c,
        'D': ejercicio_d
    }

    if opcion in ejercicios:
        ejercicios[opcion]()
    else:
        print("Opción no válida. Usa A, B, C o D.")


# Ejecución
if __name__ == "__main__":
    while True:
        main()
        salir = input("Escribe 'exit' para salir o presiona Enter para continuar: ").strip().lower()
        if salir == 'exit':
            break
        else:
            print("\n"*5)  # Limpiar pantalla simulada