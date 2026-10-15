import random


def Generate_y_start(n, p):
    """
    :param n: мощность множества I
    :param p: количество открываемых предприятий (медиана)
    :return: стартовое размещение
    """
    y_start = [0 for _ in range(n)]
    for i in random.sample(range(n), p):
        y_start[i] = 1
    return y_start


def Swap(y):
    """
    :param y: вектор размещения
    :return: окрестность 1-swap
    """
    indx_1 = [i for i, v in enumerate(y) if v == 1]
    indx_0 = [i for i, v in enumerate(y) if v == 0]

    swap = []
    for i in indx_1:
        for j in indx_0:
            vector = y.copy()
            vector[i] = 0
            vector[j] = 1
            swap.append(vector)
    return swap


def Pairs(array):
    """
    :param array: массив
    :return: массив различных пар из элементов данного массива
    """
    n = len(array)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((array[i], array[j]))
    return pairs


def Swap_2(y):
    """
    :param y: размещение
    :return: окрестность 2-swap
    """
    indx_1 = [i for i, v in enumerate(y) if v == 1]
    indx_0 = [i for i, v in enumerate(y) if v == 0]

    p_1 = Pairs(indx_1)
    p_0 = Pairs(indx_0)

    swap_2 = []
    for i in p_1:
        for j in p_0:
            vector = y.copy()
            vector[j[0]] = 1
            vector[j[1]] = 1
            vector[i[0]] = 0
            vector[i[1]] = 0
            swap_2.append(vector)
    return swap_2
