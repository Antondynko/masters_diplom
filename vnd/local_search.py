from vnd.follower import Folower
from vnd.neighborhoods import Swap, Swap_2
from vnd.leader import Leader, Leader_simplified


def N(y, d, c, V, leader_fn=Leader):
    """
    Выбрать лучшего соседа 1-swap (first-improvement).
    :param y: стартовое размещение
    :param d: матрица предпочтений
    :param c: матрица затрат
    :param V: порог
    :param leader_fn: функция Leader
    :return: сосед с улучшением или y
    """
    swap = Swap(y)
    _, delta_rho = leader_fn(Folower(y, d), c, V)

    for v in swap:
        _, g = leader_fn(Folower(v, d), c, V)
        if g > delta_rho:
            return v
    return y


def Local_Search(y, d, c, V, leader_fn=Leader, max_iter=100, verbose=True):
    """
    Процедура локального спуска.
    :param y: размещение, от которого стартует спуск
    :param d: матрица предпочтений
    :param c: матрица затрат
    :param V: порог
    :param leader_fn: функция Leader
    :param max_iter: ограничение итераций
    :param verbose: печатать предупреждения
    :return: локальный оптимум
    """
    k = 0
    result = [0 for _ in range(len(y))]
    while True:
        k += 1
        _, delta_rho = leader_fn(Folower(y, d), c, V)
        vector = N(y, d, c, V, leader_fn)
        _, f = leader_fn(Folower(vector, d), c, V)
        if f <= delta_rho:
            result = vector
            break
        else:
            y = vector
        if k > max_iter:
            if verbose:
                print("Сработал ограничитель")
            break
    return result


def Improve(y, d, c, V, leader_fn=Leader, verbose=True):
    """
    Процедура последовательного просмотра окрестности 2-swap после локального спуска.
    :param y: размещение
    :param d: матрица предпочтений
    :param c: матрица затрат
    :param V: порог
    :param leader_fn: функция Leader
    :param verbose: печатать статус
    :return: улучшенное решение или y
    """
    swap_2 = Swap_2(y)
    _, rho = leader_fn(Folower(y, d), c, V)

    for v in swap_2:
        _, rho_new = leader_fn(Folower(v, d), c, V)
        if rho_new > rho:
            if verbose:
                print("Improvement happened")
            return v
    if verbose:
        print("No improvement")
    return y
