import torch.nn as nn
import torch.nn.functional as F


class ChessNet(nn.Module):
    def __init__(
        self, board_height=10, board_width=9, num_actions=10 * 9 * 10 * 9
    ):  # from_pos * to_pos
        super().__init__()
        self.conv1 = nn.Conv2d(20, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, padding=1)

        self.policy_head = nn.Sequential(
            nn.Conv2d(64, 2, kernel_size=1),
            nn.Flatten(),
            nn.Linear(2 * board_height * board_width, num_actions),
        )

        self.value_head = nn.Sequential(
            nn.Conv2d(64, 1, kernel_size=1),
            nn.Flatten(),
            nn.Linear(board_height * board_width, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Tanh(),
        )

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        policy_logits = self.policy_head(x)
        value = self.value_head(x)
        return policy_logits, value
