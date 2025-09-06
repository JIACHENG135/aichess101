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
    def __init__(self, state: State, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move  # (from_pos, to_pos)
        self.children: dict[tuple[int, int], MctNode] = {}
        self.visits = 0
        self.values = 0

    def select(self):
        return max(
            self.children.values(),
            key=lambda node: _calculate(self.visits, node.values, node.visits),
        )

    def expand(self):
        for _state in self.state.get_legal_moves():
            move = self.find_move(self.state, _state)
            if move:
                self.children[move] = MctNode(_state, self, move)
    def backpropagate(self, value):
        self.visits += 1
        self.values += value
        if self.parent:
            self.parent.backpropagate(-value)  # 关键：翻转

    def find_move(self, old_state: State, new_state: State):
        from_pos = None
        to_pos = None
        for x in range(10):
            for y in range(9):
                a = old_state.state[x][y]
                b = new_state.state[x][y]
                if a != "一一" and b == "一一":
                    from_pos = (x, y)
                if a == "一一" and b != "一一":
                    to_pos = (x, y)
        return (from_pos, to_pos) if from_pos and to_pos else None


class Mct:
    def __init__(self, state: State):
        Visualize.render_board_with_state(state.state)
        self.root = MctNode(state)
        self.cur = self.root
        self.rounds = 800

    def simulate(self, state: State):
        current = state
        seen = {hash(current)}
        steps = 0
        max_len = self.rounds  # 或单独设 playout_len
        while not current.is_terminal() and steps < max_len:
            moves = current.get_legal_moves()  # 若返回的是 state 列表
            random.shuffle(moves)
            picked = None
            for s in moves:
                h = hash(s)
                if h not in seen:
                    picked = s
                    seen.add(h)
                    break
            if picked is None:
                break  # 都见过了，避免自转
            current = picked
            steps += 1
        # 最好从发起方视角要值（见下一条）
        res = current.get_result()
        # print(f"Simulation ended with result by using {steps}:", res)
        return res

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
        best_node = max(
            self.root.children.values(),
            key=lambda n: (0 if n.visits == 0 else n.values / n.visits)
        )
        print(best_node.values)
        Visualize.render_board_with_state(best_node.state.state)
        self.root = best_node
        self.cur = best_node
        self.cur.parent = None
        return best_node.state

    def do_human_move(self, from_pos, to_pos):
        next_state = self.cur.state.apply_move(from_pos, to_pos)
        Visualize.render_board_with_state(next_state.state)
        move = (from_pos, to_pos)
        node = self.cur.children.get(move)
        if node is None:
            node = MctNode(next_state, self.cur, move)
            self.cur.children[move] = node
        self.root = node
        self.cur = node
        self.cur.parent = None  # 重新定根 OK
        return node.state
