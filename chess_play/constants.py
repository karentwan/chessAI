'''
    常量
'''


class Chessman:
    '''
    棋子常量
    '''
    NOCHESS = 0  # 没有棋子
    B_KING = 1  # 黑将
    B_CAR = 2  # 黑车
    B_HORSE = 3  # 黑马
    B_CANNON = 4  # 黑炮
    B_BISHOP = 5  # 黑仕
    B_ELEPHANT = 6  # 黑象
    B_PAWN = 7  # 黑卒
    R_KING = 8  # 红帅
    R_CAR = 9  # 红车
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
    WIN_WIDTH = 188
    WIN_HEIGHT = 91
    LOSS_WIDTH = 389
    LOSS_HEIGHT = 101
    CHESS_WIDTH = 640
    CHESS_HEIGHT = 720


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
