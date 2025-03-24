from abc import ABC, abstractmethod
from pieces_move import (
    car_filter,
    cannon_filter,
    elephant_move,
    gurdian_move,
    filter_legal_moves,
    horse_move,
    raw_moves,
)


class AbstractPiece(ABC):
    @classmethod
    @abstractmethod
    def _is(cls, cur_state, x, y):
        pass

    @staticmethod
    @abstractmethod
    def get_next_legal_move(cur_state, x, y):
        pass


class Piece(AbstractPiece):
    available_pieces = []

    name = None
    move_func = None
    filter_func = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name:
            Piece.available_pieces.append(cls)
        if cls.name and cls.move_func:
            color = cls.name[0]
            cls.get_next_legal_move = filter_legal_moves(color, cls.filter_func)(
                cls.move_func
            )

    @classmethod
    def _is(cls, cur_state, x, y):
        return cur_state[x][y] == cls.name

    @staticmethod
    def get_all_available_pieces():
        return Piece.available_pieces

    @staticmethod
    def get_name_to_cls_mapping():
        return {piece.name: piece for piece in Piece.available_pieces}


class BlackMinion(Piece):
    name = "黑兵"
    move_func = lambda s, x, y: (
        [(x - 1, y)] if x > 4 else [(x - 1, y), (x, y + 1), (x, y - 1)]
    )


class RedMinion(Piece):
    name = "红兵"
    move_func = lambda s, x, y: (
        [(x + 1, y)] if x < 5 else [(x + 1, y), (x, y + 1), (x, y - 1)]
    )


class BlackCar(Piece):
    name = "黑车"
    move_func = raw_moves
    filter_func = car_filter


class RedCar(Piece):
    name = "红车"
    move_func = raw_moves
    filter_func = car_filter


class BlackCannon(Piece):
    name = "黑炮"
    move_func = raw_moves
    filter_func = cannon_filter


class RedCannon(Piece):
    name = "红炮"
    move_func = raw_moves
    filter_func = cannon_filter


class BlackHorse(Piece):
    name = "黑马"
    move_func = horse_move


class RedHorse(Piece):
    name = "红马"
    move_func = horse_move


class BlackElephant(Piece):
    name = "黑象"
    move_func = elephant_move


class RedElephant(Piece):
    name = "红象"
    move_func = elephant_move


class BlackGurdian(Piece):
    name = "黑士"
    move_func = gurdian_move


class RedGurdian(Piece):
    name = "红士"
    move_func = gurdian_move


class BlackGeneral(Piece):
    name = "黑帅"

    @staticmethod
    def _filter(state, x, y, nx, ny):
        return 7 <= nx <= 9 and 3 <= ny <= 5

    @staticmethod
    @filter_legal_moves("黑", customize_filter=_filter)
    def get_next_legal_move(state, x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


class RedGeneral(Piece):
    name = "红帅"

    @staticmethod
    def _filter(state, x, y, nx, ny):
        return 0 <= nx <= 2 and 3 <= ny <= 5

    @staticmethod
    @filter_legal_moves("红", customize_filter=_filter)
    def get_next_legal_move(state, x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
