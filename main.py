# main.py
import torch
from mcts import Mct
from cnet import ChessNet

from state import State
from utils import state_to_tensor, move_to_index

import random

NUM_GAMES = 50
NUM_EPOCHS = 10
BATCH_SIZE = 32


def self_play(model, device):
    training_data = []
    # 初始局面（你可以替换成初始棋盘）
    init_board = [
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

    state = State(init_board, player=1)
    mcts = Mct(state)
    game_states = []

    for _ in range(100):  # 最多100步
        mcts.search()
        legal_children = list(mcts.root.children.items())
        if not legal_children:
            break

        visits = torch.tensor(
            [child.visits for _, child in legal_children], dtype=torch.float
        )
        probs = visits / visits.sum()

        # 构造完整动作概率向量
        pi_full = torch.zeros(10 * 9 * 10 * 9)
        for i, (move, child) in enumerate(legal_children):
            pi_full[move_to_index(*move)] = probs[i]

        game_states.append(
            (state_to_tensor(mcts.root.state), pi_full, mcts.root.state.player)
        )

        # 随机选择下一步
        next_state = random.choices(
            [child.state for _, child in legal_children], weights=probs.tolist(), k=1
        )[0]

        mcts = Mct(next_state)

        if next_state.is_terminal():
            break

    result = mcts.root.state.get_result()

    training_examples = []
    for state_tensor, pi, player in game_states:
        value = result if player == 1 else -result
        training_examples.append((state_tensor, pi, value))

    return training_examples


def train_model(model, data, device):
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    model.to(device)

    states, policies, values = zip(*data)
    dataset = torch.utils.data.TensorDataset(
        torch.stack(states).to(device),
        torch.stack(policies).to(device),
        torch.tensor(values, dtype=torch.float32).to(device),
    )
    loader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    for epoch in range(NUM_EPOCHS):
        model.train()
        total_loss = 0
        for s, pi, v in loader:
            out_pi, out_v = model(s)
            loss_pi = torch.nn.functional.cross_entropy(out_pi, pi)
            loss_v = torch.nn.functional.mse_loss(out_v.view(-1), v)
            loss = loss_pi + loss_v

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
        print(f"Epoch {epoch+1}/{NUM_EPOCHS}, Loss: {total_loss:.4f}")


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ChessNet()

    all_training_data = []
    for i in range(NUM_GAMES):
        print(f"\n=== Self-Play Game {i+1} ===")
        game_data = self_play(model, device)
        all_training_data.extend(game_data)

        if len(all_training_data) > 5000:
            all_training_data = all_training_data[-5000:]  # 只保留最近的

        train_model(model, all_training_data, device)

        torch.save(model.state_dict(), f"xiangqi_model_round{i+1}.pt")


if __name__ == "__main__":
    main()
