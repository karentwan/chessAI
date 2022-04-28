'''
    象棋测试函数
'''
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import resources_rc  # 不导包的话程序无法使用图片资源, 而且不会报错


class Chessman:
    '''
    棋子常量
    '''
    NOCHESS = 0  # 没有棋子
    B_KING = 1  # 黑将
    B_CHR = 2  # 黑车
    B_HORSE = 3  # 黑马
    B_CANNON = 4  # 黑炮
    B_BISHOP = 5  # 黑仕
    B_ELEPHANT = 6  # 黑象
    B_PAWN = 7  # 黑卒
    R_KING = 8  # 红帅
    R_CHR = 9  # 红车
    R_HORSE = 10  # 红马
    R_CANNON = 11  # 红炮
    R_BISHOP = 12  # 红仕
    R_ELEPHANT = 13  # 红相
    R_PAWN = 14  # 红兵


class Constants:
    '''
    一些绘制常量
    '''
    GRID_WIDTH = 70
    OFFSET_WIDTH = 37.5
    OFFSET_HEIGHT = 42.5
    CHESSMAN_WIDTH = 65  # 棋子直径
    SELECT_WIDTH = 68


class ClickState:
    '''
    鼠标点击状态
    '''
    NO_SELECTED = 0
    SELECTED = 1


class GameState:
    '''
    游戏状态
    '''
    PREPARE = 0  # 准备
    RED = 1   # 红方下棋
    BLACK = 2  # 黑方下棋
    RED_WIN = 3  # 红方获胜
    BLACK_WIN = 4  # 黑方获胜
    PEACH = 5  # 平局


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()
        # 棋盘 10 * 9
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

    def init_ui(self):
        self.setFixedSize(640, 720)  # 设置窗口固定值(w, h)

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

    def paintEvent(self, e):
        paint = QPainter()
        paint.begin(self)
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
        paint.end()

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
                self.move(idx_i, idx_j)
                self.click_state = ClickState.NO_SELECTED
                # 落子成功后, 开始转换状态
                if self.game_state == GameState.BLACK:
                    self.game_state = GameState.RED
                elif self.game_state == GameState.RED:
                    self.game_state = GameState.BLACK
        self.repaint()  # 重绘

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
                if idx_i < 7:
                    return False
            else:
                if idx_i > 2:
                    return False
        elif old_c == Chessman.B_CHR or old_c == Chessman.R_CHR:  # 车
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
                if cnt == 0 and c == Chessman.NOCHESS :
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
                if idx_i < 7:
                    return False
            else:  # 红仕
                if idx_i > 2:
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
                if idx_i > old_idx_i:
                    return False
                # 没过界只能往前
                if old_idx_i >= 5:
                    if width != 0:
                        return False
            else:  # 红兵
                if idx_i < old_idx_i:
                    return False
                if old_idx_i <= 4:
                    if width != 0:
                        return False
            return True
        return True

    def move(self, idx_i, idx_j):
        '''
        走棋, 并且在这里面判断棋子的走法是否符合规则
        :param idx_i: 目标棋子的row
        :param idx_j: 目标位置的col
        :return:
        '''
        old_i, old_j = self.old_point
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
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
