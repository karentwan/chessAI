'''
    象棋人工智能 - 李大智

象棋人工智能分以下三个组成部分：
    一：极大极小搜索
        算法是固定的, 变动不大
    二：走法产生器
    三：估值棋盘的分数
        棋盘的整体估值又由以下部分组成
        1) 棋子价值估值
        side_value = sum(piece_number \times piece_value)
        其中, piece_number表示棋子的数量, piece_value表示棋子的分值
        例如一个车的piece_value价值500, 马300, 兵100
        2) 棋子的灵活性与棋盘控制估值
        mobility = sum(move_number \times move_value)
        其中, move_number是棋子的合法走法数量, move_value是棋子每一走法的价值
        3) 棋子关系的评估

'''
from typing import *
from chess_play.constants import *
import copy


class ChessmanPosition:

    def __init__(self) -> None:
        self.x = 0
        self.y = 0


class ChessmanMove:

    def __init__(self) -> None:
        self.chess_id = None  # 棋子
        self.fron = ChessmanPosition()
        self.to = ChessmanPosition()
        self.score = 0


class MoveGenerator:
    '''
    走法产生器
    '''

    def __init__(self) -> None:
        super().__init__()
        # 8 \times 80, 用来存放ChessmanMove队列
        self.move_list = [[ChessmanMove()] * 80 for _ in range(8)]
        self.move_cnt = 0  # 记录move_list中走法的数量
        self.up_red = False

    def same(self, chess1, chess2):
        '''
        判断两个棋子是否同色
        :param chess1:
        :param chess2:
        :return:
        '''
        return (1 <= chess1 <= 7 and 1 <= chess2 <= 7) \
               or (8 <= chess1 <= 14 and 8 <= chess2 <= 14)

    def is_valid_move(self, chess, old_idx_j, old_idx_i, idx_j, idx_i):
        '''
        判断目标位置是否合法
        :param idx_i: 目标位置的row
        :param idx_j: 目标位置的col
        :return:
        '''
        old_c, c = chess[old_idx_i][old_idx_j], chess[idx_i][idx_j]
        # 1. 如果目标位置是己方棋子则无效
        if self.same(old_c, c):
            # print('目标位置是己方棋子, 下棋无效')
            return False
        # 3. 判断棋子的走法是否符合规则
        width, height = abs(idx_j - old_idx_j), abs(idx_i - old_idx_i)
        if old_c == Chessman.B_KING or old_c == Chessman.R_KING:  # 帅
            # 是否是一条直线杀对方的将军
            if width == 0 and height > 2:
                for i in range(min(idx_i, old_idx_i) + 1, max(idx_i, old_idx_i)):
                    if chess[i][old_idx_j] != Chessman.NOCHESS:
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
                    if chess[idx_i][i] != Chessman.NOCHESS:
                        return False
            else:  # 竖着走
                for i in range(min(idx_i, old_idx_i) + 1, max(idx_i, old_idx_i)):
                    if chess[i][old_idx_j] != Chessman.NOCHESS:
                        return False
            return True  # 不能拐弯
        elif old_c == Chessman.B_HORSE or old_c == Chessman.R_HORSE:  # 马
            if width == 2 and height == 1:
                mid = (old_idx_j + idx_j) // 2
                if chess[old_idx_i][mid] != Chessman.NOCHESS:
                    return False
            elif width == 1 and height == 2:
                mid = (old_idx_i + idx_i) // 2
                if chess[mid][old_idx_j] != Chessman.NOCHESS:
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
                    if chess[idx_i][i] != Chessman.NOCHESS:
                        cnt += 1
                if cnt == 0 and c == Chessman.NOCHESS:
                    return True
                elif cnt == 1 and c != Chessman.NOCHESS and not self.same(old_c, c):
                    return True
                return False
            else:  # 竖着走
                cnt = 0
                for i in range(min(idx_i, old_idx_i) + 1, max(idx_i, old_idx_i)):
                    if chess[i][old_idx_j] != Chessman.NOCHESS:
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
            if chess[mid_i][mid_j] != Chessman.NOCHESS:
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

    def add_move(self, from_x: int, from_y: int, to_x: int, to_y: int, play: int) -> int:
        '''
        将走法添加进move_list当中
        :param from_x: 起始位置横坐标
        :param from_y: 其实位置纵坐标
        :param to_x: 目标位置横坐标
        :param to_y: 目标位置纵坐标
        :param play: 此走法所在的层次
        :return:
        '''
        self.move_list[play][self.move_cnt].fron.x = from_x
        self.move_list[play][self.move_cnt].fron.y = from_y
        self.move_list[play][self.move_cnt].to.x = to_x
        self.move_list[play][self.move_cnt].to.y = to_y
        self.move_cnt += 1  # 计数器
        return self.move_cnt

    def is_red(self, id):
        return 8 <= id <= 14

    def is_black(self, id):
        return 1 <= id <= 7

    def create_possible_move(self, chess: List[List[int]], ply: int, side: int) -> int:
        '''
        走法产生器, 产生一层的所有可能的走法
        :param chess: 棋盘
        :param ply: 搜索的层数
        :param side: 是否是红子
        :return:
        '''
        self.move_cnt = 0
        # 枚举每一个棋子, 然后分别生成它们可走的路
        for i in range(10):
            for j in range(9):
                if chess[i][j] != Chessman.NOCHESS:
                    id = chess[i][j]
                    if not side and self.is_red(id):
                        continue  # 如果要产生黑棋走法, 跳过红棋
                    if side and self.is_black(id):
                        continue  # 如果要产生红旗走法, 黑棋跳过
                    if id == Chessman.R_KING or id == Chessman.B_KING:
                        self.gen_king_move(chess, i, j, ply)
                    elif id == Chessman.R_BISHOP:
                        self.gen_rbishop_move(chess, i, j, ply)
                    elif id == Chessman.B_BISHOP:
                        self.gen_bbishop_move(chess, i, j, ply)
                    elif id == Chessman.R_ELEPHANT or id == Chessman.B_ELEPHANT:
                        self.gen_elephant_move(chess, i, j, ply)
                    elif id == Chessman.R_HORSE or id == Chessman.B_HORSE:
                        self.gen_horse_move(chess, i, j, ply)
                    elif id == Chessman.R_CAR or id == Chessman.B_CAR:
                        self.gen_car_move(chess, i, j, ply)
                    elif id == Chessman.R_PAWN:
                        self.gen_rpawn_move(chess, i, j, ply)
                    elif id == Chessman.B_PAWN:
                        self.gen_bpawn_move(chess, i, j, ply)
                    elif id == Chessman.B_CANNON or id == Chessman.R_CANNON:
                        self.gen_cannon_move(chess, i, j, ply)
        return self.move_cnt

    def gen_king_move(self, chess: List[List[int]], i: int, j: int, ply: int):
        '''
        产生国王的走法
        :param chess:
        :param i:
        :param j:
        :param ply:
        :return:
        '''
        for y in range(3):
            for x in range(3, 6):
                if self.is_valid_move(chess, j, i, x, y):
                    self.add_move(j, i, x, y, ply)
        for y in range(7, 10):
            for x in range(3, 6):
                if self.is_valid_move(chess, j, i, x, y):
                    self.add_move(j, i, x, y, ply)

    def gen_rbishop_move(self, chess: List[List[int]], i: int, j: int, ply: int):
        for y in range(7, 10):
            for x in range(3, 6):
                if self.is_valid_move(chess, j, i, x, y):
                    self.add_move(j, i, x, y, ply)

    def gen_bbishop_move(self, chess: List[List[int]], i: int, j: int, ply: int):
        for y in range(3):
            for x in range(3, 6):
                if self.is_valid_move(chess, j, i, x, y):
                    self.add_move(j, i, x, y, ply)

    def gen_elephant_move(self, chess: List[List[int]], i: int, j: int, ply: int):
        # 插入右下方的有效走法
        x, y = j + 2, i + 2
        if x < 9 and y < 10 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)
        # 插入右上方的有效走法
        x, y = j + 2, i - 2
        if x < 9 and y >= 0 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)
        # 插入左下方的有效走法
        x, y = j - 2, i + 2
        if x >= 0 and y < 10 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)
        # 插入左上方的有效走法
        x, y = j - 2, i - 2
        if x >= 0 and y >= 0 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)

    def gen_horse_move(self, chess: List[List[int]], i: int, j: int, ply: int):
        # 插入右下方的有效走法
        x, y = j + 2, i + 1
        if x < 9 and y < 10 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)
        # 插入右上方的有效走法
        x, y = j + 2, i - 1
        if x < 9 and y >= 0 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)
        # 插入左下方的有效走法
        x, y = j - 2, i + 1
        if x >= 0 and y < 10 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)
        # 插入左上方的有效走法
        x, y = j - 2, i - 1
        if x >= 0 and y >= 0 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)
        # 插入右下方的有效走法
        x, y = j + 1, i + 2
        if x < 9 and y < 10 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)
        # 插入左下方的有效走法
        x, y = j - 1, i + 2
        if x >= 0 and y < 10 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)
        # 插入右下方的有效走法
        x, y = j + 1, i - 2
        if x < 9 and y >= 0 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)
        # 插入左上方的有效走法
        x, y = j - 1, i - 2
        if x >= 0 and y >= 0 and self.is_valid_move(chess, j, i, x, y):
            self.add_move(j, i, x, y, ply)

    def gen_rpawn_move(self, chess: List[List[int]], i: int, j: int, ply: int):
        id = chess[i][j]
        y, x = i - 1, j
        if y > 0 and not self.same(id, chess[y][x]):
            self.add_move(j, i, x, y, ply)
        if i < 5:  # 是否已过河
            y, x = i, j + 1
            if x < 9 and not self.same(id, chess[y][x]):
                self.add_move(j, i, x, y, ply)
            x = j - 1
            if x >= 0 and self.same(id, chess[y][x]):
                self.add_move(j, i, x, y, ply)

    def gen_bpawn_move(self, chess: List[List[int]], i: int, j: int, ply: int):
        # 产生黑兵的合法走法
        id = chess[i][j]
        y, x = i + 1, j
        if y < 10 and not self.same(id, chess[y][x]):
            self.add_move(j, i, x, y, ply)
        if i > 4:
            y, x = i, j + 1
            if x < 9 and not self.same(id, chess[y][x]):
                self.add_move(j, i, x, y, ply)
            x = j - 1
            if x >= 0 and not self.same(id, chess[y][x]):
                self.add_move(j, i, x, y, ply)

    def gen_car_move(self, chess: List[List[int]], i: int, j: int, ply: int):
        id = chess[i][j]
        x, y = j + 1, i
        # 纵
        while x < 9:
            if chess[y][x] == Chessman.NOCHESS:
                self.add_move(j, i, x, y, ply)
            else:
                if not self.same(id, chess[y][x]):
                    self.add_move(j, i, x, y, ply)
                    break
            x += 1
        x, y = j - 1, i
        while x >= 0:
            if chess[y][x] == Chessman.NOCHESS:
                self.add_move(j, i, x, y, ply)
            else:
                if not self.same(id, chess[y][x]):
                    self.add_move(j, i, x, y, ply)
                    break
            x -= 1
        # 横
        x, y = j, i + 1
        while y < 10:
            if chess[y][x] == Chessman.NOCHESS:
                self.add_move(j, i, x, y, ply)
            else:
                if not self.same(id, chess[y][x]):
                    self.add_move(j, i, x, y, ply)
                    break
            y += 1
        x, y = j, i - 1
        while y >= 0:
            if chess[y][x] == Chessman.NOCHESS:
                self.add_move(j, i, x, y, ply)
            else:
                if not self.same(id, chess[y][x]):
                    self.add_move(j, i, x, y, ply)
                    break
            y -= 1

    def gen_cannon_move(self, chess: List[List[int]], i: int, j: int, ply: int):
        id = chess[i][j]
        x, y = j + 1, i
        flag = False
        # 右
        while x < 9:
            if chess[y][x] == Chessman.NOCHESS:
                if not flag:
                    self.add_move(j, i, x, y, ply)
            else:
                if not flag:
                    flag = True  # 遇到炮架
                else:
                    if not self.same(id, chess[y][x]):
                        self.add_move(j, i, x, y, ply)
                        break
            x += 1
        # 左
        x = j - 1
        flag = False
        while x >= 0:
            if chess[y][x] == Chessman.NOCHESS:
                if not flag:
                    self.add_move(j, i, x, y, ply)
            else:
                if not flag:
                    flag = True
                else:
                    if not self.same(id, chess[y][x]):
                        self.add_move(j, i, x, y, ply)
                        break
            x -= 1
        # 上
        x, y = j, i - 1
        flag = False
        while y >= 0:
            if chess[y][x] == Chessman.NOCHESS:
                if not flag:
                    self.add_move(j, i, x, y, ply)
            else:
                if not flag:
                    flag = True
                else:
                    if not self.same(id, chess[y][x]):
                        self.add_move(j, i, x, y, ply)
                        break
            y -= 1
        # 下
        x, y = j, i + 1
        flag = False
        while y < 10:
            if chess[y][x] == Chessman.NOCHESS:
                if not flag:
                    self.add_move(j, i, x, y, ply)
            else:
                if not flag:
                    flag = True
                else:
                    if not self.same(id, chess[y][x]):
                        self.add_move(j, i, x, y, ply)
                        break
            y += 1


class Evaluation:
    '''
    估值函数
    '''

    def __init__(self) -> None:
        self.base_value = [0] * 15  # 棋子基本价值
        self.flex_value = [0] * 15  # 存放棋子灵活性分数的数组
        self.attack_pos = [[0] * 9 for _ in range(10)]  # 每一个位置被威胁的信息
        self.guard_pos = [[0] * 9 for _ in range(10)]  # 每一位置被保护的信息
        self.flexibility_pos = [[0] * 9 for _ in range(10)]  # 每一位置的棋子的灵活性分数
        self.chess_value = [[0] * 9 for _ in range(10)]  # 每一位置上的棋子的总价值
        self.pos_cnt = 0  # 记录一棋子的相关位置个数
        self.relate_pos = [ChessmanPosition()] * 20  # 记录一个棋子相关位置的数组
        # 红卒的附加值矩阵
        self.BA0 = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [90, 90, 110, 120, 120, 120, 110, 90, 90],
            [90, 90, 110, 120, 120, 120, 110, 90, 90],
            [70, 90, 110, 110, 110, 110, 110, 90, 70],
            [70, 70, 70, 70, 70, 70, 70, 70, 70],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        # 黑兵的附加值矩阵
        self.BA1 = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [70, 70, 70, 70, 70, 70, 70, 70, 70],
            [70, 90, 110, 110, 110, 110, 110, 90, 70],
            [90, 90, 110, 120, 120, 120, 110, 90, 90],
            [90, 90, 110, 120, 120, 120, 110, 90, 90],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        # 定义每一种棋子的基本价值
        self.BASEVALUE_PAWN = 100
        self.BASEVALUE_BISHOP = 250
        self.BASEVALUE_ELEPHANT = 250
        self.BASEVALUE_CAR = 500
        self.BASEVALUE_HORSE = 350
        self.BASEVALUE_CANNON = 350
        self.BASEVALUE_KING = 10000
        # 定义棋子的灵活性
        self.FLEXIBILITY_PAWN = 15
        self.FLEXIBILITY_BISHOP = 1
        self.FLEXIBILITY_ELEPHANAT = 1
        self.FLEXIBILITY_CAR = 6
        self.FLEXIBILITY_HORSE = 12
        self.FLEXIBILITY_CANNON = 6
        self.FLEXIBILITY_KING = 0
        # 初始化
        self.init()
        # 叶子节点的次数
        self.leaf_cnt = 0

    def init(self):
        self.base_value[Chessman.B_KING] = self.BASEVALUE_KING
        self.base_value[Chessman.B_CAR] = self.BASEVALUE_CAR
        self.base_value[Chessman.B_HORSE] = self.BASEVALUE_HORSE
        self.base_value[Chessman.B_BISHOP] = self.BASEVALUE_BISHOP
        self.base_value[Chessman.B_ELEPHANT] = self.BASEVALUE_ELEPHANT
        self.base_value[Chessman.B_CANNON] = self.BASEVALUE_CANNON
        self.base_value[Chessman.B_PAWN] = self.BASEVALUE_PAWN
        self.base_value[Chessman.R_KING] = self.BASEVALUE_KING
        self.base_value[Chessman.R_CAR] = self.BASEVALUE_CAR
        self.base_value[Chessman.R_HORSE] = self.BASEVALUE_HORSE
        self.base_value[Chessman.R_BISHOP] = self.BASEVALUE_BISHOP
        self.base_value[Chessman.R_ELEPHANT] = self.BASEVALUE_ELEPHANT
        self.base_value[Chessman.R_CANNON] = self.BASEVALUE_CANNON
        self.base_value[Chessman.R_PAWN] = self.BASEVALUE_PAWN
        # 初始化灵活性价值数组
        self.flex_value[Chessman.B_KING] = self.FLEXIBILITY_KING
        self.flex_value[Chessman.B_CAR] = self.FLEXIBILITY_CAR
        self.flex_value[Chessman.B_HORSE] = self.FLEXIBILITY_HORSE
        self.flex_value[Chessman.B_BISHOP] = self.FLEXIBILITY_BISHOP
        self.flex_value[Chessman.B_ELEPHANT] = self.FLEXIBILITY_ELEPHANAT
        self.flex_value[Chessman.B_CANNON] = self.FLEXIBILITY_CANNON
        self.flex_value[Chessman.B_PAWN] = self.FLEXIBILITY_PAWN
        self.flex_value[Chessman.R_KING] = self.FLEXIBILITY_KING
        self.flex_value[Chessman.R_CAR] = self.FLEXIBILITY_CAR
        self.flex_value[Chessman.R_HORSE] = self.FLEXIBILITY_HORSE
        self.flex_value[Chessman.R_BISHOP] = self.FLEXIBILITY_BISHOP
        self.flex_value[Chessman.R_ELEPHANT] = self.FLEXIBILITY_ELEPHANAT
        self.flex_value[Chessman.R_CANNON] = self.FLEXIBILITY_CANNON
        self.flex_value[Chessman.R_PAWN] = self.FLEXIBILITY_PAWN

    def reset(self):
        for i in range(10):
            for j in range(9):
                self.attack_pos[i][j] = 0
                self.guard_pos[i][j] = 0
                self.flexibility_pos[i][j] = 0
                self.chess_value[i][j] = 0

    def get_bing_value(self, x, y, chess):
        # 如果是红兵返回其位置附加价值
        if chess[y][x] == Chessman.R_PAWN:
            return self.BA0[y][x]
        # 如果是黑兵返回其位置附加价值
        if chess[y][x] == Chessman.B_PAWN:
            return self.BA1[y][x]
        return 0

    def same(self, chess1, chess2):
        '''
        判断两个棋子是否同色
        :param chess1:
        :param chess2:
        :return:
        '''
        return (1 <= chess1 <= 7 and 1 <= chess2 <= 7) \
               or (8 <= chess1 <= 14 and 8 <= chess2 <= 14)

    def is_red(self, id):
        return 8 <= id <= 14

    def is_black(self, id):
        return 1 <= id <= 7

    def evaluate(self, chess: List[List[int]], is_red: bool) -> int:
        '''
        棋子评估函数
        :param chess: 棋盘
        :param is_red: 是否轮到红子
        :return:
        '''
        pass
        # 每调一次估值函数就统计一次(只有叶子节点才会调估值函数)
        self.leaf_cnt += 1
        self.reset()  # 重置中间状态值
        chess_type, target_type = None, None
        for i in range(10):
            for j in range(9):
                if chess[i][j] != Chessman.NOCHESS:
                    chess_type = chess[i][j]  # 获取棋子类型
                    self.get_relate_piece(chess, j, i)  # 找出该棋子所有相关位置
                    for k in range(self.pos_cnt):
                        target_type = chess[self.relate_pos[k].y][self.relate_pos[k].x]
                        if target_type == Chessman.NOCHESS:
                            self.flexibility_pos[i][j] += 1
                        else:
                            if self.same(chess_type, target_type):  # 如果是己方棋子, 则保护
                                self.guard_pos[self.relate_pos[k].y][self.relate_pos[k].x] += 1
                            else:  # 敌方棋子, 开始威胁
                                self.attack_pos[self.relate_pos[k].y][self.relate_pos[k].x] += 1
                                self.flexibility_pos[i][j] += 1  # 灵活性增加
                                if target_type == Chessman.R_KING:
                                    if not is_red:
                                        return 18888
                                elif target_type == Chessman.B_KING:
                                    if is_red:
                                        return 18888
                                else:
                                    self.attack_pos[self.relate_pos[k].y][self.relate_pos[k].x] \
                                        += (30 + (
                                            self.base_value[target_type] - self.base_value[chess_type]) // 10) // 10
        for i in range(10):
            for j in range(9):
                if chess[i][j] != Chessman.NOCHESS:
                    chess_type = chess[i][j]
                    self.chess_value[i][j] += 1
                    self.chess_value[i][j] += self.flex_value[chess_type] * self.flexibility_pos[i][j]
                    self.chess_value[i][j] += self.get_bing_value(j, i, chess)
        half_value = 0
        for i in range(10):
            for j in range(9):
                if chess[i][j] != Chessman.NOCHESS:
                    chess_type = chess[i][j]
                    half_value = self.base_value[chess_type] // 16
                    self.chess_value[i][j] += self.base_value[chess_type]
                    if self.is_red(chess_type):
                        if self.attack_pos[i][j]:  # 如果当前红棋被危险
                            if is_red:
                                if chess_type == Chessman.R_KING:
                                    self.chess_value[i][j] -= 20
                                else:
                                    self.chess_value[i][j] -= half_value * 2
                                    if self.guard_pos[i][j]:
                                        self.chess_value[i][j] += half_value
                            else:
                                if chess_type == Chessman.R_KING:
                                    return 18888
                                self.chess_value[i][j] -= half_value * 10
                                if self.guard_pos[i][j]:
                                    self.chess_value[i][j] += half_value * 9
                            self.chess_value[i][j] -= self.attack_pos[i][j]
                        else:  # 没受威胁
                            if self.guard_pos[i][j]:
                                self.chess_value[i][j] += 5
                    else:
                        if self.attack_pos[i][j]:
                            if not is_red:
                                if chess_type == Chessman.B_KING:
                                    self.chess_value[i][j] -= 20
                                else:
                                    self.chess_value[i][j] -= half_value * 2
                                    if self.guard_pos[i][j]:
                                        self.chess_value[i][j] += half_value
                            else:
                                if chess_type == Chessman.B_KING:
                                    return 18888
                                self.chess_value[i][j] -= half_value * 10
                                if self.guard_pos[i][j]:
                                    self.chess_value[i][j] += half_value * 9
                            self.chess_value[i][j] -= self.attack_pos[i][j]
                        else:
                            if self.guard_pos[i][j]:
                                self.chess_value[i][j] += 5
        # 开始统计每一个棋子的总价值
        red_value, black_value = 0, 0
        for i in range(10):
            for j in range(9):
                chess_type = chess[i][j]
                if chess_type != Chessman.NOCHESS:
                    if self.is_red(chess_type):
                        red_value += self.chess_value[i][j]
                    else:
                        black_value += self.chess_value[i][j]
        if is_red:
            return red_value - black_value
        return black_value - red_value

    def add_point(self, x, y):
        self.relate_pos[self.pos_cnt].x = x
        self.relate_pos[self.pos_cnt].y = y
        self.pos_cnt += 1

    def get_relate_piece(self, chess: List[List[int]], j: int, i: int):
        self.pos_cnt = 0
        id = chess[i][j]
        if id == Chessman.R_KING or id == Chessman.B_KING:
            for y in range(3):
                for x in range(3, 6):
                    if self.can_touch(chess, j, i, x, y):
                        self.add_point(x, y)
            for y in range(7, 10):
                for x in range(3, 6):
                    if self.can_touch(chess, j, i, x, y):
                        self.add_point(x, y)
        elif id == Chessman.R_BISHOP:
            for y in range(7, 10):
                for x in range(3, 6):
                    if self.can_touch(chess, j, i, x, y):
                        self.add_point(x, y)
        elif id == Chessman.R_ELEPHANT or id == Chessman.B_ELEPHANT:
            x, y = j + 2, i + 2
            if x < 9 and y < 10 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
            x, y = j + 2, i - 2
            if x < 9 and y >= 0 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
            x, y = j - 2, i + 2
            if x >= 0 and y < 10 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
            x, y = j - 2, i - 2
            if x >= 0 and y >= 0 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
        elif id == Chessman.R_HORSE or id == Chessman.B_HORSE:
            x, y = j + 2, i + 1
            if x < 9 and y < 10 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
            x, y = j + 2, i - 1
            if x < 9 and y >= 0 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
            x, y = j - 2, i + 1
            if x >= 0 and y < 10 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
            x, y = j - 2, i - 1
            if x >= 0 and y >= 0 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
            x, y = j + 1, i + 2
            if x < 9 and y < 10 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
            x, y = j - 1, i + 2
            if x >= 0 and y < 10 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
            x, y = j + 1, i - 2
            if x < 9 and y >= 0 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
            x, y = j - 1, i - 2
            if x >= 0 and y >= 0 and self.can_touch(chess, j, i, x, y):
                self.add_point(x, y)
        elif id == Chessman.R_CAR or id == Chessman.B_CAR:
            x, y = j + 1, i
            while x < 9:
                if chess[y][x] == Chessman.NOCHESS:
                    self.add_point(x, y)
                else:
                    self.add_point(x, y)
                x += 1
            x, y = j - 1, i
            while x >= 0:
                if chess[y][x] == Chessman.NOCHESS:
                    self.add_point(x, y)
                else:
                    self.add_point(x, y)
                    break
                x -= 1
            x, y = j, i + 1
            while y < 10:
                if chess[y][x] == Chessman.NOCHESS:
                    self.add_point(x, y)
                else:
                    self.add_point(x, y)
                    break
                y += 1
            x, y = j, i - 1
            while y >= 0:
                if chess[y][x] == Chessman.NOCHESS:
                    self.add_point(x, y)
                else:
                    self.add_point(x, y)
                    break
                y -= 1
        elif id == Chessman.R_PAWN:
            y, x = i - 1, j
            if y >= 0:
                self.add_point(x, y)
            if i < 5:
                y, x = i, j + 1
                if x < 9:
                    self.add_point(x, y)
                x = j - 1
                if x >= 0:
                    self.add_point(x, y)
        elif id == Chessman.B_PAWN:
            y, x = i + 1, j
            if y < 10:
                self.add_point(x, y)
            if i > 4:
                y, x = i, j + 1
                if x < 9:
                    self.add_point(x, y)
                x = j - 1
                if x >= 0:
                    self.add_point(x, y)
        elif id == Chessman.B_CANNON or id == Chessman.R_CANNON:
            x, y = j + 1, i
            flag = False
            while x < 9:
                if chess[y][x] == Chessman.NOCHESS:
                    if not flag:
                        self.add_point(x, y)
                else:
                    if not flag:
                        flag = True
                    else:
                        self.add_point(x, y)
                        break
                x += 1
            x = j - 1
            flag = False
            while x >= 0:
                if chess[y][x] == Chessman.NOCHESS:
                    if not flag:
                        self.add_point(x, y)
                else:
                    if not flag:
                        flag = True
                    else:
                        self.add_point(x, y)
                        break
                x -= 1
            x, y = j, i + 1
            flag = False
            while y < 10:
                if chess[y][x] == Chessman.NOCHESS:
                    if not flag:
                        self.add_point(x, y)
                else:
                    if not flag:
                        flag = True
                    else:
                        self.add_point(x, y)
                        break
                y += 1
            y = i - 1
            flag = False
            while y >= 0:
                if chess[y][x] == Chessman.NOCHESS:
                    if not flag:
                        self.add_point(x, y)
                else:
                    if not flag:
                        flag = True
                    else:
                        self.add_point(x, y)
                        break
                y -= 1
        return self.pos_cnt

    def can_touch(self, chess: List[List[int]], from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        if from_y == to_y and from_x == to_x:
            return False
        move_id = chess[from_y][from_x]
        target_id = chess[to_y][to_x]
        if move_id == Chessman.B_KING:
            if target_id == Chessman.R_KING:
                if from_x != to_x:
                    return False
                for i in range(from_y + 1, to_y):
                    if chess[i][from_x] != Chessman.NOCHESS:
                        return False
            else:
                if to_y > 2 or to_x > 5 or to_x < 3:
                    return False
                if abs(from_y - to_y) + abs(to_x - from_x) > 1:
                    return False
        elif move_id == Chessman.R_BISHOP:
            if to_y < 7 or to_x > 5 or to_x < 3:
                return False
            if abs(from_y - to_y) != 2 or abs(to_x - from_x) != 1:
                return False
        elif move_id == Chessman.B_BISHOP:
            if to_y > 2 or to_x > 5 or to_x < 3:
                return False
            if abs(from_y - to_y) != 1 or abs(to_x - from_x) != 1:
                return False
        elif move_id == Chessman.R_ELEPHANT:
            if to_y < 5:
                return False
            if abs(from_x - to_x) != 2 or abs(from_y - to_y) != 2:
                return False
            if chess[(from_y + to_y) // 2][(from_x + to_x) // 2] != Chessman.NOCHESS:
                return False
        elif move_id == Chessman.B_ELEPHANT:
            if to_y > 4:
                return False
            if abs(from_x - to_x) != 2 or abs(from_y - to_y) != 2:
                return False
            if chess[(from_y + to_y) // 2][(from_x + to_x) // 2] != Chessman.NOCHESS:
                return False
        elif move_id == Chessman.B_PAWN:
            if to_y < from_y:
                return False
            if from_y < 5 and from_y == to_y:
                return False
            if to_y - from_y + abs(to_x - from_x) > 1:
                return False
        elif move_id == Chessman.R_PAWN:
            if to_y > from_y:
                return False
            if from_y > 4 and from_y == to_y:
                return False
            if from_y - to_y + abs(to_x - from_x) > 1:
                return False
        elif move_id == Chessman.R_KING:
            if target_id == Chessman.B_KING:
                if from_x != to_x:
                    return False
                for i in range(from_y - 1, to_y):
                    if chess[i][from_x] != Chessman.NOCHESS:
                        return False
            else:
                if to_y < 7 or to_x > 5 or to_x < 3:
                    return False
                if abs(from_y - to_y) + abs(to_x - from_x) > 1:
                    return False
        elif move_id == Chessman.B_CAR or move_id == Chessman.R_CAR:
            if from_y != to_y and from_x != to_x:
                return False
            if from_y == to_y:
                if from_x < to_x:
                    for i in range(from_x + 1, to_x):
                        if chess[from_y][i] != Chessman.NOCHESS:
                            return False
                else:
                    for i in range(to_x + 1, from_x):
                        if chess[from_y][i] != Chessman.NOCHESS:
                            return False
            else:
                if from_y < to_y:
                    for j in range(from_y + 1, to_y):
                        if chess[j][from_x] != Chessman.NOCHESS:
                            return False
                else:
                    for j in range(to_y + 1, from_y):
                        if chess[j][from_x] != Chessman.NOCHESS:
                            return False
        elif move_id == Chessman.B_HORSE or move_id == Chessman.R_HORSE:
            if not ((abs(to_x - from_x) == 1 and abs(to_y - from_y) == 2)
                    or (abs(to_x - from_x) == 2 and abs(to_y - from_y) == 1)):
                return False
            if to_x - from_x == 2:
                i, j = from_x + 1, from_y
            elif from_x - to_x == 2:
                i, j = from_x - 1, from_y
            elif to_y - from_y == 2:
                i, j = from_x, from_y + 1
            elif from_y - to_y == 2:
                i, j = from_x, from_y - 1
            if chess[j][i] != Chessman.NOCHESS:
                return False
        elif move_id == Chessman.B_CANNON or move_id == Chessman.R_CANNON:
            if from_y != to_y and from_x != to_x:
                return False
            if chess[to_y][to_x] == Chessman.NOCHESS:
                if from_y == to_y:
                    if from_x < to_x:
                        for i in range(from_x + 1, to_x):
                            if chess[from_y][i] != Chessman.NOCHESS:
                                return False
                    else:
                        for i in range(to_x + 1, from_x):
                            if chess[from_y][i] != Chessman.NOCHESS:
                                return False
                else:
                    if from_y < to_y:
                        for j in range(from_y + 1, to_y):
                            if chess[j][from_x] != Chessman.NOCHESS:
                                return False
                    else:
                        for j in range(to_y, from_y):
                            if chess[j][from_x] != Chessman.NOCHESS:
                                return False
            else:
                cnt = 0
                if from_y == to_y:
                    if from_x < to_x:
                        for i in range(from_x + 1, to_x):
                            if chess[from_y][i] != Chessman.NOCHESS:
                                cnt += 1
                            if cnt != 1:
                                return False
                    else:
                        for i in range(to_x + 1, from_x):
                            if chess[from_y][i] != Chessman.NOCHESS:
                                cnt += 1
                            if cnt != 1:
                                return False
                else:
                    if from_y < to_y:
                        for j in range(from_y + 1, to_y):
                            if chess[j][from_x] != Chessman.NOCHESS:
                                cnt += 1
                            if cnt != 1:
                                return False
                    else:
                        for j in range(to_y + 1, from_y):
                            if chess[j][from_x] != Chessman.NOCHESS:
                                cnt += 1
                            if cnt != 1:
                                return False
        return True


class SearchEngine:
    '''
    搜索引擎
    '''

    def __init__(self) -> None:
        self.move_generator = MoveGenerator()
        self.evaluation = Evaluation()
        self.search_depth = 0  # 搜索深度
        self.max_depth = 0  # 最大深度
        self.chess = [[0] * 9 for _ in range(10)]

    def make_move(self, move):
        id = self.chess[move.to.y][move.to.x]
        # 移动棋子
        self.chess[move.to.y][move.to.x] = self.chess[move.fron.y][move.fron.x]
        # 清空原来的位置
        self.chess[move.fron.y][move.fron.x] = Chessman.NOCHESS
        return id

    def un_make_move(self, move, chess_id):
        # 还原
        self.chess[move.fron.y][move.fron.x] = self.chess[move.to.y][move.to.x]
        # 恢复目标位置的棋子
        self.chess[move.to.y][move.to.x] = chess_id

    def is_game_over(self, chess, depth):
        '''
        判断游戏是否已经结束, 将在不在
        :param position:
        :param depth:
        :return:
        '''
        red_live, black_live = False, False
        for i in range(7, 10):
            for j in range(3, 6):
                if chess[i][j] == Chessman.B_KING:
                    black_live = True
                if chess[i][j] == Chessman.R_KING:
                    red_live = True
        for i in range(3):
            for j in range(3, 6):
                if chess[i][j] == Chessman.B_KING:
                    black_live = True
                if chess[i][j] == Chessman.R_KING:
                    red_live = True
        i = (self.max_depth - depth + 1) % 2
        if not red_live:
            if i:
                return 19990 + depth
            else:
                return -19990 - depth
        if not black_live:
            if i:
                return -19990 - depth
            else:
                return 19990 + depth
        return 0


class NegamaxEngine(SearchEngine):

    def __init__(self, search_depth) -> None:
        super().__init__()
        self.best_move = None
        self.search_depth = search_depth  # 设定搜索深度

    def copy(self, chess1, chess2):
        for i in range(10):
            for j in range(9):
                chess2[i][j] = chess1[i][j]

    def search_a_good_move(self, chess):
        # 设定搜索层数
        self.max_depth = self.search_depth
        # 将传入的棋盘复制到成员变量中
        self.copy(chess, self.chess)
        # 调用极大值搜索函数找最佳走法
        self.nega_max(self.max_depth)
        # 修改棋盘的走法
        # self.make_move(self.best_move)
        # 将修改过的棋盘复制到传入的棋盘中
        self.copy(self.chess, chess)
        return [self.best_move.fron.y,
                self.best_move.fron.x,
                self.best_move.to.y,
                self.best_move.to.x]

    def nega_max(self, depth):
        current = -20000
        i = self.is_game_over(self.chess, depth)
        if i:
            return i  # 棋局结束
        if depth <= 0:
            return self.evaluation.evaluate(self.chess,
                                            (self.max_depth - depth) % 2)
        cnt = self.move_generator.create_possible_move(self.chess, depth,
                                                       (self.max_depth - depth) % 2)
        for i in range(cnt):
            type = self.make_move(self.move_generator.move_list[depth][i])
            score = -self.nega_max(depth - 1)
            self.un_make_move(self.move_generator.move_list[depth][i], type)
            if score > current:
                current = score
                if depth == self.max_depth:
                    self.best_move = self.move_generator.move_list[depth][i]
        return current

