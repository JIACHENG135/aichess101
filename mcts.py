from __future__ import annotations

from math import sqrt, log
from state import State
import random

from visutalize import Visualize

inf = float("inf")


def _uct(total_visits: int, values: float, visits: int) -> float:
    """
    UCT value for a node.
    未访问节点在外层会以 +inf 对待；这里仅计算已访问节点的 UCT。
    """
    if visits == 0:
        return -inf  # 这里给已访问判定；未访问由调用方特殊处理
    # 平滑 total_visits，避免 log(0)
    return (values / visits) + sqrt(2.0 * log(max(1, total_visits)) / visits)


class MctNode:
    def __init__(self, state: State, parent: MctNode | None = None, move=None):
        self.state = state
        self.parent = parent
        self.move = move  # (from_pos, to_pos)
        self.children: dict[tuple[int, int], MctNode] = {}
        self.visits: int = 0
        self.values: float = 0.0

    def select(self) -> "MctNode":
        """
        从已经展开的子节点中依据 UCT 选择一个 child。
        使用“未访问 = +inf”的策略：优先探索未访问节点。
        """
        assert self.children, "select() 仅在存在子节点时调用"
        total = self.visits if self.visits > 0 else 1

        def score(node: MctNode) -> float:
            if node.visits == 0:
                return inf
            return _uct(total, node.values, node.visits)

        return max(self.children.values(), key=score)

    def expand(self) -> None:
        """
        将当前节点的所有后继状态加入 children（宽展开）。
        如果你想要“渐进展开”，可只加入一个未出现的后继。
        """
        for _state in self.state.get_legal_moves():
            move = self.find_move(self.state, _state)
            if move and move not in self.children:
                self.children[move] = MctNode(_state, self, move)

    def backpropagate(self, value: float) -> None:
        """
        回传：这里假设 simulate() 返回的是“当前节点行动方视角”的收益。
        因为父子轮流行动，所以沿父链翻转符号。
        """
        self.visits += 1
        self.values += value
        if self.parent is not None:
            self.parent.backpropagate(-value)  # 关键：翻转

    @staticmethod
    def find_move(old_state: State, new_state: State) -> tuple[int, int] | None:
        """
        从 old_state 到 new_state 解析出 (from_pos, to_pos)。
        修复点：吃子时目的格原本不是空格，因此只要格子内容发生变化，
        新盘面非空就视为 to_pos，变为空就视为 from_pos。
        """
        from_pos = None
        to_pos = None
        # 中国象棋棋盘 10x9，按你工程的实际维度来
        for x in range(10):
            for y in range(9):
                a = old_state.state[x][y]
                b = new_state.state[x][y]
                if a != b:
                    if b == "一一":  # 有 -> 空：这是出发点
                        from_pos = (x, y)
                    else:
                        # 空 -> 我方子 或 敌子 -> 我方子（吃子）：这是落点
                        to_pos = (x, y)
        return (from_pos, to_pos) if (from_pos and to_pos) else None


class Mct:
    def __init__(self, state: State, rounds: int = 800, playout_len: int = 80):
        """
        rounds: 搜索迭代次数（也可理解为模拟次数级别）
        playout_len: rollout 最大步数上限
        """
        Visualize.render_board_with_state(state.state)
        self.root = MctNode(state)
        self.cur = self.root
        self.rounds = int(rounds)
        self.playout_len = int(playout_len)

    # --------- 辅助：rollout 的轻量偏置 ---------

    @staticmethod
    def _count_pieces(state: State) -> int:
        """粗略估计：统计非空格子的数量。"""
        cnt = 0
        board = state.state
        for x in range(10):
            for y in range(9):
                if board[x][y] != "一一":
                    cnt += 1
        return cnt

    def _prefer_moves(self, current: State, next_states: list[State]) -> list[State]:
        """
        给 rollout 用的简单排序：优先“可能是吃子”的后继。
        近似判断方法：若总子数减少了，视作有吃子。
        """
        cur_cnt = self._count_pieces(current)

        def key_fn(ns: State):
            # True > False，所以吃子排前
            return (self._count_pieces(ns) < cur_cnt)

        # 先打乱，再稳定排序（避免总走同一路）
        random.shuffle(next_states)
        return sorted(next_states, key=key_fn, reverse=True)

    @staticmethod
    def normalize_result(node_state: State, raw_result: float) -> float:
        """
        统一“视角”的适配层：
        - 如果 `State.get_result()` 已经是“当前行动方视角”（当前方胜=+1，负=-1，和=0），
          那就直接 return raw_result。
        - 如果是固定视角（比如永远以“红方”为+1），这里需要按 node_state 的轮次做转换。
          你可以在此处按你的 State 协议补充逻辑（例如依据 node_state.current_player）。
        """
        # TODO: 若你的 State 有 player / side_to_move，可在此做转换。
        return raw_result

    # --------- 核心：simulate / search / move 接口 ---------

    def simulate(self, state: State) -> float:
        """
        轻量 rollout：限制步长，优先尝试“可能吃子”的后继。
        若走到终局：返回 normalize 后的胜负值；
        若在步数上限截断：返回 0（中性）。
        """
        current = state
        seen = {hash(current)}
        steps = 0

        while not current.is_terminal() and steps < self.playout_len:
            moves = list(current.get_legal_moves())
            if not moves:
                break
            moves = self._prefer_moves(current, moves)
            picked = None
            for s in moves:
                h = hash(s)
                if h not in seen:
                    picked = s
                    seen.add(h)
                    break
            if picked is None:
                break
            current = picked
            steps += 1

        if current.is_terminal():
            raw = current.get_result()
            return self.normalize_result(state, raw)
        else:
            # 用子力差距作为启发式评估
            return self.piece_count_diff(current) / 16.0  # 归一化到[-1,1]，16为最大子数

    def search(self) -> None:
        """
        进行 self.rounds 次 MCTS 迭代。
        标准流程：从根选择到叶 -> （必要时）展开 -> rollout -> 回传
        """
        for _ in range(self.rounds):
            node = self.root

            # 1) Selection：一直往下挑 child，直到叶节点（或未访问 child）
            while node.children:
                nxt = node.select()
                if nxt.visits == 0:
                    node = nxt
                    break
                node = nxt

            # 2) Expansion：若到的这个节点已经访问过，再进行一次展开并选择一个未访问子
            if node.visits > 0:
                node.expand()
                # 可能没有子（终局），也可能有子
                unvisited = [c for c in node.children.values() if c.visits == 0]
                if unvisited:
                    node = random.choice(unvisited)

            # 3) Simulation
            value = self.simulate(node.state)

            # 4) Backpropagation（翻转）
            node.backpropagate(value)

    def do_best_move(self) -> State | None:
        """
        从根节点挑选落子。
        推荐用“访问次数最多”的子（robust child），更稳。
        """
        if not self.root.children:
            return None

        # 如果全部子状态无效（取决于你的 State.valid），直接返回 None
        if all(hasattr(child.state, "valid") and (not child.state.valid())
               for child in self.root.children.values()):
            return None

        best_node = max(self.root.children.values(), key=lambda n: n.visits)
        # 可选：若想看平均价值，可打印 n.values / n.visits
        # print("Chosen visits/avg:", best_node.visits,
        #       0 if best_node.visits == 0 else best_node.values / best_node.visits)

        Visualize.render_board_with_state(best_node.state.state)
        # 重新定根（丢弃历史，避免树膨胀）
        self.root = best_node
        self.cur = best_node
        self.cur.parent = None
        return best_node.state

    def do_human_move(self, from_pos, to_pos) -> State:
        """
        人类走子 -> 应用到当前状态 -> 若没有现成子节点则创建一个 -> 重新定根
        """
        next_state = self.cur.state.apply_move(from_pos, to_pos)
        Visualize.render_board_with_state(next_state.state)
        move = (from_pos, to_pos)
        node = self.cur.children.get(move)
        if node is None:
            node = MctNode(next_state, self.cur, move)
            self.cur.children[move] = node
        self.root = node
        self.cur = node
        self.cur.parent = None
        return node.state

    @staticmethod
    def piece_count_diff(state: State) -> int:
        """
        统计当前行动方与对方的子力数量差距。
        假设 state.player == 1 表示红方行动，-1 表示黑方行动。
        """
        my_count = 0
        opp_count = 0
        board = state.state
        for x in range(10):
            for y in range(9):
                piece = board[x][y]
                if piece != "一一":
                    if state.player == 1 and piece.startswith("红"):
                        my_count += 1
                    elif state.player == -1 and piece.startswith("黑"):
                        my_count += 1
                    else:
                        opp_count += 1
        return my_count - opp_count  # >0 当前方优，<0 对方优