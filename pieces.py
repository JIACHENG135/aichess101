from abc import ABC, abstractmethod


def is_legal_by_bound(state, x, y):
    return 0 <= x < len(state) and 0 <= y < len(state[0])


def is_legal_by_state(state, color, x, y):
    target = state[x][y]
    if target == "一一":
        return True
    return not target.startswith(color)


def raw_moves(cur_state, x, y):
    return (
        [(x + i, y) for i in range(1, 10)]
        + [(x - i, y) for i in range(1, 10)]
        + [(x, y + i) for i in range(1, 10)]
        + [(x, y - i) for i in range(1, 10)]
    )


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
    else:
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


def filter_legal_moves(color, customize_filter=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cur_state, x, y = args[-3], args[-2], args[-1]
            moves = func(*args, **kwargs)
            moves = [pos for pos in moves if is_legal_by_bound(cur_state, *pos)]
            moves = [pos for pos in moves if is_legal_by_state(cur_state, color, *pos)]
            if customize_filter:
                moves = [
                    pos for pos in moves if customize_filter(cur_state, x, y, *pos)
                ]
            return set(moves)

        return wrapper

    return decorator


car_filter = lambda s, x, y, nx, ny: linear_move_filter(
    s, x, y, nx, ny, allow_jump=False
)
cannon_filter = lambda s, x, y, nx, ny: linear_move_filter(
    s, x, y, nx, ny, allow_jump=True
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


def horse_move(state, x, y):
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
        nx, ny = x + dx, y + dy
        if is_legal_by_bound(state, nx, ny):
            if not state[nx][ny].startswith(state[x][y][0]) or state[nx][ny] == "一一":
                if (
                    (dx == 2 and state[x + 1][y] == "一一")
                    or (dx == -2 and state[x - 1][y] == "一一")
                    or (dy == 2 and state[x][y + 1] == "一一")
                    or (dy == -2 and state[x][y - 1] == "一一")
                ):
                    moves.append((nx, ny))
    return moves


class BlackHorse(Piece):
    name = "黑马"
    move_func = horse_move


class RedHorse(Piece):
    name = "红马"
    move_func = horse_move


def elephant_move(state, x, y):
    moves = []
    for dx, dy in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
        nx, ny = x + dx, y + dy
        if is_legal_by_bound(state, nx, ny):
            mx, my = (x + nx) // 2, (y + ny) // 2
            if state[mx][my] == "一一":
                if (state[x][y].startswith("黑") and nx >= 5) or (
                    state[x][y].startswith("红") and nx <= 4
                ):
                    moves.append((nx, ny))
    return moves


class BlackElephant(Piece):
    name = "黑象"
    move_func = elephant_move


class RedElephant(Piece):
    name = "红象"
    move_func = elephant_move


def gurdian_move(state, x, y):
    moves = []
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        nx, ny = x + dx, y + dy
        if is_legal_by_bound(state, nx, ny) and 3 <= ny <= 5:
            if (state[x][y].startswith("黑") and nx >= 7) or (
                state[x][y].startswith("红") and nx <= 2
            ):
                moves.append((nx, ny))
    return moves


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
