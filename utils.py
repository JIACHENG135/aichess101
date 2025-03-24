# utils.py
import torch
from state import State


def state_to_tensor(state: State) -> torch.Tensor:
    piece_to_idx = {
        "红车": 0,
        "红马": 1,
        "红相": 2,
        "红仕": 3,
        "红帅": 4,
        "红炮": 5,
        "红兵": 6,
        "黑车": 7,
        "黑马": 8,
        "黑象": 9,
        "黑士": 10,
        "黑帅": 11,
        "黑炮": 12,
        "黑卒": 13,
    }
    tensor = torch.zeros(20, 10, 9)
    for i, row in enumerate(state.state):
        for j, piece in enumerate(row):
            if piece in piece_to_idx:
                tensor[piece_to_idx[piece], i, j] = 1
    tensor[14 if state.player == 1 else 15, :, :] = 1  # 当前玩家channel
    return tensor


def move_to_index(from_pos, to_pos):
    return from_pos[0] * 9 * 10 * 9 + from_pos[1] * 10 * 9 + to_pos[0] * 9 + to_pos[1]


def index_to_move(index):
    f_x = index // (9 * 10 * 9)
    f_y = (index % (9 * 10 * 9)) // (10 * 9)
    t_x = (index % (10 * 9)) // 9
    t_y = index % 9
    return (f_x, f_y), (t_x, t_y)
