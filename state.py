from state_machine import StateMachine
from __future__ import annotations


class State:
    def __init__(self, state, player):
        self.state = state
        self.player = player

    def valid(self):
        _general_name = "黑帅" if self.player == 1 else "红帅"
        for row in self.state:
            for piece in row:
                if piece == _general_name:
                    return True
        return False

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
        states = StateMachine.get_all_legal_mutates(self.state, self.player)
        return [State(state=state, player=-self.player) for state in states]

    def is_terminal(self):
        return not self.valid()

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
