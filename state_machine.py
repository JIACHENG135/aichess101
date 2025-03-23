from pieces import Piece
from state import State


class StateMachine:
    @staticmethod
    def get_all_legal_mutates(state, player):
        yielded = set()
        for _row in state:
            for _piece in _row:
                if _piece != "一一":
                    piece_cls: Piece = Piece.get_name_to_cls_mapping().get(_piece)
                    if piece_cls and _piece.startswith(player):
                        for x in range(len(state)):
                            for y in range(len(state[0])):
                                if piece_cls._is(state, x, y):
                                    moves = piece_cls.get_next_legal_move(state, x, y)
                                    for move in moves:
                                        if (x, y, move[0], move[1]) not in yielded:
                                            yielded.add((x, y, move[0], move[1]))
                                            yield (x, y), move

    @staticmethod
    def get_a_random_mutate(state, player):
        from random import choice

        player_color = ["红", "黑"][player == 1]
        moves = list(StateMachine.get_all_legal_mutates(state, player_color))
        if moves:
            return choice(moves)
        return None
