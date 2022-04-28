'''
    alpha-beta剪枝
'''


def evaluate(chess, is_max):
    '''
    棋盘估值函数
    :param chess:
    :return:
    '''
    return 0


def next(chess):
    '''
    下一步棋子
    :param chess:
    :return:
    '''
    return chess


def chess_generator(chess):
    yield chess


def alphabeta(chess, depth, is_max, alpha, beta):
    '''
        alpha-beta剪枝的具体实现算法, 只看树的局部就可以理解
        alpha和beta是继承自父亲, 需要寻找到子节点中 > alpha 和 < beta的元素
    :param chess: 棋盘
    :param depth: 深度
    :param is_max: 是否求最大
    :param alpha:
    :param beta:
    :return:
    '''
    if depth <= 0:  # 叶子节点
        return evaluate(chess, is_max)
    gen = chess_generator(chess)  # 棋盘生成器
    if is_max:  # 求最大
        for n_chess in next(gen):
            score = alphabeta(n_chess, depth-1, False, alpha, beta)
            if score > alpha:  # 当前节点求最大 max(score, alpha)
                alpha = score
                if alpha >= beta:  # 如果当前节点的alpha >= beta, 那么说明后面的子节点都没有意义了
                    return beta
        return alpha
    else:  # 求最小
        for n_chess in next(gen):
            score = alphabeta(n_chess, depth-1, True, alpha, beta)
            if score < beta:
                beta = score
                if beta <= alpha:
                    return alpha
        return beta


def alphabeta_v2(chess, depth, is_max, alpha, beta):
    '''
    使用负最大化算法改进的alphabeta算法
    :param chess:
    :param depth:
    :param alpha:
    :param beta:
    :return:
    '''
    if depth < 0:
        return evaluate(chess, is_max)
    gen = chess_generator(chess)
    for n_chess in next(gen):
        score = -alphabeta_v2(n_chess, depth-1, not is_max, -beta, -alpha)
        if score >= alpha:
            alpha = score
        if alpha >= beta:
            break
    return alpha
