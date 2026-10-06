# regex-to-dfa

From regular expressions to minimal deterministic finite automata. For each of four regular expressions, the NFA, the equivalent DFA and the minimised DFA were built in [JFLAP](https://www.jflap.org/), and the minimal DFA is then simulated in Python with a transition table to accept or reject input strings.

Lab project (PL1) for the *Procesadores del Lenguaje* (Language Processors) course at the University of Alcalá (UAH), 2025–26 academic year.

## Regular expressions

| Part | Language | Regular expression |
|------|----------|--------------------|
| A | Identifiers | `[a-zA-Z][a-zA-Z0-9]*` |
| B | Strings over {a, b} with an even number of `a` | `b*(ab*ab*)*` |
| C | Integer or floating-point numbers | `[0-9]+(\.[0-9]+)?` |
| D | Addition/subtraction expressions of identifiers and numbers | `((l+L)(l+L+d)* + d+(.d+)?)([+-]((l+L)(l+L+d)* + d+(.d+)?))*` (l = lowercase letter, L = uppercase letter, d = digit) |

## Structure

```
PL1/
├── Versión corta/
│   ├── Apartado A/   # NFA.jff, DFA.jff, MINIMIZED DFA.jff
│   ├── Apartado B/
│   ├── Apartado C/
│   └── Apartado D/   # automata for the operand and operator schemes and the full expression
└── code/
    └── main.py       # DFA simulator with named states (q0, q1, ...) for parts A–D
```

## Usage

The `.jff` files open in JFLAP (not included; download it from <https://www.jflap.org/>).

The simulator needs only Python 3:

```bash
python3 PL1/code/main.py
```

Choose a part (`A`, `B`, `C` or `D`), type a string and the program prints whether the minimal DFA accepts it (`Cadena válida`) or not (`Cadena no válida`). Type `exit` to quit.

## License

[MIT](LICENSE)
