from __future__ import annotations
import copy
from collections import defaultdict
from random import choice

from pieces import Piece
from visutalize import Visualize
import torch


class State:
    def __init__(self, state, player):
        self.state = state
        self.player = player

    def draw(self):
        Visualize.render_board_with_state(self.state)

    def valid(self):
        general = "黑帅" if self.player == 1 else "红帅"
        return any(general in row for row in self.state)

    def __str__(self):
        return (
            "\n".join(["\t".join(row) for row in self.state])
            + f"\nplayer: {self.player}"
        )

    def __iter__(self):
        return iter(self.state)

    def __hash__(self):
        return hash(",".join([",".join(row) for row in self.state]) + str(self.player))

    def random_move(self):
        new_state = StateMachine.get_random_mutation(self, self.player)
        return State(new_state, -self.player) if new_state else self

    def get_legal_moves(self) -> list[State]:
        return [
            State(state=new_board, player=-self.player)
            for new_board, _ in StateMachine.get_all_legal_mutations(self, self.player)
        ]

    def is_terminal(self):
        return not self.valid()

    def get_result(self):
        return -self.player if not self.valid() else 0

    def apply_move(self, src, dst) -> State:
        x1, y1 = src
        x2, y2 = dst
        new_board = [row[:] for row in self.state]
        new_board[x2][y2], new_board[x1][y1] = new_board[x1][y1], "一一"
        return State(new_board, -self.player)


class StateMachine:
    @staticmethod
    def get_all_legal_mutations(state: State | list[list[str]], player: int | str):
        if isinstance(state, list):
            state = State(state, 1 if player == "黑" else -1)
        color = "红" if state.player == -1 else "黑"
        visited = set()

        for x, row in enumerate(state.state):
            for y, name in enumerate(row):
                if name == "一一" or not name.startswith(color):
                    continue
                piece_cls = Piece.get_name_to_cls_mapping().get(name)
                if piece_cls and piece_cls._is(state.state, x, y):
                    for nx, ny in piece_cls.get_next_legal_move(state.state, x, y):
                        key = (x, y, nx, ny)
                        if key in visited:
                            continue
                        visited.add(key)
                        yield state.apply_move((x, y), (nx, ny)).state, (x, y, nx, ny)

    @staticmethod
    def get_legal_moves_from_pos(state: State, pos, player):
        return {
            move[2:]
            for _, move in StateMachine.get_all_legal_mutations(state, player)
            if move[:2] == pos
        }

    @staticmethod
    def get_random_mutation(state: State, player: int):
        mutations = list(StateMachine.get_all_legal_mutations(state, player))
        return choice(mutations)[0] if mutations else None
