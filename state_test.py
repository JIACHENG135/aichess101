import unittest

from state import State


class StateTest(unittest.TestCase):
    def test_state_hash(self):
        state = State([["a", "b"], ["c", "d"]], 1)
        _hash = hash(state)
        self.assertEqual(_hash, hash("a,b,c,d"))


unittest.main()
