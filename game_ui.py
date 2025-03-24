from __future__ import annotations
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPixmap, QMouseEvent, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer, QEventLoop, pyqtSignal

from state import State, StateMachine
from mcts import Mct


def get_player_move(chessboard: ChessBoard):
    loop = QEventLoop()
    move = {}

    def on_move_made(pos):
        move["action"] = pos
        loop.quit()

    chessboard.move_made.connect(on_move_made)
    loop.exec_()  # This will block until loop.quit() is called

    return move["action"][:2], move["action"][2:]  # from_pos, to_pos


class ChessBoard(QWidget):
    move_made = pyqtSignal(tuple)

    def __init__(self, mct: Mct):
        super().__init__()
        self.setWindowTitle("Chinese Chess - Click Test")
        self.mct = mct
        self.board_pixmap = QPixmap("./imgs/board.png")
        self.setFixedSize(self.board_pixmap.size())  # 设置窗口尺寸为图像大小

        self.origin_x = 0
        self.origin_y = 0
        self.cell_width = 115
        self.cell_height = 114
        self.num_cols = 9
        self.num_rows = 10

        self.last_clicked = None
        self.human_action = []

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            x, y = event.x(), event.y()
            col = round((x - self.origin_x) / self.cell_width)
            row = round((y - self.origin_y) / self.cell_height)

            if 0 <= col < self.num_cols and 0 <= row < self.num_rows:
                print(f"你点击了第 {row} 行，第 {col} 列")
                self.last_clicked = (col, row, x, y)
                self.update()
            else:
                print("点击在棋盘之外")

    def getCurrentStateImage(self):
        return QPixmap("./output_chessboard.png")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.getCurrentStateImage())

        if self.last_clicked:
            col, row, x, y = self.last_clicked
            self.human_action.append([row, col])

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(50, 50, 50, 200))
            radius = 10

            painter.drawEllipse(
                int(x - radius), int(y - radius), radius * 2, radius * 2
            )
        self.check_and_update_human_action()

    def check_and_update_human_action(self):
        if len(self.human_action) == 2:
            from_pos = (self.human_action[-2][0], self.human_action[-2][1])
            to_pos = (self.human_action[-1][0], self.human_action[-1][1])
            print(f"人类选择了动作: {from_pos} -> {to_pos}")
            legal_moves = StateMachine.get_legal_moves_from_pos(
                self.mct.cur.state, from_pos, self.mct.cur.state.player
            )
            if to_pos in legal_moves:
                # 更新棋盘状态
                self.mct.do_human_move(from_pos, to_pos)
                self.human_action = []
                self.last_clicked = None
                painter = QPainter(self)
                painter.drawPixmap(0, 0, self.getCurrentStateImage())
                self.move_made.emit((from_pos[0], from_pos[1], to_pos[0], to_pos[1]))
            else:
                print("非法移动，点击无效")
                self.human_action = []
                self.last_clicked = None


if __name__ == "__main__":

    # 我希望 get_player_move() 能listen到人类的点击动作
    # mct = Mct(initial_state)

    # while not mct.cur.state.is_terminal():
    #     mct.search()

    #     best_node = max(mct.cur.children.values(), key=lambda n: n.visits)

    #     print(f"AI 选择了动作: {best_node.state}")

    #     mct.cur = best_node
    #     mct.root = mct.cur
    #     mct.cur.parent = None

    #     opponent_action = get_player_move()
    #     next_state = best_node.state.apply_move(opponent_action)

    #     for child in mct.cur.children.values():
    #         if child.state == next_state:
    #             mct.cur = child
    #             mct.root = mct.cur
    #             mct.cur.parent = None
    #             break
    #     else:
    #         mct = Mct(next_state)
    state = State(
        [
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
        ],
        1,
    )
    app = QApplication(sys.argv)
    mct = Mct(state)

    window = ChessBoard(mct)
    window.show()

    def game_loop():

        while not mct.cur.state.is_terminal():
            # Human turn
            get_player_move(window)
            window.update()

            # AI turn
            mct.search()
            mct.do_best_move()

            window.update()

    QTimer.singleShot(0, game_loop)  # Start loop after window shows
    sys.exit(app.exec_())
