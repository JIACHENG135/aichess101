from __future__ import annotations

from math import sqrt, log
from state import State
import random

from visutalize import Visualize

inf = float("inf")


def _calculate(total_visits, values, visits):
    """
    Calculate the UCT value for a node.
    """
    if visits == 0:
        return inf
    return values / visits + sqrt(2 * log(total_visits) / visits)


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
            key=lambda node: _calculate(self.visits, node.values, node.visits),
        )

    def expand(self):
        for _state in self.state.get_legal_moves():
            self.children[_state] = MctNode(_state, self)

    def backpropagate(self, value):
        print("Backpropagating value:", value)
        self.visits += 1
        self.values += value
        if self.parent:
            self.parent.backpropagate(value)


class Mct:
    def __init__(self, state: State):
        Visualize.render_board_with_state(state.state)
        self.root = MctNode(state)
        self.cur = self.root
        self.rounds = 300

    def simulate(self, state: State):
        current = state
        seen_states = set()
        seen_states.add(hash(current))
        rounds = self.rounds
        while not current.is_terminal() and rounds > 0:
            moves = current.get_legal_moves()
            current = random.choice(moves)
            if hash(current) in seen_states:
                continue
            seen_states.add(hash(current))
            rounds -= 1
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

    def do_best_move(self):
        if not self.root.children:
            return None
        if all(not child.state.valid() for child in self.root.children.values()):
            return None
        self.search()
        best_node = max(self.root.children.values(), key=lambda n: n.values / n.visits)
        Visualize.render_board_with_state(best_node.state.state)
        self.root = best_node
        self.cur = best_node
        self.cur.parent = None
        return best_node.state

    def do_human_move(self, from_pos, to_pos):
        next_state = self.cur.state.apply_move(from_pos, to_pos)
        Visualize.render_board_with_state(next_state.state)
        node = self.cur.children.get(hash(next_state), MctNode(next_state, self.root))
        self.root = node
        self.cur = node
        self.cur.parent = None
        return node.state
