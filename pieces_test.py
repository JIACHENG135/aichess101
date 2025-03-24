import unittest
from pieces import (
    Piece,
    BlackMinion,
    RedMinion,
    BlackGeneral,
    RedGeneral,
    BlackCannon,
    RedCannon,
    BlackCar,
    RedCar,
    BlackHorse,
    RedHorse,
    BlackElephant,
    RedElephant,
    BlackGurdian,
    cannon_filter,
)
from state import StateMachine


class TestPieces(unittest.TestCase):
    def test_piece_is(self):
        state = [["黑兵"]]
        x, y = 0, 0
        self.assertTrue(BlackMinion._is(state, x, y))

    def test_get_all_pieces(self):
        pieces = Piece.get_all_available_pieces()
        self.assertIn(BlackMinion, pieces)
        self.assertIn(RedMinion, pieces)
        self.assertIn(BlackGeneral, pieces)
        self.assertIn(RedGeneral, pieces)
        self.assertIn(BlackCannon, pieces)
        self.assertIn(RedCannon, pieces)

    def test_get_name_to_cls_mapping(self):
        mapping = Piece.get_name_to_cls_mapping()
        self.assertEqual(mapping["黑兵"], BlackMinion)
        self.assertEqual(mapping["红兵"], RedMinion)

    def test_cannon_filter(self):
        state = [
            ["一一", "一一", "一一"],
            ["一一", "黑炮", "一一"],
            ["一一", "一一", "红车"],
        ]
        self.assertTrue(cannon_filter(state, 1, 1, 2, 1))
        state = [
            ["一一", "一一", "一一", "一一"],
            ["一一", "黑炮", "黑兵", "一一"],
            ["黑炮", "红车", "一一", "红车"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "黑车", "一一", "一一"],
        ]
        actual_moves = BlackCannon.get_next_legal_move(state, 1, 1)
        expect_moves = {(0, 1), (1, 0)}
        self.assertEqual(actual_moves, expect_moves)
        actual_moves = BlackCannon.get_next_legal_move(state, 2, 0)
        expect_moves = {(0, 0), (1, 0), (3, 0), (4, 0), (2, 3)}
        self.assertEqual(actual_moves, expect_moves)

    def test_state_machine(self):
        state = [
            ["一一", "一一", "一一"],
            ["一一", "黑炮", "一一"],
            ["一一", "红车", "一一"],
        ]

        moves = list(move for _, move in StateMachine.get_all_legal_mutates(state))
        self.assertEqual(len(moves), 3)

    def test_car_filter(self):
        state = [
            ["一一", "一一", "一一", "一一"],
            ["黑车", "一一", "红车", "红车"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["黑炮", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
        ]
        actual_moves = BlackCar.get_next_legal_move(state, 1, 0)
        expect_moves = {(0, 0), (1, 1), (1, 2), (2, 0), (3, 0)}
        self.assertEqual(actual_moves, expect_moves)

    def test_horse_move(self):
        state = [
            ["一一", "一一", "一一", "一一"],
            ["红车", "一一", "一一", "一一"],
            ["黑马", "一一", "红车", "红车"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["黑炮", "一一", "一一", "黑车"],
            ["一一", "黑车", "红车", "红车"],
        ]
        actual_moves = BlackHorse.get_next_legal_move(state, 2, 0)
        expect_moves = {(3, 2), (1, 2), (4, 1)}
        self.assertEqual(actual_moves, expect_moves)

    def test_elephant_move(self):
        state = [
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["黑象", "一一", "一一", "一一"],
        ]
        actual_moves = BlackElephant.get_next_legal_move(state, 9, 0)
        expect_moves = {(7, 2)}
        self.assertEqual(actual_moves, expect_moves)
        state = [
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "黑象", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
        ]
        actual_moves = BlackElephant.get_next_legal_move(state, 7, 2)
        expect_moves = {(9, 0), (5, 0)}
        self.assertEqual(actual_moves, expect_moves)

        state = [
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "黑象", "一一"],
            ["一一", "红兵", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
        ]
        actual_moves = BlackElephant.get_next_legal_move(state, 7, 2)
        expect_moves = {(5, 0)}
        self.assertEqual(actual_moves, expect_moves)
        state = [
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "黑象", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["红兵", "一一", "一一", "一一"],
        ]
        actual_moves = BlackElephant.get_next_legal_move(state, 7, 2)
        expect_moves = {(5, 0), (9, 0)}
        self.assertEqual(actual_moves, expect_moves)
        state = [
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "黑象", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["黑车", "一一", "一一", "一一"],
        ]
        actual_moves = BlackElephant.get_next_legal_move(state, 7, 2)
        expect_moves = {(5, 0)}
        self.assertEqual(actual_moves, expect_moves)
        state = [
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["黑象", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一"],
        ]
        actual_moves = BlackElephant.get_next_legal_move(state, 5, 0)
        expect_moves = {(7, 2)}
        self.assertEqual(actual_moves, expect_moves)

    def test_gurdian_move(self):
        # fmt: off
        state = [
            ["红车", "红马", "红象", "红士", "红帅", "红士", "红象", "红马", "红车"],
            ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
            ["一一", "红炮", "一一", "一一", "一一", "一一", "一一", "红炮", "一一"],
            ["红兵", "一一", "红兵", "一一", "红兵", "一一", "红兵", "一一", "红兵"],
            ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
            ["黑兵", "一一", "黑兵", "一一", "黑兵", "一一", "黑兵", "一一", "黑兵"],
            ["一一", "黑炮", "一一", "一一", "一一", "一一", "一一", "黑炮", "一一"],
            ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
            ["黑车", "黑马", "黑象", "黑士", "黑帅", "黑士", "黑象", "黑马", "黑车"],
        ]
        # fmt: on
        actual_moves = BlackGurdian.get_next_legal_move(state, 0, 3)
        expect_moves = {(1, 4)}
        self.assertEqual(actual_moves, expect_moves)
        # fmt: off
        state = [
            ["红车", "红马", "红象", "红士", "红帅", "一一", "红象", "红马", "红车"],
            ["一一", "一一", "一一", "一一", "红士", "一一", "一一", "一一", "一一"],
            ["一一", "红炮", "一一", "一一", "一一", "一一", "一一", "红炮", "一一"],
            ["红兵", "一一", "红兵", "一一", "红兵", "一一", "红兵", "一一", "红兵"],
            ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
            ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
            ["黑兵", "一一", "黑兵", "一一", "黑兵", "一一", "黑兵", "一一", "黑兵"],
            ["一一", "黑炮", "一一", "一一", "一一", "一一", "一一", "黑炮", "一一"],
            ["一一", "一一", "一一", "一一", "黑士", "一一", "一一", "一一", "一一"],
            ["黑车", "黑马", "黑象", "黑士", "黑帅", "一一", "黑象", "黑马", "黑车"],
        ]
        # fmt: on
        actual_moves = BlackGurdian.get_next_legal_move(state, 1, 4)
        expect_moves = {(0, 5), (2, 3), (2, 5)}
        actual_moves = BlackGurdian.get_next_legal_move(state, 8, 4)
        expect_moves = {(7, 3), (7, 5), (9, 5)}
        self.assertEqual(actual_moves, expect_moves)


unittest.main()
