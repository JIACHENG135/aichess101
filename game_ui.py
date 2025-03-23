import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QMouseEvent, QPainter, QColor
from PyQt5.QtCore import Qt, QPoint


class ChessBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chinese Chess - Click Test")

        self.board_pixmap = QPixmap("./imgs/board.png")
        self.board_label = QLabel(self)
        self.board_label.setPixmap(self.board_pixmap)
        self.board_label.resize(self.board_pixmap.size())
        self.setFixedSize(self.board_pixmap.size())

        self.origin_x = 0
        self.origin_y = 0
        self.cell_width = 115
        self.cell_height = 114
        self.num_cols = 9
        self.num_rows = 10

        self.last_clicked = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            x, y = event.x(), event.y()
            col = round((x - self.origin_x) / self.cell_width)
            row = round((y - self.origin_y) / self.cell_height)

            if 0 <= col < self.num_cols and 0 <= row < self.num_rows:
                print(f"你点击了第 {row} 行，第 {col} 列")
                self.last_clicked = (col, row)
                self.update()
            else:
                print("点击在棋盘之外")

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.last_clicked:
            painter = QPainter(self)
            painter.setPen(Qt.red)
            painter.setBrush(QColor(255, 0, 0, 120))
            x = self.origin_x + self.last_clicked[0] * self.cell_width
            y = self.origin_y + self.last_clicked[1] * self.cell_height
            radius = 10
            painter.drawEllipse(QPoint(x, y), radius, radius)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessBoard()
    window.show()
    sys.exit(app.exec_())
