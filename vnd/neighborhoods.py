import random


def generate_y_start(n, p, rng=None):
    """
    :param n: мощность множества I
    :param p: количество открываемых предприятий (медиана)
    :param rng: необязательный random.Random - для воспроизводимых стартов (по умолчанию глобальный random)
    :return: стартовое размещение
    """
    rng = random if rng is None else rng
    y_start = [0 for _ in range(n)]
    for i in rng.sample(range(n), p):
        y_start[i] = 1
    return y_start


def swap(y):
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


def pairs(array):
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


def swap_2(y):
    """
    :param y: размещение
    :return: окрестность 2-swap
    """
    indx_1 = [i for i, v in enumerate(y) if v == 1]
    indx_0 = [i for i, v in enumerate(y) if v == 0]

    p_1 = pairs(indx_1)
    p_0 = pairs(indx_0)

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
