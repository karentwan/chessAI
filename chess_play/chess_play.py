'''
    象棋对弈版
'''
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)
import resources_rc  # 不导包的话程序无法使用图片资源, 而且不会报错
import chess_play.core as core
from constants import *


class Opponent(QtCore.QObject):

    play_signal = QtCore.pyqtSignal(int, int, int, int)  # 发送
    process_signal = QtCore.pyqtSignal(list)

    def __init__(self, slot, parent=None) -> None:
        super(Opponent, self).__init__(parent)
        self.AI = core.NegamaxEngine(3)
        self.process_signal.connect(self.play)
        self.play_signal.connect(slot)

    @QtCore.pyqtSlot(list)  # 槽定义在哪里就是哪个线程执行
    def play(self, chess):
        # 下棋
        old_point_i, old_point_j, point_i, point_j = self.AI.search_a_good_move(chess)
        # 发送给主线程
        self.play_signal.emit(old_point_i, old_point_j, point_i, point_j)


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()
        self.chess = None
        self.m, self.n = 10, 9  # 棋盘的行列
        # 棋子资源
        self.res = [
            None,
            QPixmap(':/resources/b_king.png'),
            QPixmap(':/resources/b_chr.png'),
            QPixmap(':/resources/b_horse.png'),
            QPixmap(':/resources/b_cannon.png'),
            QPixmap(':/resources/b_bishop.png'),
            QPixmap(':/resources/b_elephant.png'),
            QPixmap(':/resources/b_pawn.png'),
            QPixmap(':/resources/r_king.png'),
            QPixmap(':/resources/r_chr.png'),
            QPixmap(':/resources/r_horse.png'),
            QPixmap(':/resources/r_cannon.png'),
            QPixmap(':/resources/r_bishop.png'),
            QPixmap(':/resources/r_elephant.png'),
            QPixmap(':/resources/r_pawn.png')
        ]
        self.select_pic = QPixmap(':/resources/select.png')
        self.chess_background = QPixmap(':/resources/chess_board.png')
        self.click_state = 0  # 鼠标点击状态, 一共有三种, 0: 未选中, 1: 选中, 2: 移动
        self.old_point = None  # 要移动的棋子位置
        self.game_state = GameState.RED
        self.whole_pixmap = QPixmap(640, 720)  # 整个棋盘的状态都会绘制到这里, 然后再统一绘制到QWidget上面
        self.win_pixmap = QPixmap(':/resources/win.png')
        self.loss_pixmap = QPixmap(':/resources/loss.png')
        self.mask_pixmap = QPixmap(':/resources/mask.png')
        self.up_red = False  # 红子是否在上方
        if self.up_red:
            # 红子在上的棋盘
            self.chess = [
                [9, 10, 13, 12, 8, 12, 13, 10, 9],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 11, 0, 0, 0, 0, 0, 11, 0],
                [14, 0, 14, 0, 14, 0, 14, 0, 14],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [7, 0, 7, 0, 7, 0, 7, 0, 7],
                [0, 4, 0, 0, 0, 0, 0, 4, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [2, 3, 6, 5, 1, 5, 6, 3, 2]
            ]
            self.game_self = GameState.BLACK  # 自己是红子还是黑子
        else:
            # 红子在下的棋盘
            self.chess = [
                [2, 3, 6, 5, 1, 5, 6, 3, 2],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 4, 0, 0, 0, 0, 0, 4, 0],
                [7, 0, 7, 0, 7, 0, 7, 0, 7],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [14, 0, 14, 0, 14, 0, 14, 0, 14],
                [0, 11, 0, 0, 0, 0, 0, 11, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [9, 10, 13, 12, 8, 12, 13, 10, 9]
            ]
            self.game_self = GameState.RED
        # 定义对方线程, 开始给对方发送数据
        thread = QtCore.QThread(self)
        thread.start()  # thread线程里面有一个事件循环
        self.opponent = Opponent(self.move)
        self.opponent.moveToThread(thread)
        # 连接主线程
        # self.opponent.play_signal.connect(self.move)

    def init_ui(self):
        self.setFixedSize(Constants.CHESS_WIDTH, Constants.CHESS_HEIGHT)  # 设置窗口固定值(w, h)

    def index2px(self, row, col):
        '''
        数组索引转坐标
        :param row: 行, 对应纵坐标y
        :param col: 列, 对应横坐标x
        :return:
        '''
        x = Constants.OFFSET_WIDTH + Constants.GRID_WIDTH * col - Constants.CHESSMAN_WIDTH / 2
        y = Constants.OFFSET_HEIGHT + Constants.GRID_WIDTH * row - Constants.CHESSMAN_WIDTH / 2
        return x, y

    def px2index(self, x, y):
        '''
        坐标转数组索引
        :param x:
        :param y:
        :return:
        '''
        idx_c = int((x - (Constants.OFFSET_WIDTH - Constants.CHESSMAN_WIDTH / 2)) / Constants.GRID_WIDTH)
        idx_r = int((y - (Constants.OFFSET_HEIGHT - Constants.CHESSMAN_WIDTH / 2)) / Constants.GRID_WIDTH)
        return idx_r, idx_c

    def draw_chess(self):
        '''
        绘制棋盘
        :return:
        '''
        paint = QPainter(self.whole_pixmap)
        # 绘制棋盘
        paint.drawPixmap(self.rect(), self.chess_background)
        # 绘制棋子
        for i in range(self.m):
            for j in range(self.n):
                if self.chess[i][j] != Chessman.NOCHESS:
                    x, y = self.index2px(i, j)
                    paint.drawPixmap(QRect(x, y, Constants.CHESSMAN_WIDTH, Constants.CHESSMAN_WIDTH),
                                     self.res[self.chess[i][j]])
        # 画选择框
        if self.click_state == 1:  # 棋子选中状态
            x, y = self.index2px(*self.old_point)
            paint.drawPixmap(QRect(x, y, Constants.SELECT_WIDTH, Constants.SELECT_WIDTH), self.select_pic)

    def draw_end(self):
        '''
        绘制结束状态
        :return:
        '''
        if self.game_state == GameState.RED_WIN or self.game_state == GameState.BLACK_WIN:
            print('棋盘结束')
            flag = (self.game_self == GameState.RED and GameState.RED_WIN == self.game_state) \
                   or (self.game_self == GameState.BLACK and GameState.BLACK_WIN == self.game_state)
            paint = QPainter(self.whole_pixmap)
            paint.drawPixmap(self.rect(), self.mask_pixmap)
            if flag:
                x = (Constants.CHESS_WIDTH - Constants.WIN_WIDTH) // 2
                y = (Constants.CHESS_HEIGHT - Constants.WIN_HEIGHT) // 2
                paint.drawPixmap(QRect(x, y, Constants.WIN_WIDTH, Constants.WIN_HEIGHT), self.win_pixmap)
            else:
                x = (Constants.CHESS_WIDTH - Constants.LOSS_WIDTH) // 2
                y = (Constants.CHESS_HEIGHT - Constants.LOSS_HEIGHT) // 2
                paint.drawPixmap(QRect(x, y, Constants.LOSS_WIDTH, Constants.LOSS_HEIGHT), self.loss_pixmap)

    def paintEvent(self, e):
        paint = QPainter(self)
        # 绘制棋盘
        self.draw_chess()
        self.draw_end()
        # 判断是否需要旋转
        paint.drawPixmap(0, 0, self.whole_pixmap)

    def mousePressEvent(self, e):  # 鼠标点击事件
        # 点击之前判断游戏状态, 只有处于GameState.RED和GameState.BLACK这两个状态才能选择
        if self.game_state == GameState.PREPARE:
            print('游戏未开始...')
            return
        elif self.game_state == GameState.RED_WIN:
            print('红方获胜')
            return
        elif self.game_state == GameState.BLACK_WIN:
            print('黑方获胜')
            return
        # if self.game_state != self.game_self:
        #     print('轮到对方下棋')
        #     return
        # 获取点击坐标
        p = e.pos()
        x, y = p.x(), p.y()
        idx_i, idx_j = self.px2index(x, y)
        if idx_i < 0 or idx_i >= self.m or idx_j < 0 or idx_j >= self.n:
            print('坐标超出选择区域')
            return
        if self.click_state == ClickState.NO_SELECTED:
            if self.chess[idx_i][idx_j] == Chessman.NOCHESS:  # 选中了没有棋子的地方, 表示无效走法
                print('不能选中没有棋子的地方')
                return
            self.old_point = (idx_i, idx_j)
            self.click_state = ClickState.SELECTED
        elif self.old_point[0] == idx_i and self.old_point[1] == idx_j:  # 取消选择
            self.click_state = ClickState.NO_SELECTED
            pass
        elif self.check(idx_i, idx_j):
            old_i, old_j = self.old_point
            self.move(old_i, old_j, idx_i, idx_j)
            self.click_state = ClickState.NO_SELECTED
            self.repaint()
            # 对手下棋
            self.opponent_play()
            self.repaint()
        self.repaint()  # 重绘

    def opponent_play(self):
        # AI下棋
        self.opponent.process_signal.emit(self.chess)

    def check(self, idx_i, idx_j):
        '''
        判断目标位置是否合法
        :param idx_i: 目标位置的row
        :param idx_j: 目标位置的col
        :return:
        '''
        old_idx_i, old_idx_j = self.old_point
        old_c, c = self.chess[old_idx_i][old_idx_j], self.chess[idx_i][idx_j]
        # 1. 如果目标位置是己方棋子则无效
        if self.same(old_c, c):
            print('目标位置是己方棋子, 下棋无效')
            return False
        # 2. 是否是己方落子
        if self.game_state == GameState.RED and 1 <= old_c <= 7:
            print('轮到红方落子')
            return False
        if self.game_state == GameState.BLACK and 8 <= old_c <= 14:
            print('轮到黑方落子')
            return False
        # 3. 判断棋子的走法是否符合规则
        width, height = abs(idx_j - old_idx_j), abs(idx_i - old_idx_i)
        if old_c == Chessman.B_KING or old_c == Chessman.R_KING:  # 帅
            # 是否是一条直线杀对方的将军
            if width == 0 and height > 2:
                for i in range(min(idx_i, old_idx_i)+1, max(idx_i, old_idx_i)):
                    if self.chess[i][old_idx_j] != Chessman.NOCHESS:
                        return False
                return old_c + c == 9  # 目的地是对方将领
            # 只能移动一个位置, 上下左右
            if width + height != 1:
                return False
            # 不能出大帐
            if idx_j < 3 or idx_j > 5:
                return False
            if old_c == Chessman.B_KING:
                if self.up_red:
                    if idx_i < 7:
                        return False
                else:
                    if idx_i > 2:
                        return False
            else:
                if self.up_red:
                    if idx_i > 2:
                        return False
                else:
                    if idx_i < 7:
                        return False
        elif old_c == Chessman.B_CAR or old_c == Chessman.R_CAR:  # 车
            # 车不能拐弯
            if width > 0 and height > 0:
                return False
            # 中间不能有其他棋子
            if width > 0:  # 横着走
                for i in range(min(idx_j, old_idx_j) + 1, max(idx_j, old_idx_j)):
                    if self.chess[idx_i][i] != Chessman.NOCHESS:
                        return False
            else:  # 竖着走
                for i in range(min(idx_i, old_idx_i) + 1, max(idx_i, old_idx_i)):
                    if self.chess[i][old_idx_j] != Chessman.NOCHESS:
                        return False
            return True  # 不能拐弯
        elif old_c == Chessman.B_HORSE or old_c == Chessman.R_HORSE:  # 马
            if width == 2 and height == 1:
                mid = (old_idx_j + idx_j) // 2
                if self.chess[old_idx_i][mid] != Chessman.NOCHESS:
                    return False
            elif width == 1 and height == 2:
                mid = (old_idx_i + idx_i) // 2
                if self.chess[mid][old_idx_j] != Chessman.NOCHESS:
                    return False
            else:
                return False
        elif old_c == Chessman.B_CANNON or old_c == Chessman.R_CANNON:  # 炮
            # 炮也不能拐弯
            if width > 0 and height > 0:
                return False
            # 炮要吃子的话, 必须中间有炮架
            if width > 0:  # 横着走
                cnt = 0  # 计算中间有多少个棋子
                for i in range(min(idx_j, old_idx_j) + 1, max(idx_j, old_idx_j)):
                    if self.chess[idx_i][i] != Chessman.NOCHESS:
                        cnt += 1
                if cnt == 0 and c == Chessman.NOCHESS :
                    return True
                elif cnt == 1 and c != Chessman.NOCHESS and not self.same(old_c, c):
                    return True
                return False
            else:  # 竖着走
                cnt = 0
                for i in range(min(idx_i, old_idx_i) + 1, max(idx_i, old_idx_i)):
                    if self.chess[i][old_idx_j] != Chessman.NOCHESS:
                        cnt += 1
                if cnt == 0 and c == Chessman.NOCHESS:
                    return True
                elif cnt == 1 and c != Chessman.NOCHESS and not self.same(old_c, c):
                    return True
                return False
        elif old_c == Chessman.B_BISHOP or old_c == Chessman.R_BISHOP:  # 仕
            # 只能走斜线
            if not (width == 1 and height == 1):
                return False
            # 跟将军一样只能在九宫格内
            if idx_j < 3 or idx_j > 5:
                return False
            if old_c == Chessman.B_BISHOP:  # 黑仕
                if self.up_red:
                    if idx_i < 7:
                        return False
                else:
                    if idx_i > 2:
                        return False
            else:  # 红仕
                if self.up_red:
                    if idx_i > 2:
                        return False
                else:
                    if idx_i < 7:
                        return False
        elif old_c == Chessman.B_ELEPHANT or old_c == Chessman.R_ELEPHANT:  # 相
            if not (width == 2 and height == 2):
                return False
            mid_i, mid_j = (idx_i + old_idx_i) // 2, (idx_j + old_idx_j) // 2
            if self.chess[mid_i][mid_j] != Chessman.NOCHESS:
                return False
            return True
        elif old_c == Chessman.B_PAWN or old_c == Chessman.R_PAWN:  # 兵
            # 兵只能走一步
            if width + height != 1:
                return False
            if old_c == Chessman.B_PAWN:  # 黑兵
                if self.up_red:
                    if idx_i > old_idx_i:
                        return False
                    # 没过界只能往前
                    if old_idx_i >= 5:
                        if width != 0:
                            return False
                else:
                    if idx_i < old_idx_i:
                        return False
                    if old_idx_i <= 4:
                        if width != 0:
                            return False
            else:  # 红兵
                if self.up_red:
                    if idx_i < old_idx_i:
                        return False
                    if old_idx_i <= 4:
                        if width != 0:
                            return False
                else:
                    if idx_i > old_idx_i:
                        return False
                    # 没过界只能往前
                    if old_idx_i >= 5:
                        if width != 0:
                            return False
            return True
        return True

    @QtCore.pyqtSlot(int, int, int, int)
    def move(self, old_i, old_j, idx_i, idx_j):
        '''
        走棋, 并且在这里面判断棋子的走法是否符合规则
        :param idx_i: 目标棋子的row
        :param idx_j: 目标位置的col
        :return:
        '''
        chess_man = self.chess[old_i][old_j]
        self.chess[old_i][old_j] = 0
        c = self.chess[idx_i][idx_j]
        if c == Chessman.B_KING:
            print('黑将死亡')
            self.game_state = GameState.RED_WIN
        elif c == Chessman.R_KING:
            print('红将死亡')
            self.game_state = GameState.BLACK_WIN
        self.chess[idx_i][idx_j] = chess_man
        # 开始刷新
        print('开始刷新')
        self.repaint()
        # 落子成功后, 开始转换状态
        if self.game_state == GameState.BLACK:
            self.game_state = GameState.RED
        elif self.game_state == GameState.RED:
            self.game_state = GameState.BLACK

    def same(self, chess1, chess2):
        '''
        判断两个棋子是否同色
        :param chess1:
        :param chess2:
        :return:
        '''
        return (1 <= chess1 <= 7 and 1 <= chess2 <= 7) \
               or (8 <= chess1 <= 14 and 8 <= chess2 <= 14)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
