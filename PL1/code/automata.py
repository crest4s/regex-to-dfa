"""Utilities for building and executing finite automata from regular expressions."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple, FrozenSet


@dataclass(frozen=True)
class State:
    """Represents a state inside an automaton."""

    id: int

    def __str__(self) -> str:
        return f"q{self.id}"


@dataclass(frozen=True)
class Transition:
    """Represents a transition between two states."""

    source: State
    symbol: Optional[str]
    target: State


class NFA:
    """Non-deterministic finite automaton."""

    def __init__(self, start_state: State, accept_states: Set[State]):
        self.start_state = start_state
        self.accept_states = accept_states
        self.states: Set[State] = {start_state, *accept_states}
        self.alphabet: Set[str] = set()
        self.transitions: Dict[State, Dict[Optional[str], Set[State]]] = defaultdict(
            lambda: defaultdict(set)
        )

    def add_transition(self, source: State, symbol: Optional[str], target: State) -> None:
        self.states.update({source, target})
        if symbol is not None:
            self.alphabet.add(symbol)
        self.transitions[source][symbol].add(target)

    def epsilon_closure(self, states: Iterable[State]) -> Set[State]:
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for target in self.transitions[state].get(None, set()):
                if target not in closure:
                    closure.add(target)
                    stack.append(target)
        return closure

    def move(self, states: Iterable[State], symbol: str) -> Set[State]:
        result: Set[State] = set()
        for state in states:
            result.update(self.transitions[state].get(symbol, set()))
        return result


class DFA:
    """Deterministic finite automaton."""

    def __init__(
        self,
        states: Set[FrozenSet[State]],
        alphabet: Set[str],
        transitions: Dict[FrozenSet[State], Dict[str, FrozenSet[State]]],
        start_state: FrozenSet[State],
        accept_states: Set[FrozenSet[State]],
    ) -> None:
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def run(self, text: str) -> bool:
        current = self.start_state
        for ch in text:
            targets = self.transitions.get(current, {})
            if ch not in targets:
                return False
            current = targets[ch]
        return current in self.accept_states


# Thompson construction -----------------------------------------------------


class NFAFragment:
    """Utility structure used by Thompson's construction."""

    def __init__(self, start: State, accepts: Set[State]):
        self.start = start
        self.accepts = accepts


class ThompsonConstructor:
    """Converts a regular expression into an NFA using Thompson's algorithm."""

    def __init__(self) -> None:
        self._state_counter = 0
        self.nfa = NFA(self._new_state(), set())

    def _new_state(self) -> State:
        state = State(self._state_counter)
        self._state_counter += 1
        return state

    def literal(self, symbol: str) -> NFAFragment:
        start = self._new_state()
        end = self._new_state()
        self.nfa.add_transition(start, symbol, end)
        return NFAFragment(start, {end})

    def char_class(self, symbols: Set[str]) -> NFAFragment:
        start = self._new_state()
        end = self._new_state()
        for symbol in symbols:
            self.nfa.add_transition(start, symbol, end)
        return NFAFragment(start, {end})

    def concatenate(self, left: NFAFragment, right: NFAFragment) -> NFAFragment:
        for accept in left.accepts:
            self.nfa.add_transition(accept, None, right.start)
        return NFAFragment(left.start, right.accepts)

    def alternate(self, left: NFAFragment, right: NFAFragment) -> NFAFragment:
        start = self._new_state()
        end = self._new_state()
        self.nfa.add_transition(start, None, left.start)
        self.nfa.add_transition(start, None, right.start)
        for accept in left.accepts:
            self.nfa.add_transition(accept, None, end)
        for accept in right.accepts:
            self.nfa.add_transition(accept, None, end)
        return NFAFragment(start, {end})

    def kleene_star(self, fragment: NFAFragment) -> NFAFragment:
        start = self._new_state()
        end = self._new_state()
        self.nfa.add_transition(start, None, fragment.start)
        self.nfa.add_transition(start, None, end)
        for accept in fragment.accepts:
            self.nfa.add_transition(accept, None, fragment.start)
            self.nfa.add_transition(accept, None, end)
        return NFAFragment(start, {end})

    def kleene_plus(self, fragment: NFAFragment) -> NFAFragment:
        start = self._new_state()
        end = self._new_state()
        self.nfa.add_transition(start, None, fragment.start)
        for accept in fragment.accepts:
            self.nfa.add_transition(accept, None, fragment.start)
            self.nfa.add_transition(accept, None, end)
        return NFAFragment(start, {end})

    def optional(self, fragment: NFAFragment) -> NFAFragment:
        start = self._new_state()
        end = self._new_state()
        self.nfa.add_transition(start, None, fragment.start)
        self.nfa.add_transition(start, None, end)
        for accept in fragment.accepts:
            self.nfa.add_transition(accept, None, end)
        return NFAFragment(start, {end})


@dataclass
class Token:
    kind: str
    value: Optional[Set[str]] = None


OPERATORS = {"|", "*", "+", "?", "."}
UNARY_OPERATORS = {"*", "+", "?"}
PRECEDENCE = {"|": 1, ".": 2, "*": 3, "+": 3, "?": 3}


def _escape_sequence(char: str) -> Set[str]:
    if char == "d":
        return set("0123456789")
    if char == "s":
        return set(" \t\r\n")
    if char == "w":
        return set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")
    return {char}


def tokenize(regex: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    while i < len(regex):
        char = regex[i]
        if char == "\\":
            if i + 1 >= len(regex):
                raise ValueError("Invalid escape at end of pattern")
            next_char = regex[i + 1]
            escaped = _escape_sequence(next_char)
            if len(escaped) == 1 and next_char not in {"d", "s", "w"}:
                tokens.append(Token("literal", {next(iter(escaped))}))
            else:
                tokens.append(Token("char_class", escaped))
            i += 2
        elif char in OPERATORS:
            tokens.append(Token("operator", {char}))
            i += 1
        elif char == "(":
            tokens.append(Token("lparen"))
            i += 1
        elif char == ")":
            tokens.append(Token("rparen"))
            i += 1
        elif char == "[":
            end = i + 1
            depth = 1
            while end < len(regex) and depth > 0:
                if regex[end] == "\\":
                    end += 2
                    continue
                if regex[end] == "[":
                    depth += 1
                elif regex[end] == "]":
                    depth -= 1
                end += 1
            if depth != 0:
                raise ValueError("Unterminated character class")
            content = regex[i + 1 : end - 1]
            tokens.append(Token("char_class", _parse_char_class(content)))
            i = end
        else:
            tokens.append(Token("literal", {char}))
            i += 1
    return tokens


def _parse_char_class(content: str) -> Set[str]:
    result: Set[str] = set()
    i = 0
    while i < len(content):
        char = content[i]
        if char == "\\":
            if i + 1 >= len(content):
                raise ValueError("Invalid escape in character class")
            seq = _escape_sequence(content[i + 1])
            result.update(seq)
            i += 2
        elif i + 2 < len(content) and content[i + 1] == "-":
            start = content[i]
            end = content[i + 2]
            for code in range(ord(start), ord(end) + 1):
                result.add(chr(code))
            i += 3
        else:
            result.add(char)
            i += 1
    return result


def insert_concatenation_operators(tokens: List[Token]) -> List[Token]:
    result: List[Token] = []
    for i, token in enumerate(tokens):
        result.append(token)
        if i == len(tokens) - 1:
            continue
        current = token
        nxt = tokens[i + 1]
        if _needs_concatenation(current, nxt):
            result.append(Token("operator", {"."}))
    return result


def _needs_concatenation(current: Token, nxt: Token) -> bool:
    if current.kind in {"literal", "char_class", "rparen"}:
        return nxt.kind in {"literal", "char_class", "lparen"}
    if current.kind == "operator" and current.value == {"*"}:
        return nxt.kind in {"literal", "char_class", "lparen"}
    if current.kind == "operator" and current.value == {"+"}:
        return nxt.kind in {"literal", "char_class", "lparen"}
    if current.kind == "operator" and current.value == {"?"}:
        return nxt.kind in {"literal", "char_class", "lparen"}
    return False


def to_postfix(tokens: List[Token]) -> List[Token]:
    output: List[Token] = []
    stack: List[Token] = []
    for token in tokens:
        if token.kind in {"literal", "char_class"}:
            output.append(token)
        elif token.kind == "operator":
            op = next(iter(token.value))
            while stack and stack[-1].kind == "operator":
                top_op = next(iter(stack[-1].value))
                if (
                    (op not in UNARY_OPERATORS and PRECEDENCE[top_op] >= PRECEDENCE[op])
                    or (op in UNARY_OPERATORS and PRECEDENCE[top_op] > PRECEDENCE[op])
                ):
                    output.append(stack.pop())
                else:
                    break
            stack.append(token)
        elif token.kind == "lparen":
            stack.append(token)
        elif token.kind == "rparen":
            while stack and stack[-1].kind != "lparen":
                output.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses in expression")
            stack.pop()
    while stack:
        top = stack.pop()
        if top.kind in {"lparen", "rparen"}:
            raise ValueError("Mismatched parentheses in expression")
        output.append(top)
    return output


def regex_to_nfa(pattern: str) -> NFA:
    pattern = pattern.strip()
    if pattern.startswith("^"):
        pattern = pattern[1:]
    if pattern.endswith("$"):
        pattern = pattern[:-1]
    tokens = tokenize(pattern)
    tokens = insert_concatenation_operators(tokens)
    postfix = to_postfix(tokens)
    constructor = ThompsonConstructor()
    stack: List[NFAFragment] = []

    for token in postfix:
        if token.kind == "literal":
            symbol = next(iter(token.value or []))
            stack.append(constructor.literal(symbol))
        elif token.kind == "char_class":
            stack.append(constructor.char_class(token.value or set()))
        elif token.kind == "operator":
            operator = next(iter(token.value or []))
            if operator == ".":
                right = stack.pop()
                left = stack.pop()
                stack.append(constructor.concatenate(left, right))
            elif operator == "|":
                right = stack.pop()
                left = stack.pop()
                stack.append(constructor.alternate(left, right))
            elif operator == "*":
                fragment = stack.pop()
                stack.append(constructor.kleene_star(fragment))
            elif operator == "+":
                fragment = stack.pop()
                stack.append(constructor.kleene_plus(fragment))
            elif operator == "?":
                fragment = stack.pop()
                stack.append(constructor.optional(fragment))
            else:
                raise ValueError(f"Unsupported operator: {operator}")
    if len(stack) != 1:
        raise ValueError("Invalid regular expression")
    fragment = stack.pop()
    placeholder = constructor.nfa.start_state
    constructor.nfa.start_state = fragment.start
    constructor.nfa.accept_states = fragment.accepts
    constructor.nfa.states.discard(placeholder)
    constructor.nfa.states.add(fragment.start)
    constructor.nfa.states.update(fragment.accepts)
    return constructor.nfa


# Subset construction -------------------------------------------------------


def nfa_to_dfa(nfa: NFA) -> DFA:
    alphabet = set(nfa.alphabet)
    start_closure = frozenset(nfa.epsilon_closure({nfa.start_state}))
    transitions: Dict[FrozenSet[State], Dict[str, FrozenSet[State]]] = {}
    states: Set[FrozenSet[State]] = {start_closure}
    accept_states: Set[FrozenSet[State]] = set()

    queue: deque[FrozenSet[State]] = deque([start_closure])
    while queue:
        current = queue.popleft()
        transitions.setdefault(current, {})
        if current & nfa.accept_states:
            accept_states.add(current)
        for symbol in alphabet:
            move = nfa.move(current, symbol)
            if not move:
                continue
            closure = frozenset(nfa.epsilon_closure(move))
            transitions[current][symbol] = closure
            if closure not in states:
                states.add(closure)
                queue.append(closure)
    return DFA(states, alphabet, transitions, start_closure, accept_states)


# DFA minimisation ----------------------------------------------------------


def minimize_dfa(dfa: DFA) -> DFA:
    alphabet = set(dfa.alphabet)
    non_accepting = dfa.states - dfa.accept_states
    partitions: List[Set[FrozenSet[State]]] = []
    if dfa.accept_states:
        partitions.append(set(dfa.accept_states))
    if non_accepting:
        partitions.append(set(non_accepting))

    worklist: deque[Set[FrozenSet[State]]] = deque(partitions)

    while worklist:
        current = worklist.popleft()
        for symbol in alphabet:
            pre_states = {
                state
                for state in dfa.states
                if dfa.transitions.get(state, {}).get(symbol) in current
            }
            updated_partitions: List[Set[FrozenSet[State]]] = []
            for partition in partitions:
                intersection = partition & pre_states
                difference = partition - pre_states
                if intersection and difference:
                    updated_partitions.extend([intersection, difference])
                    if partition in worklist:
                        worklist.remove(partition)
                        worklist.append(intersection)
                        worklist.append(difference)
                    else:
                        if len(intersection) <= len(difference):
                            worklist.append(intersection)
                        else:
                            worklist.append(difference)
                else:
                    updated_partitions.append(partition)
            partitions = updated_partitions

    state_map: Dict[FrozenSet[State], FrozenSet[State]] = {}
    for partition in partitions:
        rep = next(iter(partition))
        for state in partition:
            state_map[state] = frozenset(rep)

    new_states = set(state_map.values())
    new_start = state_map[dfa.start_state]
    new_accepts = {state_map[state] for state in dfa.accept_states}
    new_transitions: Dict[FrozenSet[State], Dict[str, FrozenSet[State]]] = defaultdict(dict)

    for state, edges in dfa.transitions.items():
        for symbol, target in edges.items():
            new_transitions[state_map[state]][symbol] = state_map[target]

    return DFA(new_states, alphabet, dict(new_transitions), new_start, new_accepts)


# Transition matrix ---------------------------------------------------------


def generate_transition_matrix(dfa: DFA) -> Tuple[List[List[str]], List[str], List[str]]:
    symbols = sorted(dfa.alphabet)
    state_names = {state: f"S{index}" for index, state in enumerate(sorted(dfa.states, key=lambda s: sorted(st.id for st in s)))}
    matrix: List[List[str]] = []
    for state in sorted(dfa.states, key=lambda s: sorted(st.id for st in s)):
        row: List[str] = []
        for symbol in symbols:
            target = dfa.transitions.get(state, {}).get(symbol)
            row.append(state_names[target] if target else "-")
        matrix.append(row)
    ordered_states = [state_names[state] for state in sorted(dfa.states, key=lambda s: sorted(st.id for st in s))]
    return matrix, ordered_states, symbols


# Utility API ---------------------------------------------------------------


def build_minimized_dfa(pattern: str) -> DFA:
    nfa = regex_to_nfa(pattern)
    dfa = nfa_to_dfa(nfa)
    minimized = minimize_dfa(dfa)
    return minimized


def evaluate_pattern(pattern: str, candidates: Iterable[str]) -> List[Tuple[str, bool]]:
    dfa = build_minimized_dfa(pattern)
    return [(candidate, dfa.run(candidate)) for candidate in candidates]


__all__ = [
    "State",
    "Transition",
    "NFA",
    "DFA",
    "regex_to_nfa",
    "nfa_to_dfa",
    "minimize_dfa",
    "generate_transition_matrix",
    "build_minimized_dfa",
    "evaluate_pattern",
]
