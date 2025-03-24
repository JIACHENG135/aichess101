from __future__ import annotations
import copy

from pieces import Piece

from visutalize import Visualize
from collections import defaultdict


class State:
    def __init__(self, state, player):
        self.state = state
        self.player = player

    def draw(self):
        """
        Render the current state of the board using the Visualize class.
        """
        Visualize.render_board_with_state(self.state)

    def valid(self):
        _general_name = "黑帅" if self.player == 1 else "红帅"
        for row in self.state:
            for piece in row:
                if piece == _general_name:
                    return True
        return False

    def __str__(self):
        return (
            "\n".join(["\t".join(row) for row in self.state])
            + f"\nplayer: {self.player}"
        )

    def __iter__(self):
        for row in self.state:
            yield row

    def __hash__(self):
        return hash(",".join([",".join(row) for row in self]) + str(self.player))

    def random_move(self):
        return State(
            state=StateMachine.get_a_random_mutate(self.state, self.player),
            player=-self.player,
        )

    def get_legal_moves(self) -> list[State]:
        player_color = ["红", "黑"][self.player == 1]
        return [
            State(state=state, player=-self.player)
            for state, _ in StateMachine.get_all_legal_mutates(self, player_color)
        ]

    def is_terminal(self):
        res = not self.valid()
        if res:
            print(f"terminated")
        return res

    def get_result(self):
        if not self.valid():
            return -self.player
        return 0

    def apply_move(self, from_pos, to_pos) -> State:
        x_from, y_from = from_pos
        x_to, y_to = to_pos
        new_state = [row[:] for row in self]
        new_state[x_to][y_to] = new_state[x_from][y_from]
        new_state[x_from][y_from] = "一一"

        return State(state=new_state, player=-self.player)


class StateMachine:
    @staticmethod
    def get_all_legal_mutates(state: State, player):
        yielded = set()
        for _row in state:
            for _piece in _row:
                if _piece != "一一":
                    piece_cls: Piece = Piece.get_name_to_cls_mapping().get(_piece)
                    if piece_cls and _piece.startswith(player):
                        for x in range(len(state.state)):
                            for y in range(len(state.state[0])):
                                if piece_cls._is(state.state, x, y):
                                    moves = piece_cls.get_next_legal_move(
                                        state.state, x, y
                                    )
                                    for move in moves:
                                        if (x, y, move[0], move[1]) not in yielded:
                                            yielded.add((x, y, move[0], move[1]))

                                            _new_state = copy.deepcopy(state)
                                            _new_state = _new_state.apply_move(
                                                (x, y), move
                                            )
                                            yield _new_state.state, move

    @staticmethod
    def get_legal_moves_from_pos(state: State, pos, player):
        player_color = ["红", "黑"][player == 1]
        res = set()
        for _state, move in StateMachine.get_all_legal_mutates(state, player_color):
            for x in range(len(state.state)):
                for y in range(len(state.state[0])):
                    if x != pos[0] or y != pos[1]:
                        continue
                    if state.state[x][y] != "一一":
                        res.add(move)
        return res

    @staticmethod
    def get_a_random_mutate(state, player):
        from random import choice

        player_color = ["红", "黑"][player == 1]
        moves = list(
            state
            for state, _ in StateMachine.get_all_legal_mutates(state, player_color)
        )
        if moves:
            return choice(moves)
        return None
