"""Programa principal para construir y ejecutar autómatas derivados de expresiones regulares."""
from __future__ import annotations

from automata import build_minimized_dfa, evaluate_pattern, generate_transition_matrix

PATTERNS = {
    "Identificadores": {
        "regex": r"^[A-Za-z][A-Za-z0-9]*$",
        "tests": [
            "variable",
            "a1",
            "_hidden",
            "1numero",
        ],
    },
    "Cadenas con número par de a": {
        "regex": r"^b*(ab*ab*)*$",
        "tests": [
            "",
            "b",
            "abba",
            "aba",
        ],
    },
    "Números flotantes": {
        "regex": r"^[0-9]+(\.[0-9]+)?$",
        "tests": [
            "3",
            "3.14",
            "0.001",
            "3.",
        ],
    },
    "Expresiones suma/resta": {
        "regex": r"^[A-Za-z_][A-Za-z0-9_]*(\s*[+\-]\s*([A-Za-z_][A-Za-z0-9_]*|[0-9]+(\.[0-9]+)?))*$",
        "tests": [
            "total",
            "x + 3.5",
            "resultado-valor",
            "1 + variable",
        ],
    },
}


def show_transition_matrix(pattern_name: str) -> None:
    pattern = PATTERNS[pattern_name]["regex"]
    dfa = build_minimized_dfa(pattern)
    matrix, states, symbols = generate_transition_matrix(dfa)
    header = "\t".join(["Estado"] + symbols)
    print("\nMatriz de transiciones:")
    print(header)
    for state_name, row in zip(states, matrix):
        print("\t".join([state_name] + row))


def run_tests(pattern_name: str) -> None:
    pattern = PATTERNS[pattern_name]["regex"]
    tests = PATTERNS[pattern_name]["tests"]
    results = evaluate_pattern(pattern, tests)
    print("\nCasos de prueba:")
    for text, accepted in results:
        status = "ACEPTADA" if accepted else "RECHAZADA"
        print(f"  {text!r}: {status}")


def interactive_session(pattern_name: str) -> None:
    pattern = PATTERNS[pattern_name]["regex"]
    dfa = build_minimized_dfa(pattern)
    print("\nIngrese cadenas a evaluar (línea vacía para terminar):")
    while True:
        candidate = input("> ")
        if candidate == "":
            break
        accepted = dfa.run(candidate)
        status = "ACEPTADA" if accepted else "RECHAZADA"
        print(f"  Resultado: {status}")


def main() -> None:
    print("Sistema de evaluación de ER mediante autómatas finitos")
    print("Seleccione una expresión regular de ejemplo:\n")
    names = list(PATTERNS)
    for index, name in enumerate(names, start=1):
        regex = PATTERNS[name]["regex"]
        print(f"  {index}. {name} -> {regex}")
    try:
        choice = int(input("\nOpción: "))
    except ValueError:
        print("Entrada inválida. Saliendo...")
        return
    if choice < 1 or choice > len(names):
        print("Opción fuera de rango. Saliendo...")
        return

    pattern_name = names[choice - 1]
    print(f"\nSeleccionado: {pattern_name}")
    show_transition_matrix(pattern_name)
    run_tests(pattern_name)
    interactive_session(pattern_name)


if __name__ == "__main__":
    main()
