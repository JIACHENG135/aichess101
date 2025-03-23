from abc import ABC, abstractmethod


def is_legal_by_bound(state, x, y):
    return 0 <= x < len(state) and 0 <= y < len(state[0])


def is_legal_by_state(state, color, x, y):
    target = state[x][y]
    if target == "一一":
        return True
    if target.startswith(color):
        return False
    return True


def raw_moves(cur_state, x, y):
    moves = []
    for i in range(1, 10):
        moves.append((x + i, y))
        moves.append((x - i, y))
        moves.append((x, y + i))
        moves.append((x, y - i))
    return moves


def linear_move_filter(cur_state, x, y, new_x, new_y, *, allow_jump=False):

    src_piece = cur_state[x][y]
    dst_piece = cur_state[new_x][new_y]

    if x != new_x and y != new_y:
        return False

    count = 0
    if x != new_x:
        step = 1 if new_x > x else -1
        for i in range(x + step, new_x, step):
            if cur_state[i][y] != "一一":
                count += 1
    elif y != new_y:
        step = 1 if new_y > y else -1
        for i in range(y + step, new_y, step):
            if cur_state[x][i] != "一一":
                count += 1

    dst_empty = dst_piece == "一一"
    dst_enemy = dst_piece != "一一" and not dst_piece.startswith(src_piece[0])

    if allow_jump:
        return (count == 1 and dst_enemy) or (count == 0 and dst_empty)
    else:
        return count == 0 and (dst_empty or dst_enemy)


car_filter = lambda cur_state, x, y, new_x, new_y: linear_move_filter(
    cur_state, x, y, new_x, new_y, allow_jump=False
)

cannon_filter = lambda cur_state, x, y, new_x, new_y: linear_move_filter(
    cur_state, x, y, new_x, new_y, allow_jump=True
)


def filter_legal_moves(color, customize_filter=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cur_state, x, y = args[-3], args[-2], args[-1]
            moves = func(*args, **kwargs)

            moves = [pos for pos in moves if is_legal_by_bound(cur_state, *pos)]

            moves = [pos for pos in moves if is_legal_by_state(cur_state, color, *pos)]

            if customize_filter is not None:
                moves = [
                    pos for pos in moves if customize_filter(cur_state, x, y, *pos)
                ]

            return set(moves)

        return wrapper

    return decorator


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

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Piece.available_pieces.append(cls)

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

    @staticmethod
    @filter_legal_moves("黑")
    def get_next_legal_move(cur_state, x, y):
        if x <= 4:
            return [(x - 1, y), (x, y + 1), (x, y - 1)]
        return [(x - 1, y)]


class RedMinion(Piece):
    name = "红兵"

    @staticmethod
    @filter_legal_moves("红")
    def get_next_legal_move(cur_state, x, y):
        if x > 4:
            return [(x + 1, y), (x, y + 1), (x, y - 1)]
        return [(x + 1, y)]


class BlackGeneral(Piece):
    name = "黑帅"

    @staticmethod
    def _filter(cur_state, x, y, new_x, new_y):
        if new_x < 7 or new_y < 3 or new_y > 5:
            return False
        return True

    @staticmethod
    @filter_legal_moves("黑", customize_filter=_filter)
    def get_next_legal_move(cur_state, x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


class RedGeneral(Piece):
    name = "红帅"

    @staticmethod
    def _filter(cur_state, x, y, new_x, new_y):
        if new_x > 2 or new_y < 3 or new_y > 5:
            return False
        return True

    @staticmethod
    @filter_legal_moves("红", customize_filter=_filter)
    def get_next_legal_move(cur_state, x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


class Cannon(Piece):
    name = None

    get_next_legal_move = classmethod(lambda cls, cur_state, x, y: [])

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        color = cls.name[0]
        cls.get_next_legal_move = filter_legal_moves(color, cannon_filter)(raw_moves)


class BlackCannon(Cannon):
    name = "黑炮"


class RedCannon(Cannon):
    name = "红炮"


class Car(Piece):
    name = None

    get_next_legal_move = classmethod(lambda cls, cur_state, x, y: [])

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        color = cls.name[0]
        cls.get_next_legal_move = filter_legal_moves(color, car_filter)(raw_moves)


class BlackCar(Car):
    name = "黑车"


class RedCar(Car):
    name = "红车"


def horse_move(cur_state, x, y):
    moves = []
    for dx, dy in [
        (2, 1),
        (2, -1),
        (-2, 1),
        (-2, -1),
        (1, 2),
        (1, -2),
        (-1, 2),
        (-1, -2),
    ]:
        new_x = x + dx
        new_y = y + dy
        if is_legal_by_bound(cur_state, new_x, new_y):
            if cur_state[new_x][new_y] == "一一" or not cur_state[new_x][
                new_y
            ].startswith(cur_state[x][y][0]):
                if (
                    (dx == 2 and cur_state[x + 1][y] == "一一")
                    or (dx == -2 and cur_state[x - 1][y] == "一一")
                    or (dy == 2 and cur_state[x][y + 1] == "一一")
                    or (dy == -2 and cur_state[x][y - 1] == "一一")
                ):
                    moves.append((new_x, new_y))

    return moves


class Horse(Piece):
    name = None

    get_next_legal_move = classmethod(lambda cls, cur_state, x, y: [])

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        color = cls.name[0]
        cls.get_next_legal_move = filter_legal_moves(color)(horse_move)


class BlackHorse(Horse):
    name = "黑马"


class RedHorse(Horse):
    name = "红马"


def elephant_move(cur_state, x, y):
    moves = []
    black_bound = 5
    red_bound = 4
    for dx, dy in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
        new_x = x + dx
        new_y = y + dy
        if is_legal_by_bound(cur_state, new_x, new_y):
            if cur_state[new_x][new_y] == "一一" or not cur_state[new_x][
                new_y
            ].startswith(cur_state[x][y][0]):
                midx = (x + new_x) // 2
                midy = (y + new_y) // 2
                if cur_state[midx][midy] == "一一":
                    if (cur_state[x][y].startswith("黑") and midx >= black_bound) or (
                        cur_state[x][y].startswith("红") and midx <= red_bound
                    ):
                        moves.append((new_x, new_y))
    return moves


class Elephant(Piece):
    name = None

    get_next_legal_move = classmethod(lambda cls, cur_state, x, y: [])

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        color = cls.name[0]
        cls.get_next_legal_move = filter_legal_moves(color)(elephant_move)


class BlackElephant(Elephant):
    name = "黑象"


class RedElephant(Elephant):
    name = "红象"


def gurdian_move(cur_state, x, y):
    moves = []
    for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        new_x = x + dx
        new_y = y + dy
        if is_legal_by_bound(cur_state, new_x, new_y):
            if (
                (
                    cur_state[new_x][new_y] == "一一"
                    or not cur_state[new_x][new_y].startswith(cur_state[x][y][0])
                )
                and new_y >= 3
                and new_y <= 5
            ):
                if (cur_state[x][y].startswith("黑") and new_x >= 7) or (
                    cur_state[x][y].startswith("红") and new_x <= 2
                ):
                    moves.append((new_x, new_y))
    return moves


class Gurdian(Piece):
    name = None

    get_next_legal_move = classmethod(lambda cls, cur_state, x, y: [])

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        color = cls.name[0]
        cls.get_next_legal_move = filter_legal_moves(color)(gurdian_move)


class BlackGurdian(Gurdian):
    name = "黑士"


class RedGurdian(Gurdian):
    name = "红士"
