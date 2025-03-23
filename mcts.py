from math import sqrt, log
from state import State
import random
from __future__ import annotations

inf = float("inf")


class MctNode:
    def __init__(self, state: State, parent=None):
        self.state = state
        self.parent = parent
        self.children: dict[int, MctNode] = {}
        self.visits = 0
        self.values = 0

    def select(self):
        return max(
            self.children.values(),
            key=lambda node: node.values / node.visits
            + sqrt(2 * log(self.visits) / node.visits if node.visits else inf),
        )

    def expand(self):
        for _state in self.state.get_legal_moves():
            self.children[_state] = MctNode(_state, self)

    def backpropagate(self, value):
        self.visits += 1
        self.values += value
        if self.parent:
            self.parent.backpropagate(value)


class Mct:
    def __init__(self, state: State):
        self.root = MctNode(state)
        self.cur = self.root
        self.rounds = 1000

    def simulate(self, state: State):
        current = state
        seen_states = set()
        seen_states.add(hash(current))
        while not current.is_terminal():
            moves = current.get_legal_moves()
            current = random.choice(moves)
            if hash(current) in seen_states:
                continue
            seen_states.add(hash(current))
        return current.get_result()

    def search(self):
        for _ in range(self.rounds):
            node = self.root
            while node.children:
                node = node.select()
            if node.visits:
                node.expand()
                node = node.select()
            value = self.simulate(node.state)
            node.backpropagate(value)
